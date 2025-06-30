import sys
import os
import json
import subprocess
import atexit
import shutil
import tempfile
import platform
import time
import logging
import configparser
from pathlib import Path
from PyQt6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGroupBox,QRadioButton,QCheckBox,QLabel,QPushButton,QFrame,QComboBox,QGridLayout,QDialog,QMessageBox,QInputDialog,QButtonGroup,QColorDialog,QSizePolicy,QFormLayout)
from PyQt6.QtCore import (Qt, QUrl, QTimer, QThread, pyqtSignal)
from PyQt6.QtGui import (QIcon, QDesktopServices, QColor, QPixmap, QPalette)
import urllib.request
import re

logger = None


def setup_logger(log_path, log_level="ERROR"):
    global logger
    logger = logging.getLogger("Mica4U")
    level = getattr(logging, log_level.upper(), logging.ERROR)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def cleanup_temp():
    temp_dir = tempfile.gettempdir()
    now = time.time()
    try:
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if filename.startswith("_MEI") and os.path.isdir(filepath):
                if now - os.path.getmtime(filepath) > 86400:
                    shutil.rmtree(filepath, ignore_errors=True)
                    log_info(f"Removed temp directory: {filepath}")
            elif (
                filename.endswith(".tmp") or filename.endswith(".log")
            ) and os.path.isfile(filepath):
                if now - os.path.getmtime(filepath) > 86400:
                    try:
                        os.remove(filepath)
                        log_info(f"Removed temp file: {filepath}")
                    except Exception as e:
                        log_warning(f"Failed to remove temp file {filepath}: {e}")
    except Exception as e:
        log_error(f"Failed to clean up temp directories: {str(e)}")


def gwv():
    ver = platform.version().split(".")
    version_tuple = (int(ver[0]), int(ver[1]), int(ver[2]))
    return version_tuple


def get_icon_color():
    app = QApplication.instance()
    if not app:
        return "black"
    palette = app.palette()
    window_color = palette.color(QPalette.ColorRole.Window)
    return "black" if window_color.lightness() > 128 else "white"


def get_icon(icon_name, color=None):
    if not hasattr(get_icon, "_icon_cache"):
        get_icon._icon_cache = {}
    if color is None:
        color = get_icon_color()
    cache_key = f"{icon_name}:{color}"
    if cache_key in get_icon._icon_cache:
        return get_icon._icon_cache[cache_key]
    icon_path = Path(__file__).parent / "assets" / "icons" / f"{icon_name}.svg"
    if not icon_path.exists():
        icon = QIcon()
        get_icon._icon_cache[cache_key] = icon
        return icon
    with open(icon_path, "r", encoding="utf-8") as f:
        svg_content = f.read().replace("{color}", color)
    pixmap = QPixmap()
    pixmap.loadFromData(svg_content.encode("utf-8"), "SVG")
    icon = QIcon()
    icon.addPixmap(pixmap)
    get_icon._icon_cache[cache_key] = icon
    return icon


def check_dll_registered(config):
    try:
        dll_name = os.path.basename(config.get_dll_path()).lower()
        result = subprocess.run(
            f'tasklist /M /FI "IMAGENAME eq explorer.exe" /FO CSV /NH',
            capture_output=True,
            text=True,
            shell=True,
        )
        found = dll_name in result.stdout.lower()
        log_info(f"Checked DLL registration: {dll_name} found={found}")
        return found
    except Exception as e:
        log_error(f"Error checking DLL status: {str(e)}")
        return False


def get_rgba_from_config(config, section="light"):
    r = int(config.get_value(section, "r"))
    g = int(config.get_value(section, "g"))
    b = int(config.get_value(section, "b"))
    a = int(config.get_value(section, "a"))
    return r, g, b, a


VERSION = "1.7.1"
STANDARD_HEIGHT = 30
STANDARD_SPACING = 2


def create_icon_button(text="", icon=None, tooltip=None, callback=None, min_width=None, icon_only=False, object_name=None):
    btn = QPushButton(text if not icon_only else "")
    btn.setFixedHeight(STANDARD_HEIGHT)
    if min_width:
        btn.setMinimumWidth(min_width)
    elif icon_only:
        btn.setFixedWidth(STANDARD_HEIGHT)
    if icon:
        btn.setIcon(get_icon(icon))
    if tooltip:
        btn.setToolTip(tooltip)
    if object_name:
        btn.setObjectName(object_name)
    if icon_only:
        btn.setProperty("iconOnly", "true")
    if callback:
        btn.clicked.connect(callback)
    return btn


def log_info(msg):
    if logger:
        logger.info(msg)


def log_warning(msg):
    if logger:
        logger.warning(msg)


def log_error(msg):
    if logger:
        logger.error(msg)


class ConfigManager:
    def __init__(self):
        if getattr(sys, "frozen", False):
            self.base_path = Path(sys.executable).parent
        else:
            self.base_path = Path(__file__).parent
        self.portable_mode = (self.base_path / "portable.ini").exists()
        if self.portable_mode:
            self.config_dir = self.base_path
        else:
            self.config_dir = self._setup_appdata_dir("Mica4U")
        self.dll_path = self.config_dir / "ExplorerBlurMica.dll"
        self.config_path = self.config_dir / "config.ini"
        self.log_path = self.config_dir / "Mica4U.log"
        self.defaults = {
            "config": {
                "effect": "1",
                "clearAddress": "true",
                "clearBarBg": "true",
                "clearWinUIBg": "true",
                "showLine": "false",
            },
            "light": {"r": "255", "g": "255", "b": "255", "a": "120"},
            "dark": {"r": "255", "g": "255", "b": "255", "a": "120"},
            "gui": {
                "showUnsupportedEffects": "false",
                "last_preset": "Light Mode",
                "showUnsupportedOptions": "false",
                "logLevel": "ERROR",
                "checkForUpdates": "true",
            },
        }
        self.presets = {
            "Light Mode": {"r": "220", "g": "220", "b": "220", "a": "160"},
            "Dark Mode": {"r": "0", "g": "0", "b": "0", "a": "120"},
        }
        self._initializing = True
        self._save_timer = None
        self.config_parser = configparser.ConfigParser()
        self._load_config()
        self._initializing = False
        preset = self.get_value("gui", "last_preset", fallback=None)
        if preset and preset in self.presets:
            self.load_preset(preset)

    def _setup_appdata_dir(self, dir_name):
        path = Path(os.getenv("APPDATA", "")) / dir_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _create_default_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(
                """[config]
effect = 1
clearAddress = true
clearBarBg = true
clearWinUIBg = true
showLine = false

[light]
r = 255
g = 255
b = 255
a = 120

[dark]
r = 255
g = 255
b = 255
a = 120

[gui]
showUnsupportedEffects = false
last_preset = Light Mode
showUnsupportedOptions = false
logLevel = ERROR
checkForUpdates = true

[presets]
Light Mode = {\"r\": \"220\", \"g\": \"220\", \"b\": \"220\", \"a\": \"160\"}
Dark Mode = {\"r\": \"0\", \"g\": \"0\", \"b\": \"0\", \"a\": \"120\"}"""
            )

    def _load_config(self):
        if not self.config_path.exists():
            self._create_default_config()
            log_info("Created default config file.")
        self.config_parser.read(self.config_path, encoding="utf-8")
        if self.config_parser.has_section("presets"):
            for name in list(self.config_parser["presets"]):
                try:
                    norm_name = name.title()
                    self.presets[norm_name] = json.loads(
                        self.config_parser["presets"][name]
                    )
                except Exception as e:
                    log_warning(f"Failed to load preset {name}: {e}")

    def save_config(self):
        for section, keys in self.defaults.items():
            if not self.config_parser.has_section(section):
                self.config_parser.add_section(section)
            for key in keys:
                if self.config_parser.has_option(section, key):
                    value = self.config_parser.get(section, key)
                else:
                    value = self.defaults[section][key]
                self.config_parser.set(section, key, str(value))
        if not self.config_parser.has_section("presets"):
            self.config_parser.add_section("presets")
        for name in list(self.config_parser["presets"]):
            self.config_parser.remove_option("presets", name)
        for name, data in self.presets.items():
            self.config_parser.set("presets", name.title(), json.dumps(data))
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config_parser.write(f)
        log_info("Configuration saved.")

    def get_value(self, section, key, default=None, fallback=None):
        if self.config_parser.has_option(section, key):
            return self.config_parser.get(section, key)
        if fallback is not None:
            return fallback
        if section in self.defaults and key in self.defaults[section]:
            return self.defaults[section][key]
        return default

    def set_value(self, section, key, value):
        if not self.config_parser.has_section(section):
            self.config_parser.add_section(section)
        self.config_parser.set(section, key, str(value))
        if not self._initializing:
            if self._save_timer is None:
                parent = QApplication.instance() or None
                self._save_timer = QTimer(parent)
                self._save_timer.setSingleShot(True)
                self._save_timer.timeout.connect(self.save_config)
            self._save_timer.start(500)

    def get_preset_names(self):
        return list(self.presets.keys())

    def get_preset(self, name):
        return self.presets.get(name.title())

    def save_preset(self, name):
        norm_name = name.title()
        self.presets[norm_name] = {
            k: self.get_value("light", k) for k in ("r", "g", "b", "a")
        }
        if not self.config_parser.has_section("presets"):
            self.config_parser.add_section("presets")
        self.config_parser.set(
            "presets", norm_name, json.dumps(self.presets[norm_name])
        )
        self.save_config()
        return True

    def delete_preset(self, name):
        norm_name = name.title()
        if norm_name in self.presets and norm_name not in ["Light Mode", "Dark Mode"]:
            del self.presets[norm_name]
            if self.config_parser.has_option("presets", norm_name):
                self.config_parser.remove_option("presets", norm_name)
            self.save_config()
            return True
        return False

    def load_preset(self, name):
        norm_name = name.title()
        if norm_name in self.presets:
            for key, value in self.presets[norm_name].items():
                self.set_value("light", key, value)
                self.set_value("dark", key, value)
            self.set_value("gui", "last_preset", norm_name)
            return True
        return False

    def reset_to_defaults(self):
        try:
            self._create_default_config()
            self.config_parser = configparser.ConfigParser()
            self.presets.clear()
            self._load_config()
            log_info("Settings reset to defaults.")
            return True
        except Exception as e:
            log_error(f"Error resetting settings: {str(e)}")
            return False

    def get_dll_path(self):
        return self.dll_path

    def get_base_dir(self):
        return self.base_path

    def get_config_dir(self):
        return self.config_dir

    def get_config_path(self):
        return self.config_path

    def get_log_path(self):
        return self.log_path


class BaseGroup(QGroupBox):
    def __init__(self, title, config):
        super().__init__(title)
        self.config = config
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.init_ui()

    def init_ui(self):
        pass


class EffectGroup(BaseGroup):
    effect_changed = pyqtSignal(bool)

    def __init__(self, config):
        self.radio_buttons = {}
        self.button_group = QButtonGroup(exclusive=True)
        super().__init__("Effects", config)

    def init_ui(self):
        layout = QVBoxLayout()
        self.radio_layout = QGridLayout()
        effects = [
            ("0", "Blur", "Windows 10/early 11 Blur effect"),
            ("1", "Acrylic", "Windows 10 Acrylic effect"),
            ("2", "Mica", "Windows 11 Mica effect"),
            ("3", "Blur (Clear)", "Blur (Clear) effect"),
            ("4", "Mica Alt", "Alternative system colors"),
        ]
        for i, (effect_key, effect_name, tooltip) in enumerate(effects):
            radio = QRadioButton(effect_name)
            radio.setChecked(self.config.get_value("config", "effect") == effect_key)
            from functools import partial

            radio.clicked.connect(partial(self.on_effect_changed, effect_key))
            radio.setToolTip(tooltip)
            self.radio_buttons[effect_key] = radio
            self.button_group.addButton(radio)
            self.radio_layout.addWidget(radio, i // 2, i % 2)
        layout.addLayout(self.radio_layout)
        self.layout().addLayout(layout)
        self.refresh_effects()

    def refresh_effects(self):
        show_unsupported = (
            self.config.get_value(
                "gui", "showUnsupportedEffects", fallback="false"
            ).lower()
            == "true"
        )
        effect_support = {
            "0": gwv()[0] == 10 and gwv()[2] < 22621,
            "1": True,
            "2": gwv()[0] == 10 and gwv()[2] >= 22000,
            "3": gwv()[0] == 10 and gwv()[2] < 26100,
            "4": gwv()[0] == 10 and gwv()[2] >= 22000,
        }
        current_effect = self.config.get_value("config", "effect", fallback="1")
        needs_fallback = not show_unsupported and not effect_support.get(
            current_effect, False
        )
        for effect_key, radio in self.radio_buttons.items():
            is_supported = effect_support.get(effect_key, False)
            tooltip = radio.toolTip()
            tooltip = tooltip.replace(" (Incompatible with system)", "")
            if not is_supported:
                tooltip += " (Incompatible with system)"
            radio.setEnabled(is_supported or show_unsupported)
            radio.setToolTip(tooltip)
            radio.setStyleSheet("QRadioButton:disabled {color: #808080;}")
            if needs_fallback and effect_key == current_effect:
                radio.setChecked(False)
        if needs_fallback:
            fallback_effect = "1"
            self.radio_buttons[fallback_effect].setChecked(True)
            self.config.set_value("config", "effect", fallback_effect)
            self.on_effect_changed(fallback_effect)
        QTimer.singleShot(0, self.updateGeometry)

    def on_effect_changed(self, effect_key, checked=None):
        self.config.set_value("config", "effect", str(effect_key))
        self.effect_changed.emit(True)

    def refresh_from_config(self):
        effect = self.config.get_value("config", "effect", fallback="1")
        for effect_key, radio in self.radio_buttons.items():
            radio.setChecked(effect_key == effect)


class OptionsGroup(BaseGroup):
    def __init__(self, config):
        self.checkboxes = {}
        super().__init__("Options", config)

    def init_ui(self):
        options = [
            (
                "Clear Address Bar",
                "clearAddress",
                "Clear the background of the address bar.",
            ),
            (
                "Clear Scrollbar Bg",
                "clearBarBg",
                "Clear the background color of the scrollbar (May differ from system style).",
            ),
            (
                "Clear WinUI Bg",
                "clearWinUIBg",
                "Remove toolbar background color (Win11 WinUI/XamlIslands only).",
            ),
            (
                "Show Separator",
                "showLine",
                "Show split line between TreeView and DUIView.",
            ),
        ]
        grid = QGridLayout()
        for idx, (text, key, tooltip) in enumerate(options):
            cb = QCheckBox(text)
            cb.setChecked(self.config.get_value("config", key) == "true")
            cb.clicked.connect(
                lambda checked, k=key: self.config.set_value(
                    "config", k, str(checked).lower()
                )
            )
            cb.setToolTip(tooltip)
            self.checkboxes[key] = cb
            row = idx % 2
            col = idx // 2
            grid.addWidget(cb, row, col)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self.layout().addLayout(grid)
        self.refresh_options()

    def refresh_options(self):
        show_unsupported = (
            self.config.get_value(
                "gui", "showUnsupportedOptions", fallback="false"
            ).lower()
            == "true"
        )
        if winui_cb := self.checkboxes.get("clearWinUIBg"):
            is_supported = gwv()[0] == 10 and gwv()[2] >= 22000
            winui_cb.setEnabled(is_supported or show_unsupported)
            if not is_supported:
                winui_cb.setToolTip(
                    winui_cb.setToolTip() + " (Incompatible with system)"
                )
            winui_cb.setStyleSheet("QCheckBox:disabled { color: #808080; }")
        self.updateGeometry()

    def refresh_from_config(self):
        self.refresh_options()
        for key, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(self.config.get_value("config", key) == "true")
            checkbox.blockSignals(False)


class PresetsColorsGroup(BaseGroup):
    def __init__(self, config):
        self.preview = ColorPreview()
        self.preview.colorSelected.connect(self.on_color_picked)
        super().__init__("Presets && Colors", config)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(2)
        preset_layout.setContentsMargins(0, 0, 0, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.setFixedHeight(STANDARD_HEIGHT)
        self.preset_combo.setToolTip("Select a preset")
        self.update_presets()
        last_preset = self.config.get_value("gui", "last_preset", fallback=None)
        if last_preset and last_preset in self.config.get_preset_names():
            index = self.preset_combo.findText(last_preset)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        preset_btns = [
            ("save_btn", "save", "Save current settings as preset", self.save_preset),
            ("delete_btn", "trash", "Delete selected preset", self.delete_preset),
        ]
        for attr_name, icon_name, tooltip, callback in preset_btns:
            btn = create_icon_button(
                icon=icon_name,
                tooltip=tooltip,
                callback=callback,
                min_width=None,
                icon_only=True,
                object_name=attr_name.replace("_", "") + "Button"
            )
            setattr(self, attr_name, btn)
            preset_layout.addWidget(btn)
        layout.addLayout(preset_layout)
        layout.addWidget(self.preview)
        self.layout().addLayout(layout)
        self.update_color_preview()

    def on_preset_changed(self, name):
        if name and self.config.load_preset(name):
            self.update_color_preview()
            self.config.set_value("gui", "last_preset", name)

    def save_preset(self, checked=False):
        name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        if ok and name:
            if self.config.save_preset(name):
                self.update_presets()
                self.preset_combo.setCurrentText(name)

    def delete_preset(self, checked=False):
        name = self.preset_combo.currentText()
        if not name:
            return
        if name in self.config.get_preset_names():
            if self.config.delete_preset(name):
                self.update_presets()
                QMessageBox.information(self, "Success", "Preset deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Cannot delete default presets.")

    def update_presets(self):
        current = self.preset_combo.currentText()
        self.preset_combo.clear()
        self.preset_combo.addItems(self.config.get_preset_names())
        if current and current in self.config.get_preset_names():
            index = self.preset_combo.findText(current)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)

    def on_color_picked(self, r, g, b, a):
        for section in ("light", "dark"):
            self.config.set_value(section, "r", str(r))
            self.config.set_value(section, "g", str(g))
            self.config.set_value(section, "b", str(b))
            self.config.set_value(section, "a", str(a))
        self.update_color_preview()

    def update_color_preview(self):
        r, g, b, a = get_rgba_from_config(self.config, "light")
        effect_key = self.config.get_value("config", "effect", fallback="1")
        is_supported = effect_key not in ("2", "4")
        self.setEnabled(is_supported)
        if not is_supported:
            self.setToolTip(
                "Color selection is not supported for Mica and Mica Alt effects."
            )
        else:
            self.setToolTip("")
        for child in self.findChildren(QWidget):
            child.setToolTip(self.toolTip())
        self.preview.setEnabled(is_supported)
        if is_supported:
            self.preview.update_color(r, g, b, a)
        else:
            grey = int(0.299 * r + 0.587 * g + 0.114 * b)
            self.preview.update_color(grey, grey, grey, int(a * 0.5))

    def refresh_from_config(self):
        self.update_color_preview()

    def on_effect_changed(self, checked):
        self.update_color_preview()


class ColorPreview(QFrame):
    colorSelected = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setFixedHeight(STANDARD_HEIGHT)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setObjectName("colorPreview")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Double-click to open color picker")
        self.edit_icon = QLabel(self)
        icon_size = int(STANDARD_HEIGHT * 0.6)
        self.edit_icon.setFixedSize(icon_size, icon_size)
        self.edit_icon.setObjectName("editColorIcon")
        self.edit_icon.setToolTip("Edit color")
        self.edit_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 7, 0)
        layout.setSpacing(2)
        layout.addStretch(1)
        layout.addWidget(
            self.edit_icon,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self._last_icon_color = None
        self._color_dialog = None
        self.update_edit_icon((255, 255, 255, 255))

    def mouseDoubleClickEvent(self, event):
        try:
            self.open_color_picker()
            super().mouseDoubleClickEvent(event)
        except Exception as e:
            log_error(f"Error in color picker: {str(e)}")

    def open_color_picker(self):
        try:
            if not self._color_dialog:
                self._color_dialog = QColorDialog(self)
                self._color_dialog.setWindowTitle("Choose Color")
                self._color_dialog.setOption(
                    QColorDialog.ColorDialogOption.ShowAlphaChannel, True
                )
            style = self.styleSheet()
            current_r, current_g, current_b, current_a = (
                get_rgba_from_config(self.parent().config, "light")
                if hasattr(self.parent(), "config")
                else (255, 255, 255, 128)
            )
            import re

            if "rgba" in style:
                if rgba_match := re.search(
                    r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", style
                ):
                    current_r, current_g, current_b, current_a = [
                        int(rgba_match.group(i)) for i in range(1, 5)
                    ]
            self._color_dialog.setCurrentColor(
                QColor(current_r, current_g, current_b, current_a)
            )
            if self._color_dialog.exec() == QColorDialog.DialogCode.Accepted:
                color = self._color_dialog.currentColor()
                self.colorSelected.emit(
                    color.red(), color.green(), color.blue(), color.alpha()
                )
        except Exception as e:
            log_error(f"Error opening color picker: {str(e)}")

    def update_color(self, r, g, b, a):
        self.setEnabled(True)
        self.setStyleSheet(
            f"#colorPreview {{ background-color: rgba({r}, {g}, {b}, {a}); border-radius: 4px; }}"
        )
        self.setToolTip("Double-click to open color picker")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_edit_icon((r, g, b, a))
        self.update()

    def update_edit_icon(self, rgba):
        icon_color = (
            "rgb(32,32,32)"
            if (rgba[0] * 0.299 + rgba[1] * 0.587 + rgba[2] * 0.114) > 128
            else "rgb(240,240,240)"
        )
        if self._last_icon_color == icon_color:
            return
        self._last_icon_color = icon_color
        icon_path = Path(__file__).parent / "assets" / "icons" / "edit.svg"
        icon_size = self.edit_icon.size()
        if icon_path.exists():
            with open(icon_path, "r", encoding="utf-8") as f:
                svg = f.read().replace("{color}", icon_color)
            pixmap = QPixmap()
            pixmap.loadFromData(svg.encode("utf-8"), "SVG")
            self.edit_icon.setPixmap(
                pixmap.scaled(
                    icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.edit_icon.setPixmap(get_icon("edit", icon_color).pixmap(icon_size))


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.ui_elements = {}
        self._icon_buttons = []
        self.setWindowTitle("Settings")
        self.setFixedSize(275, 250)
        self._build_ui()
        self.update_icon_colors()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.compat_group())
        layout.addWidget(self.advanced_group())
        layout.addStretch()
        self.reset_btn = create_icon_button(
            text="Reset Settings",
            icon="undo",
            tooltip="Reset Settings",
            callback=self.reset_settings,
            object_name="resetButton",
        )
        self.reset_btn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        )
        layout.addWidget(self.reset_btn)

    def compat_group(self):
        group = QGroupBox("Compatibility")
        vbox = QVBoxLayout(group)
        for element_id, text, section, key, callback in [
            (
                "show_unsupported",
                "Enable unsupported effects",
                "gui",
                "showUnsupportedEffects",
                self.unsupported_effects_changed,
            ),
            (
                "show_unsupported_options",
                "Enable unsupported options",
                "gui",
                "showUnsupportedOptions",
                self.unsupported_options_changed,
            ),
        ]:
            cb = QCheckBox(text)
            cb.setFixedHeight(STANDARD_HEIGHT)
            cb.setObjectName(element_id)
            cb.setChecked(
                self.config.get_value(section, key, fallback="false").lower() == "true"
            )
            cb.clicked.connect(callback)
            vbox.addWidget(cb)
            self.ui_elements[element_id] = cb
        return group

    def advanced_group(self):
        group = QGroupBox("Advanced")
        form = QFormLayout(group)
        config_row = QWidget()
        config_layout = QHBoxLayout(config_row)
        config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(4)
        config_layout.addStretch(1)
        config_row.setFixedHeight(STANDARD_HEIGHT)
        open_btn = create_icon_button(
            icon="folder",
            tooltip="Open config directory",
            callback=lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.config.get_config_dir()))),
            icon_only=True
        )
        edit_btn = create_icon_button(
            icon="edit",
            tooltip="Edit config file",
            callback=lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.config.get_config_path()))),
            icon_only=True
        )
        config_layout.addWidget(open_btn)
        config_layout.addWidget(edit_btn)
        self._icon_buttons.extend([(open_btn, "folder"), (edit_btn, "edit")])
        form.addRow(QLabel("Configuration:"), config_row)
        self.log_level_combo = QComboBox()
        self.log_level_combo.setFixedHeight(STANDARD_HEIGHT - 2)
        self.log_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        current_level = self.config.get_value(
            "gui", "logLevel", fallback="ERROR"
        ).upper()
        idx = self.log_level_combo.findText(current_level)
        if idx >= 0:
            self.log_level_combo.setCurrentIndex(idx)
        self.log_level_combo.currentTextChanged.connect(self.on_log_level_changed)
        form.addRow(QLabel("Log Level:"), self.log_level_combo)
        return group

    def update_icon_colors(self):
        for btn, icon_name in self._icon_buttons:
            if isinstance(btn, QLabel):
                btn.setPixmap(get_icon(icon_name).pixmap(16, 16))
            elif isinstance(btn, QPushButton):
                btn.setIcon(get_icon(icon_name))

    def showEvent(self, event):
        super().showEvent(event)
        self.update_icon_colors()
        self.refresh_ui()

    def refresh_ui(self):
        config_elements = {
            "show_unsupported": ("gui", "showUnsupportedEffects", None),
            "show_unsupported_options": ("gui", "showUnsupportedOptions", "false"),
        }
        for elem_id, (section, key, fallback) in config_elements.items():
            if elem_id in self.ui_elements:
                self.ui_elements[elem_id].setChecked(
                    self.config.get_value(section, key, fallback=fallback).lower()
                    == "true"
                )
        if hasattr(self, "log_level_combo"):
            current_level = self.config.get_value(
                "gui", "logLevel", fallback="ERROR"
            ).upper()
            idx = self.log_level_combo.findText(current_level)
            if idx >= 0:
                self.log_level_combo.setCurrentIndex(idx)

    def on_log_level_changed(self, level):
        self.config.set_value("gui", "logLevel", level.upper())

    def unsupported_effects_changed(self, checked):
        self.config.set_value("gui", "showUnsupportedEffects", str(checked).lower())
        if hasattr(self.parent, "get_component"):
            effects_group = self.parent.get_component("effects_group")
            effects_group.refresh_effects()

    def unsupported_options_changed(self, checked):
        self.config.set_value("gui", "showUnsupportedOptions", str(checked).lower())
        if hasattr(self.parent, "get_component"):
            options_group = self.parent.get_component("options_group")
            options_group.refresh_options()

    def reset_settings(self):
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to default?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.config.reset_to_defaults():
                parent = self.parent
                parent.get_component("effects_group").config = self.config
                parent.get_component("options_group").config = self.config
                presets_group = parent.get_component("presets_colors_group")
                presets_group.config = self.config
                parent.get_component("effects_group").refresh_from_config()
                parent.get_component("effects_group").refresh_effects()
                parent.get_component("options_group").refresh_from_config()
                presets_group.refresh_from_config()
                presets_group.update_presets()
                default_preset = self.config.get_value(
                    "gui", "last_preset", "Light Mode"
                )
                preset_combo = presets_group.preset_combo
                index = preset_combo.findText(default_preset)
                if index >= 0:
                    preset_combo.setCurrentIndex(index)
                elif preset_combo.count() > 0:
                    preset_combo.setCurrentIndex(0)
                self.refresh_ui()
                QMessageBox.information(self, "Success", "Settings reset successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to reset settings!")


class DLLRegistrationThread(QThread):
    status = pyqtSignal(str, bool)

    def __init__(self, config, action):
        super().__init__()
        self.config = config
        self.action = action

    def run(self):
        dll_path = self.config.get_dll_path()
        if not os.path.exists(dll_path):
            self.status.emit(f"DLL not found: {dll_path}", False)
            log_error(f"DLL not found for registration: {dll_path}")
            return
        try:
            if self.action == "register":
                if check_dll_registered(self.config):
                    log_info(f"DLL already registered: {dll_path}, skipping regsvr32.")
                    self.status.emit(
                        "DLL already registered. Restarting Explorer...", True
                    )
                    subprocess.run("taskkill /f /im explorer.exe", shell=True)
                    time.sleep(1.5)
                    subprocess.Popen("explorer.exe", shell=True)
                    self.status.emit("Operation successful", True)
                    log_info(f"DLL {self.action} operation successful (skipped regsvr32).")
                    return
                log_info(f"Registering DLL: {dll_path}")
                result = subprocess.run(
                    f'regsvr32 /s "{dll_path}"',
                    shell=True,
                    capture_output=True,
                    text=True,
                )
            else:
                log_info(f"Unregistering DLL: {dll_path}")
                result = subprocess.run(
                    f'regsvr32 /u /s "{dll_path}"',
                    shell=True,
                    capture_output=True,
                    text=True,
                )
            if result.returncode != 0:
                self.status.emit(f"regsvr32 failed: {result.stderr}", False)
                log_error(f"regsvr32 failed: {result.stderr}")
                return
            subprocess.run("taskkill /f /im explorer.exe", shell=True)
            time.sleep(1.5)
            subprocess.Popen("explorer.exe", shell=True)
            self.status.emit("Operation successful", True)
            log_info(f"DLL {self.action} operation successful.")
        except Exception as e:
            self.status.emit(f"Exception: {str(e)}", False)
            log_error(f"Exception during DLL {self.action}: {str(e)}")


class DLLStatusThread(QThread):
    status_updated = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True
        self.check_interval = 15000
        self._force_check = False

    def run(self):
        while self.running:
            try:
                status = check_dll_registered(self.config)
                self.status_updated.emit(status)
                log_info(f"DLL status thread check: {status}")
                waited = 0
                while (
                    waited < self.check_interval
                    and self.running
                    and not self._force_check
                ):
                    self.msleep(100)
                    waited += 100
                self._force_check = False
            except Exception as e:
                log_error(f"Error in DLL status thread: {str(e)}")
                self.msleep(self.check_interval)

    def force_check(self):
        self._force_check = True

    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    update_available = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self._ui_components = {}
        self._settings_dialog = None
        self._dll_status_thread = None
        self.load_selected_effect = lambda: None
        self.update_available.connect(self.show_update_dialog)
        self.init_ui()
        QTimer.singleShot(200, self.start_background_tasks)

    def init_ui(self):
        self.setWindowTitle("Mica4U")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setText(
            '<span style="font-size: 11pt; letter-spacing: 1px;"><b>DLL Status: '
            '<font color="#808080">Checking...</font></b></span>'
        )
        layout.addWidget(self.status_label)
        effects_group = self.get_component("effects_group")
        options_group = self.get_component("options_group")
        presets_colors_group = self.get_component("presets_colors_group")
        effects_group.effect_changed.connect(presets_colors_group.on_effect_changed)
        for component in [effects_group, options_group, presets_colors_group]:
            layout.addWidget(component)
        action_layout = QHBoxLayout()
        self.create_action_buttons(action_layout)
        layout.addLayout(action_layout)
        self.setFixedSize(275, 350)
        self.load_selected_effect = self._load_selected_effect_impl
        self.load_selected_effect()

    def start_background_tasks(self):
        if not self._dll_status_thread:
            self._dll_status_thread = DLLStatusThread(self.config)
            self._dll_status_thread.status_updated.connect(self.update_dll_status)
            self._dll_status_thread.start()
        check_updates = self.config.get_value(
            "gui", "checkForUpdates", fallback="true"
        ).lower()
        if check_updates != "false":
            QTimer.singleShot(0, self.check_for_updates)

    def check_for_updates(self):
        try:
            url = "https://github.com/DrkCtrlDev/Mica4U/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "Mica4U"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode("utf-8")
            m = re.search(r'/tag/v?([\d.]+)"', html)
            if not m:
                return
            latest = m.group(1)
            if tuple(map(int, latest.split("."))) > tuple(map(int, VERSION.split("."))):
                self.update_available.emit(latest)
        except Exception:
            pass

    def show_update_dialog(self, latest_version):
        def show():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Update Available")
            msg.setText(
                f"A new version of Mica4U is available: v{latest_version}\n\nYou are running v{VERSION}."
            )
            msg.setStandardButtons(
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open
            )
            msg.button(QMessageBox.StandardButton.Open).setText("Open Releases Page")
            ret = msg.exec()
            if ret == QMessageBox.StandardButton.Open:
                QDesktopServices.openUrl(
                    QUrl("https://github.com/DrkCtrlDev/Mica4U/releases")
                )

        QTimer.singleShot(0, show)

    def get_component(self, name):
        if name not in self._ui_components:
            if name == "effects_group":
                self._ui_components[name] = EffectGroup(self.config)
            elif name == "options_group":
                self._ui_components[name] = OptionsGroup(self.config)
            elif name == "presets_colors_group":
                self._ui_components[name] = PresetsColorsGroup(self.config)
        return self._ui_components[name]

    def update_icon_colors(self):
        for btn, icon_name in getattr(self, "_icon_buttons", []):
            if isinstance(btn, QLabel):
                btn.setPixmap(get_icon(icon_name).pixmap(16, 16))
            elif isinstance(btn, QPushButton):
                btn.setIcon(get_icon(icon_name))

    def update_dll_status(self, is_initialized):
        status_text = "Initialized" if is_initialized else "Not Initialized"
        color = "green" if is_initialized else "red"
        self.status_label.setText(
            f'<span style="font-size: 11pt; letter-spacing: 1px;"><b>DLL Status: '
            f'<font color="{color}">{status_text}</font></b></span>'
        )

    def closeEvent(self, event):
        if self._dll_status_thread:
            self._dll_status_thread.stop()
            self._dll_status_thread.wait(500)
        super().closeEvent(event)

    def _load_selected_effect_impl(self):
        effect = self.config.get_value("config", "effect", fallback="1")
        effects_group = self.get_component("effects_group")
        if effect in effects_group.radio_buttons:
            effects_group.radio_buttons[effect].setChecked(True)

    def install_effects(self):
        self.dll_registration_thread = DLLRegistrationThread(self.config, "register")
        self.dll_registration_thread.finished.connect(self.trigger_dll_status_check)
        self.dll_registration_thread.start()

    def uninstall_effects(self):
        self.dll_registration_thread = DLLRegistrationThread(self.config, "unregister")
        self.dll_registration_thread.finished.connect(self.trigger_dll_status_check)
        self.dll_registration_thread.start()

    def trigger_dll_status_check(self):
        if self._dll_status_thread:
            self._dll_status_thread.force_check()

    def create_action_buttons(self, action_layout):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.setContentsMargins(0, 3, 0, 0)
        buttons = [
            ("install_btn","Install","download","Install effects",self.install_effects,100,False),
            ("uninstall_btn","Uninstall","trash","Uninstall effects",self.uninstall_effects,100,False),
            ("settings_btn","","cog","Open settings dialog",self.open_settings,None,True)
        ]
        for name, text, icon, tooltip, callback, min_width, icon_only in buttons:
            btn = create_icon_button(
                text=text,
                icon=icon,
                tooltip=tooltip,
                callback=callback,
                min_width=min_width,
                icon_only=icon_only,
                object_name=f"{name}Button"
            )
            setattr(self, name, btn)
            button_layout.addWidget(btn)
        action_layout.addLayout(button_layout)

    def open_settings(self):
        if not self._settings_dialog:
            self._settings_dialog = SettingsDialog(self.config, self)
        self._settings_dialog.refresh_ui()
        self._settings_dialog.exec()


def main():
    atexit.register(cleanup_temp)
    app = QApplication(sys.argv)
    config = ConfigManager()
    log_level = config.get_value("gui", "logLevel", default="ERROR")
    logger = setup_logger(config.get_log_path(), log_level)
    log_info("Mica4U application started.")
    window = MainWindow()
    window.setWindowIcon(QIcon(str(Path(__file__).parent / "icon.ico")))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
