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
import urllib.request, re
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, QCheckBox, QLabel, QPushButton, QComboBox, QGridLayout, QDialog, QMessageBox, QInputDialog, QButtonGroup, QColorDialog, QSizePolicy, QFormLayout)
from PyQt6.QtCore import (Qt, QUrl, QTimer, QThread, pyqtSignal, QMargins)
from PyQt6.QtGui import (QIcon, QDesktopServices, QColor, QPixmap, QPalette)

CONSTANTS = {"VERSION": "1.7.2"}

def setup_logger(log_path, log_level="ERROR"):
    global logger
    logger = logging.getLogger("Mica4U")
    logger.setLevel(getattr(logging, log_level.upper(), logging.ERROR))
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger

def log_message(level, msg):
    if logger:
        getattr(logger, level.lower())(msg)

def cleanup_temp():
    temp_dir = Path(tempfile.gettempdir())
    now = time.time()
    for filepath in temp_dir.iterdir():
        if (filepath.name.startswith("_MEI") and filepath.is_dir()) or filepath.suffix in (".tmp", ".log"):
            if now - filepath.stat().st_mtime > 86400:
                try:
                    filepath.unlink() if filepath.is_file() else shutil.rmtree(filepath, ignore_errors=True)
                    log_message("info", f"Removed {'file' if filepath.is_file() else 'directory'}: {filepath}")
                except Exception as e:
                    log_message("warning", f"Failed to remove {filepath}: {e}")

def gwv():
    ver = platform.version().split(".")
    return (int(ver[0]), int(ver[1]), int(ver[2]))

def get_icon_color():
    return "black" if QApplication.instance().palette().color(QPalette.ColorRole.Window).lightness() > 128 else "white"

_icon_cache = {}
def get_icon(icon_name, color=None):
    color = color or ("black" if QApplication.instance().palette().color(QPalette.ColorRole.Window).lightness() > 128 else "white")
    cache_key = f"{icon_name}:{color}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    icon_path = Path(__file__).parent / "assets" / "icons" / f"{icon_name}.svg"
    icon = QIcon()
    if icon_path.exists():
        with open(icon_path, "r", encoding="utf-8") as f:
            svg_content = f.read().replace("{color}", color)
        pixmap = QPixmap()
        pixmap.loadFromData(svg_content.encode("utf-8"), "SVG")
        icon.addPixmap(pixmap)
    _icon_cache[cache_key] = icon
    return icon

def check_dll_registered(config):
    try:
        dll_path = config.get_dll_path()
        dll_name = os.path.basename(dll_path).lower()
        result = subprocess.run(
            f'reg query "HKCR\\CLSID" /s /f "{dll_name}"',
            capture_output=True, text=True, shell=True
        )
        return result.returncode == 0 and dll_name in result.stdout.lower()
    except Exception as e:
        log_message("error", f"Error checking DLL status: {e}")
        return False
    
def check_compatibility(config, key, version_check):
    show_unsupported = config.get_value("gui", "showUnsupported", "false").lower() == "true"
    return version_check() or show_unsupported

def create_icon_button(text="", icon=None, tooltip=None, callback=None, min_width=None, icon_only=False, object_name=None):
    btn = QPushButton("" if icon_only else text)
    btn.setFixedHeight(30)
    if min_width:
        btn.setMinimumWidth(min_width)
    elif icon_only:
        btn.setFixedWidth(30)
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

class ConfigManager:
    def __init__(self):
        self.base_path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
        self.portable_mode = (self.base_path / "portable.ini").exists()
        self.config_dir = self.base_path if self.portable_mode else Path(os.getenv("APPDATA", "")) / "Mica4U"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.dll_path = self.config_dir / "ExplorerBlurMica.dll"
        self.config_path = self.config_dir / "config.json"
        self.log_path = self.config_dir / "Mica4U.log"
        self.defaults = {
            "config": {"effect": "1", "clearAddress": "true", "clearBarBg": "true", "clearWinUIBg": "true", "showLine": "false"},
            "light": {"r": "255", "g": "255", "b": "255", "a": "120"},
            "dark": {"r": "255", "g": "255", "b": "255", "a": "120"},
            "gui": {"showUnsupported": "false", "last_preset": "Light Mode", "logLevel": "ERROR", "checkForUpdates": "true"},
            "presets": {"Light Mode": {"r": "220", "g": "220", "b": "220", "a": "160"}, "Dark Mode": {"r": "0", "g": "0", "b": "0", "a": "120"}}
        }
        setup_logger(self.get_log_path(), self.defaults["gui"]["logLevel"])
        self.config = self._load_config()
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self.save_config)
        self.load_preset(self.get_value("gui", "last_preset", "Light Mode"))

    def _load_config(self):
        try:
            return json.load(self.config_path.open("r", encoding="utf-8")) if self.config_path.exists() else (log_message("info", "Created default config file."), self.defaults.copy())[1]
        except json.JSONDecodeError as e:
            log_message("warning", f"Failed to load config: {e}. Using defaults.")
            return self.defaults.copy()

    def save_config(self):
        try:
            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            log_message("info", "Configuration saved.")
            self.sync_ini_with_json()
        except OSError as e:
            log_message("error", f"Failed to save config: {e}")

    def get_value(self, section, key, fallback=None):
        return self.config.get(section, {}).get(key, self.defaults.get(section, {}).get(key, fallback))

    def set_value(self, section, key, value):
        self.config.setdefault(section, {})[key] = str(value)
        self._save_timer.start(1000)
        if section in ("config", "light", "dark"):
            self.sync_ini_with_json()

    def sync_ini_with_json(self):
        config = configparser.ConfigParser()
        for section in ("config", "light", "dark"):
            if section in self.config:
                config[section] = {k: str(v) for k, v in self.config[section].items()}
        with (self.config_dir / "config.ini").open("w", encoding="utf-8") as f:
            config.write(f)

    def get_preset_names(self):
        return list(self.config.get("presets", {}).keys())

    def get_preset(self, name):
        return self.config.get("presets", {}).get(name.title())

    def save_preset(self, name):
        norm_name = name.title()
        self.config.setdefault("presets", {})[norm_name] = {k: self.get_value("light", k) for k in ("r", "g", "b", "a")}
        self.set_value("gui", "last_preset", norm_name)
        log_message("info", f"Preset saved: {norm_name}")
        return True

    def delete_preset(self, name):
        norm_name = name.title()
        if norm_name in self.config.get("presets", {}) and norm_name not in ["Light Mode", "Dark Mode"]:
            del self.config["presets"][norm_name]
            self.save_config()
            log_message("info", f"Preset deleted: {norm_name}")
            return True
        return False

    def load_preset(self, name):
        if preset := self.get_preset(name.title()):
            for section in ("light", "dark"):
                for key, value in preset.items():
                    self.set_value(section, key, value)
            self.set_value("gui", "last_preset", name.title())
            return True
        return False

    def reset_to_defaults(self):
        try:
            self.config = self.defaults.copy()
            self.save_config()
            log_message("info", "Settings reset to defaults.")
            return True
        except OSError as e:
            log_message("error", f"Error resetting settings: {e}")
            return False

    def get_dll_path(self):
        return self.dll_path

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
        self.setLayout(QVBoxLayout(spacing=4, contentsMargins=QMargins(5, 5, 5, 5)))
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
        effects = [
            ("0", "Blur", "Applies a translucent blur effect, softening the background content for Windows 10 and early Windows 11 builds."),
            ("1", "Acrylic", "Creates a frosted glass effect with a smooth, semi-transparent blur, blending with the Windows 10 theme."),
            ("2", "Mica", "Introduces a subtle, dynamic background tint that adapts to the desktop wallpaper, exclusive to Windows 11."),
            ("3", "Blur (Clear)", "Provides a clear, lightweight blur effect, emphasizing transparency for Windows 10 and select Windows 11 versions."),
            ("4", "Mica Alt", "Uses alternative system colors with a Mica-like effect, offering a distinct visual style for Windows 11.")
        ]
        grid = QGridLayout()
        for i, (key, name, tooltip) in enumerate(effects):
            radio = QRadioButton(name)
            radio.setChecked(self.config.get_value("config", "effect") == key)
            radio.clicked.connect(lambda _, k=key: self.on_effect_changed(k))
            radio.setToolTip(tooltip)
            self.radio_buttons[key] = radio
            self.button_group.addButton(radio)
            grid.addWidget(radio, i // 2, i % 2)
        self.layout().addLayout(grid)
        self.refresh_effects()

    def refresh_effects(self):
        effect_support = {
            "0": lambda: gwv()[0] == 10 and gwv()[2] < 22621,
            "1": lambda: True,
            "2": lambda: gwv()[0] == 10 and gwv()[2] >= 22000,
            "3": lambda: gwv()[0] == 10 and gwv()[2] < 26100,
            "4": lambda: gwv()[0] == 10 and gwv()[2] >= 22000,
        }
        current_effect = self.config.get_value("config", "effect", "1")
        for key, radio in self.radio_buttons.items():
            is_supported = check_compatibility(self.config, key, effect_support[key])
            radio.setEnabled(is_supported)
            radio.setToolTip(f"{radio.toolTip().split(' (')[0]}{' (Incompatible with system)' if not is_supported else ''}")
            radio.setStyleSheet("QRadioButton:disabled {color: #808080;}")
            if not is_supported and key == current_effect:
                radio.setChecked(False)
                self.radio_buttons["1"].setChecked(True)
                self.config.set_value("config", "effect", "1")
                self.on_effect_changed("1")

    def on_effect_changed(self, effect_key):
        self.config.set_value("config", "effect", effect_key)
        self.effect_changed.emit(True)

    def refresh_from_config(self):
        effect = self.config.get_value("config", "effect", "1")
        for key, radio in self.radio_buttons.items():
            radio.setChecked(key == effect)

class OptionsGroup(BaseGroup):
    def __init__(self, config):
        self.checkboxes = {}
        super().__init__("Options", config)

    def init_ui(self):
        options = [
            ("Clear Address", "clearAddress", "Clear the background of the address bar."),
            ("Clear Scrollbar", "clearBarBg", "Clear the background color of the scrollbar (May differ from system style)."),
            ("Clear WinUI", "clearWinUIBg", "Remove toolbar background color (Win11 WinUI/XamlIslands only)."),
            ("Show Separator", "showLine", "Show split line between TreeView and DUIView."),
        ]
        grid = QGridLayout()
        for idx, (text, key, tooltip) in enumerate(options):
            cb = QCheckBox(text)
            cb.setChecked(self.config.get_value("config", key) == "true")
            cb.clicked.connect(lambda checked, k=key: self.config.set_value("config", k, str(checked).lower()))
            cb.setToolTip(tooltip)
            self.checkboxes[key] = cb
            grid.addWidget(cb, idx % 2, idx // 2)
        self.layout().addLayout(grid)
        self.refresh_options()

    def refresh_options(self):
        if winui_cb := self.checkboxes.get("clearWinUIBg"):
            is_supported = check_compatibility(self.config, "clearWinUIBg", lambda: gwv()[0] == 10 and gwv()[2] >= 22000)
            winui_cb.setEnabled(is_supported)
            winui_cb.setToolTip(f"{winui_cb.toolTip().split(' (')[0]}{' (Incompatible with system)' if not is_supported else ''}")
            winui_cb.setStyleSheet("QCheckBox:disabled { color: #808080; }")

    def refresh_from_config(self):
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
        layout = QVBoxLayout(spacing=2, contentsMargins=QMargins(0, 0, 0, 0))
        preset_layout = QHBoxLayout(spacing=2, contentsMargins=QMargins(0, 0, 0, 0))
        self.preset_combo = QComboBox()
        self.preset_combo.setFixedHeight(28)
        self.preset_combo.setToolTip("Select a preset")
        self.update_preset_combo()
        self.preset_combo.setCurrentText(self.config.get_value("gui", "last_preset", "Light Mode"))
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        buttons = [
            ("save_btn", "save", "Save current settings as preset", self.save_preset),
            ("delete_btn", "trash", "Delete selected preset", self.delete_preset)
        ]
        for name, icon, tooltip, callback in buttons:
            btn = create_icon_button(icon=icon, tooltip=tooltip, callback=callback, icon_only=True, object_name=name.replace("_", "") + "Button")
            setattr(self, name, btn)
            preset_layout.addWidget(btn)
        layout.addLayout(preset_layout)
        layout.addWidget(self.preview)
        self.layout().addLayout(layout)
        self.update_color_preview()

    def on_preset_changed(self, name):
        if name and self.config.load_preset(name):
            self.update_color_preview()

    def save_preset(self):
        if name := QInputDialog.getText(self, "Save Preset", "Enter preset name:")[0]:
            if self.config.save_preset(name):
                self.update_preset_combo(name)

    def delete_preset(self):
        name = self.preset_combo.currentText()
        if name and self.config.delete_preset(name):
            self.update_preset_combo()
            QMessageBox.information(self, "Success", "Preset deleted successfully!")
        elif name:
            QMessageBox.warning(self, "Error", "Cannot delete default presets.")

    def update_preset_combo(self, selected_name=None):
        current = selected_name or self.preset_combo.currentText()
        self.preset_combo.clear()
        self.preset_combo.addItems(self.config.get_preset_names())
        if current in self.config.get_preset_names():
            self.preset_combo.setCurrentText(current)

    def on_color_picked(self, r, g, b, a):
        for section in ("light", "dark"):
            for k, v in zip(("r", "g", "b", "a"), (r, g, b, a)):
                self.config.set_value(section, k, str(v))
        self.update_color_preview()

    def update_color_preview(self):
        effect_key = self.config.get_value("config", "effect", "1")
        is_supported = effect_key not in ("2", "4")
        r, g, b, a = tuple(int(self.config.get_value("light", k)) for k in ("r", "g", "b", "a"))
        self.setEnabled(is_supported)
        self.setToolTip("" if is_supported else "Color selection is not supported for Mica and Mica Alt effects.")
        for child in self.findChildren(QWidget):
            child.setToolTip(self.toolTip())
        self.preview.setEnabled(is_supported)
        self.preview.update_color(r, g, b, a if is_supported else int(a * 0.5))

    def on_effect_changed(self, Checked):
        self.update_color_preview()

    def refresh_from_config(self):
        self.update_color_preview()

class ColorPreview(QPushButton):
    colorSelected = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__(objectName="colorPreview")
        self.setFixedHeight(30)
        self.setFlat(True)
        self.setToolTip("Click to open color picker")
        self.brush_icon = QLabel(self, objectName="BrushIcon")
        self.brush_icon.setFixedSize(20, 20)
        self.brush_icon.move(208, 4)
        self._last_icon_color = None
        self.update_brush_icon((255, 255, 255))
        self.clicked.connect(self.open_color_picker)

    def open_color_picker(self):
        try:
            dialog = QColorDialog(self)
            dialog.setWindowTitle("Choose Color")
            dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
            r, g, b, a = [int(self.parent().config.get_value("light", k)) for k in ("r", "g", "b", "a")]
            dialog.setCurrentColor(QColor(r, g, b, a))
            if dialog.exec() == QColorDialog.DialogCode.Accepted:
                color = dialog.currentColor()
                self.colorSelected.emit(color.red(), color.green(), color.blue(), color.alpha())
        except Exception as e:
            print(f"Error opening color picker: {e}")

    def update_color(self, r, g, b, a):
        self.setStyleSheet(f"#colorPreview {{ background-color: rgba({r}, {g}, {b}, {a}); border-radius: 4px; }}")
        self.update_brush_icon((r, g, b))

    def update_brush_icon(self, rgb):
        icon_color = "rgb(32,32,32)" if sum(c * w for c, w in zip(rgb, (0.299, 0.587, 0.114))) > 128 else "rgb(240,240,240)"
        if self._last_icon_color == icon_color:
            return
        self._last_icon_color = icon_color
        icon_path = Path(__file__).parent / "assets" / "icons" / "brush.svg"
        if icon_path.exists():
            with open(icon_path, encoding="utf-8") as f:
                svg = f.read().replace("{color}", icon_color)
            pixmap = QPixmap()
            pixmap.loadFromData(svg.encode("utf-8"), "SVG")
            self.brush_icon.setPixmap(pixmap.scaled(self.brush_icon.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.ui_elements = {}
        self._icon_buttons = []
        self.setWindowTitle("Settings")
        self.setFixedSize(260, 200)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self, spacing=2, contentsMargins=QMargins(2, 2, 2, 2))
        group = QGroupBox("Compatibility")
        vbox = QVBoxLayout(group)
        cb = QCheckBox("Enable unsupported effects and options", objectName="show_unsupported")
        cb.setFixedHeight(30)
        cb.setChecked(self.config.get_value("gui", "showUnsupported", "false").lower() == "true")
        cb.clicked.connect(self.unsupported_changed)
        vbox.addWidget(cb)
        self.ui_elements["show_unsupported"] = cb
        layout.addWidget(group)
        group = QGroupBox("Advanced")
        form = QFormLayout(group)
        config_row = QWidget()
        config_row.setFixedHeight(30)
        config_layout = QHBoxLayout(config_row, contentsMargins=QMargins(0, 0, 0, 0), spacing=2)
        config_layout.addStretch(1)
        for icon, tooltip, url in [
            ("folder", "Open config directory", str(self.config.get_config_dir())),
            ("file-pen", "Edit config file", str(self.config.get_config_path()))
        ]:
            btn = create_icon_button(icon=icon, tooltip=tooltip, callback=lambda _, u=url: QDesktopServices.openUrl(QUrl.fromLocalFile(u)), icon_only=True)
            config_layout.addWidget(btn)
            self._icon_buttons.append((btn, icon))
        form.addRow("Configuration:", config_row)
        self.log_level_combo = QComboBox()
        self.log_level_combo.setFixedHeight(28)
        self.log_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        self.log_level_combo.setCurrentText(self.config.get_value("gui", "logLevel", "ERROR").upper())
        self.log_level_combo.currentTextChanged.connect(lambda level: self.config.set_value("gui", "logLevel", level.upper()))
        form.addRow("Log Level:", self.log_level_combo)
        layout.addWidget(group)
        layout.addStretch()
        self.reset_btn = create_icon_button("Reset Settings", "undo", "Reset Settings", self.reset_settings, object_name="resetButton")
        self.reset_btn.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        layout.addWidget(self.reset_btn)

    def refresh_ui(self):
        self.ui_elements["show_unsupported"].setChecked(self.config.get_value("gui", "showUnsupported", "false").lower() == "true")
        self.log_level_combo.setCurrentText(self.config.get_value("gui", "logLevel", "ERROR").upper())

    def unsupported_changed(self, checked):
        self.config.set_value("gui", "showUnsupported", str(checked).lower())
        if hasattr(self.parent, "get_component"):
            self.parent.get_component("effects_group").refresh_effects()
            self.parent.get_component("options_group").refresh_options()

    def reset_settings(self):
        if QMessageBox.question(self, "Reset Settings", "Are you sure you want to reset all settings to default?") == QMessageBox.StandardButton.Yes:
            if self.config.reset_to_defaults():
                for name in ["effects_group", "options_group", "presets_colors_group"]:
                    component = self.parent.get_component(name)
                    component.config = self.config
                    component.refresh_from_config()
                self.parent.get_component("effects_group").refresh_effects()
                presets_group = self.parent.get_component("presets_colors_group")
                presets_group.update_presets()
                preset_combo = presets_group.preset_combo
                default_preset = self.config.get_value("gui", "last_preset", "Light Mode")
                preset_combo.setCurrentText(default_preset) if default_preset in self.config.get_preset_names() else preset_combo.setCurrentIndex(0)
                self.refresh_ui()
                QMessageBox.information(self, "Success", "Settings reset successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to reset settings!")

class MainWindow(QMainWindow):
    update_available = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self._ui_components = {}
        self._settings_dialog = None
        self._dll_status_thread = None
        self._is_dll_registered = False
        self.update_available.connect(self.update_dialog)
        self.init_ui()
        QTimer.singleShot(200, self.start_background_tasks)

    def init_ui(self):
        self.setWindowTitle("Mica4U")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget, spacing=2, contentsMargins=QMargins(2, 2, 2, 2))
        for name in ["effects_group", "options_group", "presets_colors_group"]:
            layout.addWidget(self.get_component(name))
        self.get_component("effects_group").effect_changed.connect(self.get_component("presets_colors_group").on_effect_changed)
        action_layout = QHBoxLayout(spacing=2, contentsMargins=QMargins(0, 0, 0, 0))
        self.toggle_btn = create_icon_button(
            text="Register DLL",
            icon="circle-check",
            tooltip="Register DLL To Explorer",
            callback=self.toggle_effects,
            min_width=200,
            object_name="toggleButton"
        )
        action_layout.addWidget(self.toggle_btn)
        settings_btn = create_icon_button(
            text="",
            icon="cog",
            tooltip="Open settings dialog",
            callback=self.open_settings,
            icon_only=True,
            object_name="settingsButton"
        )
        action_layout.addWidget(settings_btn)
        layout.addLayout(action_layout)
        self.setFixedSize(250, 320)
        self.load_selected_effect = self._load_selected_effect_impl
        self.load_selected_effect()

    def start_background_tasks(self):
        if not self._dll_status_thread:
            self._dll_status_thread = DLLStatusThread(self.config)
            self._dll_status_thread.status_updated.connect(self.handle_dll_status)
            self._dll_status_thread.start()
        check_updates = self.config.get_value(
            "gui", "checkForUpdates", fallback="true"
        ).lower()
        if check_updates != "false":
            QTimer.singleShot(0, self.check_for_updates)

    def handle_dll_status(self, is_registered):
        """Handle DLL status updates from DLLStatusThread."""
        self._is_dll_registered = is_registered
        self.update_toggle_button()

    def update_toggle_button(self):
        if self._is_dll_registered:
            self.toggle_btn.setText("Unregister DLL")
            self.toggle_btn.setIcon(get_icon("circle-xmark"))
            self.toggle_btn.setToolTip("Unregister DLL From Explorer")
        else:
            self.toggle_btn.setText("Register DLL")
            self.toggle_btn.setIcon(get_icon("circle-check"))
            self.toggle_btn.setToolTip("Register DLL To Explorer")

    def toggle_effects(self):
        action = "unregister" if self._is_dll_registered else "register"
        self.manage_dll_registration(action)

    def trigger_dll_status_check(self):
        if self._dll_status_thread:
            self._dll_status_thread.force_check()

    def manage_dll_registration(self, action):
        self.dll_registration_thread = DLLRegistrationThread(self.config, action)
        self.dll_registration_thread.finished.connect(self.trigger_dll_status_check)
        self.dll_registration_thread.start()

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
            if tuple(map(int, latest.split("."))) > tuple(map(int, CONSTANTS['VERSION'].split("."))):
                self.update_available.emit(latest)
        except Exception:
            pass

    def update_dialog(self, latest_version):
        log_message("info", f"Showing update dialog for version v{latest_version}")
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Update Available")
            msg.setText(
                f"A new version of Mica4U is available: v{latest_version}\n\nYou are running v{CONSTANTS['VERSION']}."
            )
            msg.setStandardButtons(
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open
            )
            msg.button(QMessageBox.StandardButton.Open).setText("Open Releases Page")
            ret = msg.exec()
            if ret == QMessageBox.StandardButton.Open:
                log_message("info", "User clicked 'Open Releases Page'")
                QDesktopServices.openUrl(
                    QUrl("https://github.com/DrkCtrlDev/Mica4U/releases")
                )
            else:
                log_message("info", "User dismissed update dialog")
        except Exception as e:
            log_message("error", f"Failed to show update dialog: {e}")

    def get_component(self, name):
        if name not in self._ui_components:
            self._ui_components[name] = {
                "effects_group": EffectGroup,
                "options_group": OptionsGroup,
                "presets_colors_group": PresetsColorsGroup
            }[name](self.config)
        return self._ui_components[name]
    
    def closeEvent(self, event):
        if self._dll_status_thread:
            self._dll_status_thread.stop()
            self._dll_status_thread.wait(500)
        super().closeEvent(event)

    def _load_selected_effect_impl(self):
        effect = self.config.get_value("config", "effect", "1")
        if effect in self.get_component("effects_group").radio_buttons:
            self.get_component("effects_group").radio_buttons[effect].setChecked(True)

    def open_settings(self):
        if not self._settings_dialog:
            self._settings_dialog = SettingsDialog(self.config, self)
        self._settings_dialog.refresh_ui()
        self._settings_dialog.exec()

class DLLRegistrationThread(QThread):
    status = pyqtSignal(str, bool)

    def __init__(self, config, action):
        super().__init__()
        self.config = config
        self.action = action

    def run(self):
        dll_path = self.config.get_dll_path()
        if not dll_path.exists():
            self.status.emit(f"DLL not found: {dll_path}", False)
            return
        try:
            cmd = f'regsvr32 {" /u" if self.action == "unregister" else ""} /s "{dll_path}"'
            result = subprocess.run(
                f'powershell -Command "Start-Process cmd -ArgumentList \'/c {cmd}\' -Verb RunAs"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                self.status.emit(f"regsvr32 failed: {result.stderr}", False)
                return
            subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            time.sleep(2)
            subprocess.run("start explorer.exe", shell=True, capture_output=True)
            self.status.emit(f"DLL {'unregistered' if self.action == 'unregister' else 'registered'} successfully", True)
        except Exception as e:
            self.status.emit(f"Exception: {e}", False)

class DLLStatusThread(QThread):
    status_updated = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True
        self.check_interval = 8192
        self._force_check = False

    def run(self):
        while self.running:
            try:
                status = check_dll_registered(self.config)
                self.status_updated.emit(status)
                log_message("info", f"DLL status thread check: {status}")
                waited = 0
                while waited < self.check_interval and self.running and not self._force_check:
                    self.msleep(100)
                    waited += 100
                self._force_check = False
            except Exception as e:
                log_message("error", f"Error in DLL status thread: {e}")
                self.msleep(self.check_interval)

    def force_check(self):
        self._force_check = True

    def stop(self):
        self.running = False
        self.wait()

def main():
    atexit.register(cleanup_temp)
    app = QApplication(sys.argv)
    config = ConfigManager()
    window = MainWindow()
    window.setWindowIcon(QIcon(str(Path(__file__).parent / "icon.ico")))
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
