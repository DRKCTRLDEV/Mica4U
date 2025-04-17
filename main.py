import sys
import os
import json
import logging
import subprocess
import atexit
import urllib.request
import shutil
import tempfile
import ctypes
import platform
import psutil
import winreg
import time
import re
import webbrowser
from pathlib import Path
from functools import wraps
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QRadioButton,
    QCheckBox,
    QLabel,
    QSlider,
    QPushButton,
    QFrame,
    QComboBox,
    QGridLayout,
    QDialog,
    QMessageBox,
    QInputDialog,
    QButtonGroup,
    QColorDialog,
    QTextBrowser,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QDesktopServices, QColor
import qtawesome as qta


def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper


class ClickableLabel(QLabel):
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


VERSION = "1.6.7"
STANDARD_HEIGHT = 30
STANDARD_SPACING = 5

DEFAULT_CONFIG = {
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
        "showEffectPreview": "true",
        "last_preset": "Light Mode",
        "showUnsupportedOptions": "false",
        "logLevel": "Info",
        "checkUpdatesOnStartup": "true"
    },
}

DEFAULT_PRESETS = {
    "Light Mode": {"r": "220", "g": "220", "b": "220", "a": "160"},
    "Dark Mode": {"r": "0", "g": "0", "b": "0", "a": "120"},
}

STYLE_EFFECTS = [
    ("Blur", "0", "Windows 10/11 Blur effect", lambda v: True, ""),
    (
        "Acrylic",
        "1",
        "Windows 10 Acrylic effect",
        lambda v: v["is_win10"] or v["is_win11"],
        "Requires Windows 10 or Windows 11",
    ),
    (
        "Mica",
        "2",
        "Windows 11 Mica effect",
        lambda v: v["is_win11"],
        "Requires Windows 11",
    ),
    (
        "Blur (Clear)",
        "3",
        "Clean blur without noise (Windows 10/11 up to 22H2)",
        lambda v: v["is_win10"] or (v["is_win11"] and v["build_num"] <= 22621),
        "Requires Windows 10 or Windows 11 up to 22H2",
    ),
    (
        "Mica Alt",
        "4",
        "Alternative system colors",
        lambda v: v["is_win11"],
        "Requires Windows 11",
    ),
]


class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        portable_mode = Path("portable.ini").exists()
        logs_dir = (
            (
                Path(sys.executable).parent
                if getattr(sys, "frozen", False)
                else Path(__file__).parent
            )
            / "logs"
            if portable_mode
            else Path(os.getenv("APPDATA", "")) / "Mica4U" / "logs"
        )
        logs_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("Mica4U")
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(logs_dir / "mica4u.log", encoding="utf-8")
        console_handler = logging.StreamHandler(sys.stdout)

        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.handlers = {"file": file_handler, "console": console_handler}

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=True):
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=True):
        self.logger.critical(message, exc_info=exc_info)

    def set_level(self, level):
        try:
            if isinstance(level, str):
                level = getattr(logging, level.upper())
            self.logger.setLevel(level)
            for handler in self.handlers.values():
                handler.setLevel(level)
            logger.debug(f"Log level changed to: {logging.getLevelName(level)}")
        except Exception as e:
            logger.error(f"Error changing log level: {str(e)}")
            raise


logger = Logger()


def resource_path(relative_path):
    try:
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = Path(__file__).parent
        return str(Path(base_path) / relative_path)
    except Exception as e:
        logger.error(f"Error getting resource path: {str(e)}")
        return str(Path(relative_path))


def cleanup_temp():
    temp_dir = tempfile._get_default_tempdir()
    for filename in os.listdir(temp_dir):
        if filename.startswith("_MEI"):
            try:
                filepath = os.path.join(temp_dir, filename)
                if os.path.isdir(filepath):
                    logger.debug(f"Cleaning up temp directory: {filepath}")
                    shutil.rmtree(filepath, ignore_errors=True)
            except Exception as e:
                logger.warning(
                    f"Failed to clean up temp directory {filepath}: {str(e)}"
                )


def get_windows_version():
    ver = platform.version().split(".")
    version_tuple = (int(ver[0]), int(ver[1]), int(ver[2]))
    logger.debug(f"Windows version detected: {version_tuple}")
    return version_tuple


def check_file_permissions(path):
    test_file = Path(path) / ".permission_test"
    try:
        test_file.touch(exist_ok=True)
        test_file.unlink()
        return True
    except Exception as e:
        logger.warning(f"No write permissions for {path}: {str(e)}")
        return False


def download_font_awesome():
    font_path = Path("fontawesome-webfont.ttf")
    if not font_path.exists():
        logger.info("Downloading Font Awesome...")
        url = "https://github.com/FortAwesome/Font-Awesome/raw/master/fonts/fontawesome-webfont.ttf"
        urllib.request.urlretrieve(url, font_path)
        logger.info("Font Awesome downloaded successfully")
    return str(font_path)


class ConfigManager:
    def __init__(self):
        self.portable_mode = Path("portable.ini").exists()
        if self.portable_mode:
            self.config_dir = (
                Path(sys.executable).parent
                if getattr(sys, "frozen", False)
                else Path(__file__).parent
            )
            self.requirements_dir = self.config_dir / "requirements"
        else:
            self.config_dir = Path(os.getenv("APPDATA", "")) / "Mica4U"
            self.requirements_dir = self.config_dir
            self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_path = self.config_dir / "config.ini"
        self.dll_path = self.requirements_dir / "ExplorerBlurMica.dll"
        self.init_path = self.requirements_dir / "Initialise.cmd"

        if self.portable_mode:
            self.requirements_dir.mkdir(parents=True, exist_ok=True)
        self.setup_required_files()

        self._config_cache = None
        self._presets_cache = None
        self.config = {}
        self.presets = DEFAULT_PRESETS.copy()
        self._initializing = True
        self._save_timer = None
        self.load_config()
        self._initializing = False

        last_preset = self.get_value("gui", "last_preset", fallback=None)
        if last_preset and last_preset in self.presets:
            self.load_preset(last_preset)

    def setup_required_files(self):
        if not check_file_permissions(str(self.config_dir)):
            raise PermissionError(f"No write permissions for {self.config_dir}")

        base_path = (
            Path(sys._MEIPASS)
            if getattr(sys, "frozen", False)
            else Path(__file__).parent
        )
        self._copy_file_with_retry(
            base_path / "requirements" / "ExplorerBlurMica.dll",
            self.dll_path,
            "DLL file",
        )

        if not self.init_path.exists():
            logger.info(f"Copying initialization script to {self.init_path}")
            shutil.copy2(base_path / "requirements" / "Initialise.cmd", self.init_path)

        if not self.config_path.exists():
            logger.info("Creating default configuration file")
            self.create_default_config()

    def _copy_file_with_retry(self, source, destination, file_type, max_retries=3):
        if destination.exists():
            return

        for attempt in range(max_retries):
            try:
                logger.info(f"Copying {file_type} to {destination}")
                shutil.copy2(source, destination)
                return
            except PermissionError as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Permission error copying {file_type}, attempt {attempt + 1}: {str(e)}"
                    )
                    time.sleep(1)
                else:
                    raise

    def create_default_config(self):
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
showEffectPreview = true
last_preset = Light Mode
showUnsupportedOptions = false
logLevel = Info
checkUpdatesOnStartup = true

[presets]
Light Mode = {
    "r": "220",
    "g": "220",
    "b": "220",
    "a": "160"
}
Dark Mode = {
    "r": "0",
    "g": "0",
    "b": "0",
    "a": "120"
}"""
            )
        logger.info("Default configuration file created successfully")

    def load_config(self):
        if not self.config_path.exists():
            logger.info("Configuration file not found, creating default")
            self.create_default_config()
            self.config = DEFAULT_CONFIG.copy()
            self._config_cache = self.config.copy()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                content = f.read()

            main_config, _, presets_section = content.partition("[presets]")

            self.config = {}
            current_section = None
            for line in main_config.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                    self.config[current_section] = {}
                elif current_section and "=" in line:
                    key, value = line.split("=", 1)
                    self.config[current_section][key.strip()] = value.strip()

            if presets_section:
                self._parse_presets(presets_section)

            self._config_cache = self.config.copy()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            self.config = DEFAULT_CONFIG.copy()
            self._config_cache = self.config.copy()

    def _parse_presets(self, presets_section):
        try:
            preset_lines = presets_section.strip().split("\n")[1:]
            current_preset, preset_data = None, ""

            for line in preset_lines:
                if "=" in line and not current_preset:
                    name, data = line.split("=", 1)
                    current_preset, preset_data = name.strip(), data.strip()
                elif current_preset:
                    preset_data += line
                    if line.strip() == "}":
                        try:
                            self.presets[current_preset] = json.loads(preset_data)
                            current_preset, preset_data = None, ""
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Error parsing preset {current_preset}: {str(e)}"
                            )
        except Exception as e:
            logger.error(f"Error parsing presets section: {str(e)}")

    def save_config(self, skip_cache=False):
        if self._initializing and self.config_path.exists():
            return

        sections = {
            "config": [
                "effect",
                "clearAddress",
                "clearBarBg",
                "clearWinUIBg",
                "showLine",
            ],
            "light": ["r", "g", "b", "a"],
            "dark": ["r", "g", "b", "a"],
            "gui": [
                "showUnsupportedEffects",
                "showEffectPreview",
                "last_preset",
                "showUnsupportedOptions",
                "logLevel",
                "checkUpdatesOnStartup"
            ],
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                for section, keys in sections.items():
                    f.write(f"[{section}]\n")
                    for key in keys:
                        value = self.config.get(section, {}).get(
                            key, DEFAULT_CONFIG.get(section, {}).get(key, "")
                        )
                        f.write(f"{key} = {value}\n")
                    f.write("\n")

                f.write("[presets]\n")
                for preset_name, preset_data in self.presets.items():
                    f.write(f"{preset_name} = {{\n")
                    for i, (key, value) in enumerate(preset_data.items()):
                        f.write(f'    "{key}": "{value}"')
                        if i < len(preset_data) - 1:
                            f.write(",")
                        f.write("\n")
                    f.write("}\n")

            self._config_cache = self.config.copy()
            if not self._initializing:
                logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")

    def _delayed_save(self):
        self.save_config(skip_cache=True)
        self._save_timer = None

    def get_value(self, section, key, default=None, fallback=None):
        try:
            return self.config[section][key]
        except KeyError:
            if fallback is not None:
                return fallback
            if (
                default is None
                and section in DEFAULT_CONFIG
                and key in DEFAULT_CONFIG[section]
            ):
                return DEFAULT_CONFIG[section][key]
            return default

    def set_value(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)

        if not self._initializing:
            if self._save_timer is None:
                self._save_timer = QTimer()
                self._save_timer.setSingleShot(True)
                self._save_timer.timeout.connect(self._delayed_save)
            self._save_timer.start(500)
        logger.debug(f"Set config value: [{section}][{key}] = {value}")

    def get_preset_names(self):
        return list(self.presets.keys())

    def get_preset(self, name):
        return self.presets.get(name)

    def add_preset(self, name, values):
        self.presets[name] = values
        self.save_config()
        logger.info(f"Added new preset: {name}")

    def save_preset(self, name):
        preset_data = {
            "r": self.get_value("light", "r"),
            "g": self.get_value("light", "g"),
            "b": self.get_value("light", "b"),
            "a": self.get_value("light", "a"),
        }

        self.presets[name] = preset_data
        self.save_config(skip_cache=True)
        logger.info(f"Preset saved: {name}")
        return True

    def delete_preset(self, name):
        if name in self.presets and name not in ["Light Mode", "Dark Mode"]:
            del self.presets[name]
            self.save_config()
            return True
        return False

    def load_preset(self, name):
        if name in self.presets:
            preset = self.presets[name]
            for key, value in preset.items():
                self.set_value("light", key, value)
            self.set_value("gui", "last_preset", name)
            return True
        return False

    def update_presets(self):
        try:
            current = self.preset_combo.currentText()
            self.preset_combo.clear()
            self.preset_combo.addItems(self.get_preset_names())
            if current and current in self.get_preset_names():
                index = self.preset_combo.findText(current)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
            logger.debug("Presets updated successfully")
        except Exception as e:
            logger.error(f"Error updating presets: {str(e)}")
            raise

    def reset_to_defaults(self):
        try:
            self.config = DEFAULT_CONFIG.copy()
            self.presets = DEFAULT_PRESETS.copy()
            self.save_config(skip_cache=True)
            logger.info("Settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting settings to defaults: {str(e)}")
            return False

    def get_dll_path(self):
        return self.dll_path

    def get_init_path(self):
        return self.init_path


class BaseGroup(QGroupBox):
    def __init__(self, title, config):
        super().__init__(title)
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout())
        logger.debug(f"Base group {self.title()} initialized")


class StyleGroup(BaseGroup):
    effect_changed = pyqtSignal(bool)

    def __init__(self, config):
        self.radio_buttons = {}
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        super().__init__("Style", config)

    def init_ui(self):
        super().init_ui()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)

        effects = [
            ("0", "Blur", "Windows 10/11 Blur effect"),
            ("1", "Acrylic", "Windows 10 Acrylic effect"),
            ("2", "Mica", "Windows 11 Mica effect"),
            (
                "3",
                "Blur (Clear)",
                "Clean blur without noise (Windows 10/11 up to 22H2)",
            ),
            ("4", "Mica Alt", "Alternative system colors"),
        ]

        self.radio_layout = QGridLayout()
        self.radio_layout.setSpacing(5)
        self.radio_layout.setContentsMargins(0, 0, 0, 0)

        for i, (effect_key, effect_name, tooltip) in enumerate(effects):
            radio = QRadioButton(effect_name)
            radio.setFixedHeight(STANDARD_HEIGHT - 5)
            radio.setChecked(self.config.get_value("config", "effect") == effect_key)
            radio.clicked.connect(
                lambda checked, key=effect_key: self.on_effect_changed(key)
            )
            radio.setToolTip(tooltip)
            self.radio_buttons[effect_key] = radio
            self.button_group.addButton(radio)
            self.radio_layout.addWidget(radio, i // 2, i % 2)

        main_layout.addLayout(self.radio_layout)

        self.layout().addLayout(main_layout)
        self.refresh_effects()
        logger.debug("Style group initialized")

    def refresh_effects(self):
        show_unsupported = (
            self.config.get_value(
                "gui", "showUnsupportedEffects", fallback="false"
            ).lower()
            == "true"
        )

        win_ver = get_windows_version()
        major_ver = win_ver[0]
        build_num = win_ver[2]
        is_win11 = major_ver == 10 and build_num >= 22000
        is_win10 = major_ver == 10 and build_num < 22000

        for effect_key, radio in self.radio_buttons.items():
            is_supported = False
            tooltip = radio.toolTip()

            if effect_key == "0":
                is_supported = is_win10 or is_win11
            elif effect_key == "1":
                is_supported = is_win10 or is_win11
                if not is_supported:
                    tooltip += " (Incompatible with system)"
            elif effect_key == "2":
                is_supported = is_win11
                if not is_supported:
                    tooltip += " (Incompatible with system)"
            elif effect_key == "3":
                is_supported = (is_win10 and build_num < 19045) or (is_win11 and build_num <= 22621)
                if not is_supported:
                    tooltip += " (Incompatible with system)"
            elif effect_key == "4":
                is_supported = is_win11
                if not is_supported:
                    tooltip += " (Incompatible with system)"

            radio.setEnabled(is_supported or show_unsupported)
            radio.setToolTip(tooltip)
            radio.setStyleSheet("QRadioButton:disabled {color: #808080;}")

        QTimer.singleShot(0, self.updateGeometry)
        logger.debug(
            f"Effects refreshed. WinVer: {win_ver}, IsWin11: {is_win11}, IsWin10: {is_win10}, ShowUnsupported: {show_unsupported}"
        )

    def on_effect_changed(self, effect_key):
        self.config.set_value("config", "effect", effect_key)
        is_mica_effect = effect_key in ["2", "4"]

        self.effect_changed.emit(is_mica_effect)
        logger.debug(f"Effect changed to: {effect_key}")


class OptionsGroup(BaseGroup):
    def __init__(self, config):
        self.checkboxes = {}
        super().__init__("Options", config)

    def init_ui(self):
        super().init_ui()
        options = [
            (
                "Clear Address Bar",
                "clearAddress",
                "Clear the background of the address bar.",
                False,
            ),
            (
                "Clear Scrollbar Bg",
                "clearBarBg",
                "Clear the background color of the scrollbar (May differ from system style).",
                True,
            ),
            (
                "Clear WinUI Bg",
                "clearWinUIBg",
                "Remove toolbar background color (Win11 WinUI/XamlIslands only).",
                True,
            ),
            (
                "Show Separator",
                "showLine",
                "Show split line between TreeView and DUIView.",
                False,
            ),
        ]

        for text, key, tooltip, is_experimental in options:
            cb_text = f"{text} (Experimental)" if is_experimental else text
            cb = QCheckBox(cb_text)
            cb.setFixedHeight(STANDARD_HEIGHT - 5)
            cb.setChecked(self.config.get_value("config", key) == "true")
            cb.clicked.connect(
                lambda checked, k=key: self.config.set_value(
                    "config", k, str(checked).lower()
                )
            )
            cb.setToolTip(tooltip)
            self.checkboxes[key] = cb
            self.layout().addWidget(cb)

        self.layout().setSpacing(5)
        self.refresh_options()
        logger.debug("Options group initialized")

    def refresh_options(self):
        show_unsupported = (
            self.config.get_value(
                "gui", "showUnsupportedOptions", fallback="false"
            ).lower()
            == "true"
        )

        win_ver = get_windows_version()
        is_win11 = win_ver[0] == 10 and win_ver[2] >= 22000

        winui_cb = self.checkboxes.get("clearWinUIBg")
        if winui_cb:
            is_supported = is_win11
            winui_cb.setEnabled(is_supported or show_unsupported)
            if not is_supported:
                winui_cb.setToolTip(winui_cb.toolTip() + " (Incompatible with system)")
            winui_cb.setStyleSheet("QCheckBox:disabled { color: #808080; }")

        self.updateGeometry()
        logger.debug(
            f"Options refreshed. IsWin11: {is_win11}, ShowUnsupported: {show_unsupported}"
        )

    def refresh_from_config(self):
        for key, checkbox in self.checkboxes.items():
            checkbox.setChecked(self.config.get_value("config", key) == "true")
        logger.debug("Options refreshed from configuration")


class PresetGroup(BaseGroup):
    def __init__(self, config, colors_group):
        super().__init__("Presets", config)
        self.colors_group = colors_group

    def init_ui(self):
        super().init_ui()

        layout = QHBoxLayout()
        layout.setSpacing(5)

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
        layout.addWidget(self.preset_combo, stretch=1)

        theme = get_system_theme()
        icon_color = get_icon_color(theme)

        button_configs = [
            (
                "save_btn",
                "fa5s.save",
                "Save current settings as preset",
                self.save_preset,
            ),
            ("delete_btn", "fa5s.trash", "Delete selected preset", self.delete_preset),
        ]

        for attr_name, icon_name, tooltip, callback in button_configs:
            btn = QPushButton()
            btn.setFixedSize(STANDARD_HEIGHT, STANDARD_HEIGHT)
            btn.setIcon(qta.icon(icon_name, color=icon_color))
            btn.setToolTip(tooltip)
            btn.setObjectName(attr_name.replace("_", "") + "Button")
            btn.setProperty("iconOnly", "true")
            btn.clicked.connect(callback)
            setattr(self, attr_name, btn)
            layout.addWidget(btn)

        self.layout().addLayout(layout)
        logger.debug("Preset group initialized")

    def on_preset_changed(self, name):
        if name and self.config.load_preset(name):
            self.colors_group.refresh_from_config()
            self.config.set_value("gui", "last_preset", name)
            logger.debug(f"Preset changed to: {name}")

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
                logger.info(f"Preset deleted: {name}")
            else:
                QMessageBox.warning(self, "Error", "Cannot delete default presets.")
                logger.warning(f"Attempted to delete default preset: {name}")

    def update_presets(self):
        current = self.preset_combo.currentText()
        self.preset_combo.clear()
        self.preset_combo.addItems(self.config.get_preset_names())
        if current and current in self.config.get_preset_names():
            index = self.preset_combo.findText(current)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
        logger.debug("Presets updated successfully")

    def on_effect_changed(self, is_mica_effect):
        self.preset_combo.setEnabled(not is_mica_effect)
        self.save_btn.setEnabled(not is_mica_effect)
        self.delete_btn.setEnabled(not is_mica_effect)
        logger.debug(
            f"Preset controls {'disabled' if is_mica_effect else 'enabled'} for Mica effect"
        )


class ColorPreview(QFrame):
    colorSelected = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setFixedHeight(STANDARD_HEIGHT)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("colorPreview")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Double-click to open color picker")

    def mouseDoubleClickEvent(self, event):
        try:
            self.open_color_picker()
            super().mouseDoubleClickEvent(event)
        except Exception as e:
            logger.error(f"Error in color picker: {str(e)}")

    def open_color_picker(self):
        try:
            style = self.styleSheet()
            rgba_match = None
            if "rgba" in style:
                import re

                rgba_match = re.search(
                    r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", style
                )

            current_r, current_g, current_b = 255, 255, 255
            current_a = 128

            if rgba_match:
                current_r = int(rgba_match.group(1))
                current_g = int(rgba_match.group(2))
                current_b = int(rgba_match.group(3))
                current_a = int(rgba_match.group(4))

            color_dialog = QColorDialog(self)
            color_dialog.setWindowTitle("Choose Color")
            color_dialog.setOption(
                QColorDialog.ColorDialogOption.ShowAlphaChannel, True
            )
            color_dialog.setCurrentColor(
                QColor(current_r, current_g, current_b, current_a)
            )

            if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
                selected_color = color_dialog.currentColor()
                r, g, b, a = (
                    selected_color.red(),
                    selected_color.green(),
                    selected_color.blue(),
                    selected_color.alpha(),
                )
                self.colorSelected.emit(r, g, b, a)
                logger.debug(f"Color selected from picker: rgba({r}, {g}, {b}, {a})")
        except Exception as e:
            logger.error(f"Error opening color picker: {str(e)}")

    def update_color(self, r, g, b, a):
        self.setStyleSheet(
            f"#colorPreview {{ background-color: rgba({r}, {g}, {b}, {a}); border-radius: 5px; }}"
        )
        self.update()
        logger.debug(
            f"Color preview updated to rgba({r}, {g}, {b}, {a}) with rounded corners"
        )


class ColorsGroup(BaseGroup):
    def __init__(self, config):
        self.sliders = {}
        self.value_labels = {}
        self.color_labels = {}
        self.preview = ColorPreview()
        self.preview.colorSelected.connect(self.on_color_picked)
        self._update_timer = None
        self._debounce_time = 100
        super().__init__("Colors", config)

        show_preview = (
            self.config.get_value("gui", "showEffectPreview", fallback="true").lower()
            == "true"
        )
        self.preview.setVisible(show_preview)

    def on_color_picked(self, r, g, b, a):
        try:
            color_keys = {"r": r, "g": g, "b": b, "a": a}
            for key, value in color_keys.items():
                if key in self.sliders:
                    self.sliders[key].setValue(value)

            for color_key in ["r", "g", "b", "a"]:
                value = self.sliders[color_key].value()
                self.config.set_value("light", color_key, str(value))
                self.config.set_value("dark", color_key, str(value))

            self.update_color_preview()
            logger.debug(f"Updated sliders from color picker: rgba({r}, {g}, {b}, {a})")
        except Exception as e:
            logger.error(f"Error updating sliders from color picker: {str(e)}")
            raise

    def init_ui(self):
        super().init_ui()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

        color_configs = [
            ("r", "R", "red"),
            ("g", "G", "green"),
            ("b", "B", "blue"),
            ("a", "A", None),
        ]

        for color_key, label_text, label_color in color_configs:
            main_layout.addLayout(
                self._create_color_row(color_key, label_text, label_color)
            )

        main_layout.addWidget(self.preview)
        self.layout().addLayout(main_layout)

        self.update_color_preview()
        logger.debug("Colors group initialized")

    def _create_color_row(self, color_key, label_text, label_color=None):
        row_layout = QHBoxLayout()
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row_layout.setSpacing(5)

        label = QLabel()
        if label_color:
            label.setText(f'<font color="{label_color}">{label_text}</font>')
        else:
            label.setText(label_text)

        label.setFixedHeight(STANDARD_HEIGHT)
        label.setMinimumWidth(20)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_labels[color_key] = label

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setFixedHeight(STANDARD_HEIGHT)
        slider.setRange(0, 255)
        slider.setValue(int(self.config.get_value("light", color_key)))
        slider.valueChanged.connect(
            lambda value, ck=color_key: self._on_slider_changed(ck, value)
        )
        self.sliders[color_key] = slider

        value_label = ClickableLabel(str(slider.value()))
        value_label.setFixedHeight(STANDARD_HEIGHT)
        value_label.setMinimumWidth(30)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setToolTip(f"Double-click to set {label_text} value")
        value_label.doubleClicked.connect(
            lambda ck=color_key: self._handle_label_double_click(ck)
        )
        self.value_labels[color_key] = value_label

        row_layout.addWidget(label)
        row_layout.addWidget(slider)
        row_layout.addWidget(value_label)
        return row_layout

    def _on_slider_changed(self, color_key, value):
        self.value_labels[color_key].setText(str(value))

        if self._update_timer is None:
            self._update_timer = QTimer()
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self._delayed_update)
        self._update_timer.start(self._debounce_time)

        logger.debug(f"Color {color_key} slider moved to {value}")

    def _handle_label_double_click(self, color_key):
        slider = self.sliders.get(color_key)
        if not slider:
            return

        current_value = slider.value()
        max_value = slider.maximum()
        min_value = slider.minimum()
        label_text = {"r": "Red", "g": "Green", "b": "Blue", "a": "Alpha"}.get(
            color_key, "Value"
        )

        new_value, ok = QInputDialog.getInt(
            self,
            f"Set {label_text}",
            f"Enter new value for {label_text} ({min_value}-{max_value}):",
            current_value,
            min_value,
            max_value,
            1,
        )

        if ok and new_value != current_value:
            slider.setValue(new_value)
            logger.debug(f"Set {color_key} value to {new_value} via label double-click")

    def _delayed_update(self):
        try:
            for color_key in ["r", "g", "b", "a"]:
                value = self.sliders[color_key].value()
                self.config.set_value("light", color_key, str(value))
                self.config.set_value("dark", color_key, str(value))

            self.update_color_preview()
            self._update_timer = None
        except Exception as e:
            logger.error(f"Error in delayed update: {str(e)}")
            raise

    def update_color_preview(self):
        try:
            r = int(self.config.get_value("light", "r"))
            g = int(self.config.get_value("light", "g"))
            b = int(self.config.get_value("light", "b"))
            a = int(self.config.get_value("light", "a"))
            self.preview.update_color(r, g, b, a)
            logger.debug(f"Color preview updated to rgba({r}, {g}, {b}, {a})")
        except Exception as e:
            logger.error(f"Error updating color preview: {str(e)}")
            raise

    def refresh_from_config(self):
        try:
            for color_key in ["r", "g", "b", "a"]:
                value = int(self.config.get_value("light", color_key))
                self.sliders[color_key].setValue(value)
                self.value_labels[color_key].setText(str(value))

            self.update_color_preview()
            logger.debug("Colors refreshed from configuration")
        except Exception as e:
            logger.error(f"Error refreshing colors from configuration: {str(e)}")
            raise

    def set_preview_visible(self, visible):
        try:
            self.preview.setVisible(visible)
            logger.debug(f"Color preview visibility set to: {visible}")
        except Exception as e:
            logger.error(f"Error setting preview visibility: {str(e)}")
            raise

    def on_effect_changed(self, is_mica_effect):
        try:
            for slider in self.sliders.values():
                slider.setEnabled(not is_mica_effect)
            for label in self.value_labels.values():
                label.setEnabled(not is_mica_effect)

            for key, label in self.color_labels.items():
                label.setEnabled(not is_mica_effect)
                label_text = key.upper()

                if is_mica_effect:
                    label.setText(label_text)
                else:
                    if key == "r":
                        label.setText('<font color="red">R</font>')
                    elif key == "g":
                        label.setText('<font color="green">G</font>')
                    elif key == "b":
                        label.setText('<font color="blue">B</font>')
                    else:
                        label.setText("A")

            if is_mica_effect:
                self.preview.setStyleSheet(
                    "#colorPreview {"
                    " background-color: rgba(128, 128, 128, 0.5);"
                    " border-radius: 5px;"
                    "}"
                )
            else:
                show_preview = (
                    self.config.get_value(
                        "gui", "showEffectPreview", fallback="true"
                    ).lower()
                    == "true"
                )
                self.preview.setVisible(show_preview)
                if show_preview:
                    self.update_color_preview()

            logger.debug(
                f"Color controls {'disabled' if is_mica_effect else 'enabled'} for Mica effect"
            )
        except Exception as e:
            logger.error(f"Error updating color controls for effect change: {str(e)}")
            raise


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.original_height = parent.height() if parent else 600
        self.ui_elements = {}
        try:
            self.init_ui()
            logger.debug("Settings dialog initialized")
        except Exception as e:
            logger.error(f"Error initializing settings dialog: {str(e)}")
            raise

    def init_ui(self):
        try:
            self.setWindowTitle("Settings")
            self.setMinimumWidth(400)
            layout = QVBoxLayout(self)
            layout.setSpacing(5)

            effects_group = self._create_effects_group()
            layout.addWidget(effects_group)

            advanced_group = self._create_advanced_group()
            layout.addWidget(advanced_group)

            credits_group = self._create_about_group()
            layout.addWidget(credits_group)

            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)

            theme = get_system_theme()
            icon_color = get_icon_color(theme)

            reset_btn = QPushButton()
            reset_btn.setFixedSize(STANDARD_HEIGHT, STANDARD_HEIGHT)
            reset_btn.setIcon(qta.icon("fa5s.undo", color=icon_color))
            reset_btn.setToolTip("Reset Settings")
            reset_btn.setObjectName("resetButton")
            reset_btn.setProperty("iconOnly", "true")
            reset_btn.clicked.connect(self.on_reset_settings)
            button_layout.addWidget(reset_btn)

            check_now_btn = QPushButton()
            check_now_btn.setFixedSize(STANDARD_HEIGHT, STANDARD_HEIGHT)
            check_now_btn.setIcon(qta.icon("fa5s.sync", color=icon_color))
            check_now_btn.setToolTip("Check for Updates")
            check_now_btn.setObjectName("checkNowButton")
            check_now_btn.setProperty("iconOnly", "true")
            check_now_btn.clicked.connect(self.check_for_updates)
            button_layout.addWidget(check_now_btn)

            button_layout.addStretch()

            close_btn = QPushButton("Close")
            close_btn.setFixedHeight(STANDARD_HEIGHT)
            close_btn.clicked.connect(self.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)
            logger.debug("Settings dialog UI initialized")
        except Exception as e:
            logger.error(f"Error initializing settings dialog UI: {str(e)}")
            raise

    def _create_effects_group(self):
        effects_group = QGroupBox("Effects")
        effects_layout = QVBoxLayout()
        effects_layout.setSpacing(5)

        show_unsupported = QCheckBox("Enable unsupported effects")
        show_unsupported.setFixedHeight(STANDARD_HEIGHT)
        show_unsupported.setObjectName("show_unsupported")
        show_unsupported.setChecked(
            self.config.get_value("gui", "showUnsupportedEffects").lower() == "true"
        )
        show_unsupported.clicked.connect(
            lambda checked: self.on_show_unsupported_changed(checked)
        )
        effects_layout.addWidget(show_unsupported)
        self.ui_elements["show_unsupported"] = show_unsupported

        show_unsupported_options = QCheckBox("Enable unsupported options")
        show_unsupported_options.setFixedHeight(STANDARD_HEIGHT)
        show_unsupported_options.setObjectName("show_unsupported_options")
        show_unsupported_options.setChecked(
            self.config.get_value(
                "gui", "showUnsupportedOptions", fallback="false"
            ).lower()
            == "true"
        )
        show_unsupported_options.clicked.connect(
            lambda checked: self.on_show_unsupported_options_changed(checked)
        )
        effects_layout.addWidget(show_unsupported_options)
        self.ui_elements["show_unsupported_options"] = show_unsupported_options

        self.show_preview = QCheckBox("Show effect preview")
        self.show_preview.setFixedHeight(STANDARD_HEIGHT)
        self.show_preview.setObjectName("show_preview")
        self.show_preview.setChecked(
            self.config.get_value("gui", "showEffectPreview", fallback="true").lower()
            == "true"
        )
        self.show_preview.clicked.connect(self.on_show_preview_changed)
        effects_layout.addWidget(self.show_preview)
        self.ui_elements["show_preview"] = self.show_preview

        effects_group.setLayout(effects_layout)
        return effects_group

    def _create_advanced_group(self):
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(5)

        LABEL_WIDTH = 120

        updates_layout = QHBoxLayout()
        updates_label = QLabel("Updates:")
        updates_label.setFixedHeight(STANDARD_HEIGHT)
        updates_label.setFixedWidth(LABEL_WIDTH)
        updates_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        updates_layout.addWidget(updates_label)

        updates_layout.addStretch()

        check_updates = QCheckBox("Check for updates on startup")
        check_updates.setFixedHeight(STANDARD_HEIGHT)
        check_updates.setObjectName("check_updates")
        check_updates.setChecked(
            self.config.get_value("gui", "checkUpdatesOnStartup", fallback="true").lower()
            == "true"
        )
        check_updates.clicked.connect(
            lambda checked: self.config.set_value("gui", "checkUpdatesOnStartup", str(checked).lower())
        )
        updates_layout.addWidget(check_updates)
        advanced_layout.addLayout(updates_layout)
        self.ui_elements["check_updates"] = check_updates

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        advanced_layout.addWidget(separator)

        log_level_layout = QHBoxLayout()
        log_level_label = QLabel("Logging Level:")
        log_level_label.setFixedHeight(STANDARD_HEIGHT)
        log_level_label.setFixedWidth(LABEL_WIDTH)
        log_level_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        log_level_layout.addWidget(log_level_label)

        log_level_layout.addStretch()

        log_level_combo = QComboBox()
        log_level_combo.setFixedHeight(STANDARD_HEIGHT)
        log_level_combo.setObjectName("log_level_combo")
        log_level_combo.addItems(["Debug", "Info", "Warning", "Error"])
        current_level = self.config.get_value(
            "gui", "logLevel", fallback="Info"
        )
        log_level_combo.setCurrentText(current_level)
        log_level_combo.currentTextChanged.connect(
            lambda text: self.on_log_level_changed(text)
        )
        log_level_layout.addWidget(log_level_combo)
        advanced_layout.addLayout(log_level_layout)
        self.ui_elements["log_level_combo"] = log_level_combo

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        advanced_layout.addWidget(separator2)

        config_layout = QHBoxLayout()
        config_label = QLabel("Config Location:")
        config_label.setFixedHeight(STANDARD_HEIGHT)
        config_label.setFixedWidth(LABEL_WIDTH)
        config_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        config_layout.addWidget(config_label)

        config_layout.addStretch()

        config_btn_layout = QHBoxLayout()
        config_btn_layout.setSpacing(5)
        
        theme = get_system_theme()
        icon_color = get_icon_color(theme)

        open_btn = QPushButton()
        open_btn.setFixedSize(STANDARD_HEIGHT, STANDARD_HEIGHT)
        open_btn.setIcon(qta.icon("fa5s.folder-open", color=icon_color))
        open_btn.setToolTip("Open config directory")
        open_btn.setObjectName("openButton")
        open_btn.setProperty("iconOnly", "true")
        open_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(self.config.config_dir))
            )
        )
        self.open_btn = open_btn
        config_btn_layout.addWidget(open_btn)

        edit_btn = QPushButton()
        edit_btn.setFixedSize(STANDARD_HEIGHT, STANDARD_HEIGHT)
        edit_btn.setIcon(qta.icon("fa5s.edit", color=icon_color))
        edit_btn.setToolTip("Edit config file")
        edit_btn.setObjectName("editButton")
        edit_btn.setProperty("iconOnly", "true")
        edit_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(self.config.config_path))
            )
        )
        self.edit_btn = edit_btn
        config_btn_layout.addWidget(edit_btn)
        
        config_layout.addLayout(config_btn_layout)
        advanced_layout.addLayout(config_layout)

        advanced_group.setLayout(advanced_layout)
        return advanced_group

    def _create_about_group(self):
        credits_group = QGroupBox("About")
        credits_layout = QVBoxLayout()
        credits_layout.setSpacing(10)
        credits_layout.setContentsMargins(10, 15, 10, 15)
        
        title_layout = QHBoxLayout()
        app_icon = QLabel()
        app_icon.setPixmap(QIcon(resource_path("icon.ico")).pixmap(24, 24))
        title_layout.addWidget(app_icon)
        
        app_title = QLabel(f"Mica4U v{VERSION}")
        title_layout.addWidget(app_title)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_layout.addLayout(title_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        credits_layout.addWidget(line)

        devs_label = QLabel("Developers")
        devs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_layout.addWidget(devs_label)

        theme = get_system_theme()
        icon_color = get_icon_color(theme)

        devs_layout = QHBoxLayout()
        dev_icon = QLabel()
        dev_icon.setPixmap(qta.icon("fa5s.code", color=icon_color).pixmap(16, 16))
        devs_layout.addWidget(dev_icon)
        
        devs_label = QLabel('GUI by <a href="https://github.com/DRKCTRL">DRK</a>, Core by <a href="https://github.com/Maplespe">Maplespe</a>')
        devs_label.setOpenExternalLinks(True)
        devs_layout.addWidget(devs_label)
        devs_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_layout.addLayout(devs_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        credits_layout.addWidget(line2)

        testers_label = QLabel("Bug Testers")
        testers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_layout.addWidget(testers_label)

        testers_layout = QHBoxLayout()
        bug_icon = QLabel()
        bug_icon.setPixmap(qta.icon("fa5s.bug", color=icon_color).pixmap(16, 16))
        testers_layout.addWidget(bug_icon)
        
        bug_testers_label = QLabel("Youseffe, Rheman")
        testers_layout.addWidget(bug_testers_label)
        testers_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_layout.addLayout(testers_layout)
        
        credits_group.setLayout(credits_layout)
        return credits_group

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_ui()

    def refresh_ui(self):
        try:
            config_elements = {
                "show_unsupported": ("gui", "showUnsupportedEffects", None),
                "show_unsupported_options": ("gui", "showUnsupportedOptions", "false"),
                "show_preview": ("gui", "showEffectPreview", "true"),
            }

            for elem_id, (section, key, fallback) in config_elements.items():
                if elem_id in self.ui_elements:
                    self.ui_elements[elem_id].setChecked(
                        self.config.get_value(section, key, fallback=fallback).lower()
                        == "true"
                    )

            if "log_level_combo" in self.ui_elements:
                current_level = self.config.get_value(
                    "gui", "logLevel", fallback="Info"
                )
                self.ui_elements["log_level_combo"].setCurrentText(current_level)

            logger.debug("Settings dialog UI refreshed")
        except Exception as e:
            logger.error(f"Error refreshing settings UI: {str(e)}")
            raise

    def on_show_preview_changed(self):
        try:
            checked = self.show_preview.isChecked()
            self.config.set_value("gui", "showEffectPreview", str(checked).lower())

            if hasattr(self.parent, "update_window_size"):
                self.parent.update_window_size()
            logger.debug(f"Show effect preview setting changed to: {checked}")
        except Exception as e:
            logger.error(f"Error changing show preview setting: {str(e)}")
            raise

    def on_log_level_changed(self, level):
        try:
            self.config.set_value("gui", "logLevel", level)
            logger.set_level(getattr(logging, level.upper()))
            logger.debug(f"Log level changed to: {level}")
        except Exception as e:
            logger.error(f"Error changing log level: {str(e)}")
            raise

    def on_reset_settings(self):
        try:
            reply = QMessageBox.question(
                self,
                "Reset Settings",
                "Are you sure you want to reset all settings to default?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.config.reset_to_defaults():
                    if hasattr(self.parent, "style_group"):
                        for (
                            effect_key,
                            radio,
                        ) in self.parent.style_group.radio_buttons.items():
                            radio.setChecked(
                                effect_key == self.config.get_value("config", "effect")
                            )

                    if hasattr(self.parent, "options_group"):
                        self.parent.options_group.refresh_options()

                    if hasattr(self.parent, "colors_group"):
                        self.parent.colors_group.refresh_from_config()
                        show_preview = (
                            self.config.get_value(
                                "gui", "showEffectPreview", fallback="true"
                            ).lower()
                            == "true"
                        )
                        self.parent.colors_group.set_preview_visible(show_preview)

                    if hasattr(self.parent, "preset_group"):
                        self.parent.preset_group.update_presets()
                        default_preset = self.config.get_value(
                            "gui", "last_preset", "Light Mode"
                        )
                        index = self.parent.preset_group.preset_combo.findText(
                            default_preset
                        )
                        if index >= 0:
                            self.parent.preset_group.preset_combo.setCurrentIndex(index)

                    if hasattr(self.parent, "update_window_size"):
                        self.parent.update_window_size()

                    self.refresh_ui()

                    QMessageBox.information(
                        self, "Success", "Settings reset successfully!"
                    )
                else:
                    QMessageBox.critical(self, "Error", "Failed to reset settings!")
        except Exception as e:
            logger.error(f"Error resetting settings: {str(e)}")
            raise

    def on_show_unsupported_changed(self, checked):
        try:
            self.config.set_value("gui", "showUnsupportedEffects", str(checked).lower())
            if hasattr(self.parent, "style_group"):
                self.parent.style_group.refresh_effects()

            logger.debug(f"Show unsupported effects setting changed to: {checked}")
        except Exception as e:
            logger.error(f"Error changing show unsupported effects setting: {str(e)}")
            raise

    def on_show_unsupported_options_changed(self, checked):
        try:
            self.config.set_value("gui", "showUnsupportedOptions", str(checked).lower())
            if hasattr(self.parent, "options_group"):
                self.parent.options_group.refresh_options()

            logger.debug(f"Show unsupported options setting changed to: {checked}")
        except Exception as e:
            logger.error(f"Error changing show unsupported options setting: {str(e)}")
            raise

    def check_for_updates(self):
        if self.parent and hasattr(self.parent, "check_for_updates"):
            self.parent.check_for_updates(manual=True)


@log_errors
def check_dll_initialized(config_manager):
    dll_path = config_manager.get_dll_path()
    dll_name = os.path.basename(dll_path)
    for proc in psutil.process_iter(["pid", "name", "memory_maps"]):
        try:
            if proc.info["name"].lower() == "explorer.exe":
                for mmap in proc.memory_maps():
                    if dll_name.lower() in mmap.path.lower():
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


class DLLStatusThread(QThread):
    status_updated = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True
        self.check_interval = 2000

    def run(self):
        while self.running:
            try:
                is_initialized = check_dll_initialized(self.config)
                self.status_updated.emit(is_initialized)
                self.msleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in DLL status thread: {str(e)}")
                self.msleep(self.check_interval)

    def stop(self):
        self.running = False
        self.wait()


class InstallThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, cmd_path, action):
        super().__init__()
        self.cmd_path = cmd_path
        self.action = action

    def run(self):
        try:
            logger.info(f"Running {self.action} command...")
            subprocess.run([self.cmd_path, self.action], check=True)
            self.finished.emit(True, f"Effects {self.action}ed successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to {self.action} effects: {str(e)}")
            self.finished.emit(False, f"Failed to {self.action} effects: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during {self.action}: {str(e)}")
            self.finished.emit(
                False, f"Unexpected error during {self.action}: {str(e)}"
            )


@log_errors
def get_system_theme():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value == 1 else "dark"
    except Exception as e:
        logger.error(f"Error detecting system theme: {str(e)}")
        return "dark"


@log_errors
def get_icon_color(theme):
    return "black" if theme == "light" else "white"


class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    check_finished = pyqtSignal(bool)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.repo_url = "https://api.github.com/repos/DRKCTRL/Mica4U/releases/latest"
        
    def run(self):
        try:
            latest_release = self._fetch_latest_release()
            if latest_release and self._is_newer_version(latest_release["tag_name"]):
                logger.info(f"Update available: {latest_release['tag_name']}")
                self.update_available.emit(latest_release)
                self.check_finished.emit(True)
            else:
                logger.info("No updates available")
                self.check_finished.emit(False)
        except Exception as e:
            logger.error(f"Error checking for updates: {str(e)}")
            self.check_finished.emit(False)
    
    def _fetch_latest_release(self):
        try:
            with urllib.request.urlopen(self.repo_url) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    return data
                else:
                    logger.warning(f"Failed to fetch updates: HTTP {response.getcode()}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching latest release: {str(e)}")
            return None
    
    def _is_newer_version(self, latest_version):
        latest_version = latest_version.lstrip('v')
        current_version = self.current_version.lstrip('v')

        current_parts = [int(x) for x in current_version.split('.')]
        latest_parts = [int(x) for x in latest_version.split('.')]

        while len(current_parts) < 3:
            current_parts.append(0)
        while len(latest_parts) < 3:
            latest_parts.append(0)

        for i in range(min(len(current_parts), len(latest_parts))):
            if latest_parts[i] > current_parts[i]:
                return True
            elif latest_parts[i] < current_parts[i]:
                return False

        return len(latest_parts) > len(current_parts)


class UpdateDialog(QDialog):
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Update Available")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        update_icon = QLabel()
        update_icon.setPixmap(qta.icon("fa5s.cloud-download-alt", color="green").pixmap(32, 32))
        header_layout.addWidget(update_icon)
        
        title = QLabel(f"<h2>Update Available: {self.update_info['tag_name']}</h2>")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel(f"<b>Current version:</b> {VERSION}"))
        version_layout.addWidget(QLabel(f"<b>New version:</b> {self.update_info['tag_name']}"))
        layout.addLayout(version_layout)

        release_date = self.update_info.get("published_at", "").split("T")[0]
        if release_date:
            layout.addWidget(QLabel(f"<b>Release date:</b> {release_date}"))

        layout.addWidget(QLabel("<b>Release Notes:</b>"))
        release_notes = QTextBrowser()
        release_notes.setMinimumHeight(200)

        notes = self.update_info.get("body", "No release notes available.")
        notes = re.sub(r"^# (.+)$", r"<h1>\1</h1>", notes, flags=re.MULTILINE)
        notes = re.sub(r"^## (.+)$", r"<h2>\1</h2>", notes, flags=re.MULTILINE)
        notes = re.sub(r"^### (.+)$", r"<h3>\1</h3>", notes, flags=re.MULTILINE)
        notes = re.sub(r"^\* (.+)$", r"• \1<br>", notes, flags=re.MULTILINE)
        notes = re.sub(r"^- (.+)$", r"• \1<br>", notes, flags=re.MULTILINE)
        notes = re.sub(r"\n\n", r"<br><br>", notes)
        
        release_notes.setHtml(notes)
        layout.addWidget(release_notes)
        
        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download Update")
        self.download_btn.clicked.connect(self.download_update)
        
        self.close_btn = QPushButton("Remind Me Later")
        self.close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
    
    def download_update(self):
        try:
            webbrowser.open(self.update_info["html_url"])
            self.accept()
        except Exception as e:
            logger.error(f"Error opening update URL: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Could not open the download page. Please visit manually:\n{self.update_info.get('html_url', '')}"
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.dll_status_thread = DLLStatusThread(self.config)
        self.dll_status_thread.status_updated.connect(self.update_dll_status)
        self.install_thread = None
        self.uninstall_thread = None
        self.update_checker = None
        self.init_ui()
        self.dll_status_thread.start()
        self.load_styles()
        self.update_icon_colors()
        self.current_theme = get_system_theme()
        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_theme_change)
        self.theme_check_timer.start(1000)
        current_effect = self.config.get_value("config", "effect")
        is_mica_effect = current_effect in ["2", "4"]
        if is_mica_effect:
            self.colors_group.on_effect_changed(True)
            self.preset_group.on_effect_changed(True)
            
        check_on_startup = self.config.get_value("gui", "checkUpdatesOnStartup", fallback="true").lower() == "true"
        if check_on_startup:
            QTimer.singleShot(1000, lambda: self.check_for_updates(manual=False))
            
    def check_theme_change(self):
        new_theme = get_system_theme()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.update_icon_colors()
            logger.debug(f"Theme changed to {new_theme}, updating icon colors")

    def update_icon_colors(self):
        theme = get_system_theme()
        icon_color = get_icon_color(theme)
        for btn_name, icon_name in [
            ("install_btn", "fa5s.download"),
            ("uninstall_btn", "fa5s.trash"),
            ("settings_btn", "fa5s.cog"),
        ]:
            if hasattr(self, btn_name):
                getattr(self, btn_name).setIcon(qta.icon(icon_name, color=icon_color))
        if hasattr(self, "settings_dialog"):
            for btn_name, icon_name in [
                ("open_btn", "fa5s.folder-open"),
                ("edit_btn", "fa5s.edit"),
            ]:
                if hasattr(self.settings_dialog, btn_name):
                    getattr(self.settings_dialog, btn_name).setIcon(
                        qta.icon(icon_name, color=icon_color)
                    )
        if hasattr(self, "preset_group"):
            for btn_name, icon_name in [
                ("save_btn", "fa5s.save"),
                ("delete_btn", "fa5s.trash"),
            ]:
                if hasattr(self.preset_group, btn_name):
                    getattr(self.preset_group, btn_name).setIcon(
                        qta.icon(icon_name, color=icon_color)
                    )
        logger.debug(f"Updated icon colors for {theme} theme")

    def load_styles(self):
        logger.debug("Styles loading disabled")

    def update_window_size(self):
        show_preview = (
            self.config.get_value("gui", "showEffectPreview", fallback="true").lower()
            == "true"
        )
        if hasattr(self, "colors_group"):
            self.colors_group.set_preview_visible(show_preview)
        QApplication.processEvents()
        self.setFixedSize(400, 650 if show_preview else 620)
        logger.debug(f"Window size updated based on preview visibility: {show_preview}")

    def update_dll_status(self, is_initialized):
        status_text = "Initialized" if is_initialized else "Not Initialized"
        color = "green" if is_initialized else "red"
        rich_text = f'<span style="font-size: 11pt; letter-spacing: 1px;"><b>DLL Status: <font color="{color}">{status_text}</font></b></span>'
        self.status_label.setText(rich_text)

    def closeEvent(self, event):
        thread_attrs = [
            "dll_status_thread",
            "theme_check_timer",
            "install_thread",
            "uninstall_thread",
            "update_checker",
        ]
        for attr in thread_attrs:
            if hasattr(self, attr):
                thread = getattr(self, attr)
                if thread:
                    if hasattr(thread, "stop"):
                        thread.stop()
                    elif hasattr(thread, "quit") and thread.isRunning():
                        thread.quit()
                        thread.wait()
        super().closeEvent(event)

    def init_ui(self):
        self.setWindowTitle("Mica4U")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.setup_layout(main_widget)
        self.update_window_size()
        self.load_selected_effect()
        logger.debug("UI initialized successfully")

    def setup_layout(self, main_widget):
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(STANDARD_SPACING)
        self.status_label = QLabel("DLL Status: Checking...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status_label)

        self.style_group = StyleGroup(self.config)
        self.options_group = OptionsGroup(self.config)
        self.colors_group = ColorsGroup(self.config)
        self.preset_group = PresetGroup(self.config, self.colors_group)
        self.style_group.effect_changed.connect(self.colors_group.on_effect_changed)
        self.style_group.effect_changed.connect(self.preset_group.on_effect_changed)

        for widget in [
            self.style_group,
            self.options_group,
            self.preset_group,
            self.colors_group,
        ]:
            layout.addWidget(widget)

        action_layout = QHBoxLayout()
        self.create_action_buttons(action_layout)
        layout.addLayout(action_layout)
        main_widget.setLayout(layout)
        logger.debug("Layout setup completed successfully")

    def create_action_buttons(self, action_layout):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        theme = get_system_theme()
        icon_color = get_icon_color(theme)
        
        def create_btn(
            name, text, icon, tooltip, callback, min_width=None, icon_only=False
        ):
            btn = QPushButton(text if not icon_only else "")
            btn.setFixedHeight(STANDARD_HEIGHT)
            if min_width:
                btn.setMinimumWidth(min_width)
            elif icon_only:
                btn.setFixedWidth(STANDARD_HEIGHT)
            btn.setIcon(qta.icon(icon, color=icon_color))
            btn.setToolTip(tooltip)
            btn.setObjectName(f"{name}Button")
            if icon_only:
                btn.setProperty("iconOnly", "true")
            btn.clicked.connect(callback)
            setattr(self, name, btn)
            return btn
            
        def install_clicked():
            if self.install_thread and self.install_thread.isRunning():
                return
            cmd_path = self.config.get_init_path()
            is_initialized = check_dll_initialized(self.config)
            self.install_thread = InstallThread(
                cmd_path, "restart" if is_initialized else "install"
            )
            self.install_thread.finished.connect(
                lambda success, msg: self.handle_install_result(
                    success, msg, self.install_btn
                )
            )
            self.install_thread.start()
            self.install_btn.setEnabled(False)
            
        def uninstall_clicked():
            if self.uninstall_thread and self.uninstall_thread.isRunning():
                return
            self.uninstall_thread = InstallThread(
                self.config.get_init_path(), "uninstall"
            )
            self.uninstall_thread.finished.connect(
                lambda success, msg: self.handle_install_result(
                    success, msg, self.uninstall_btn
                )
            )
            self.uninstall_thread.start()
            self.uninstall_btn.setEnabled(False)
        
        button_layout.addWidget(
            create_btn(
                "install_btn",
                "Install",
                "fa5s.download",
                "Install effects",
                install_clicked,
                min_width=100,
            )
        )
        button_layout.addWidget(
            create_btn(
                "uninstall_btn",
                "Uninstall",
                "fa5s.trash",
                "Uninstall effects",
                uninstall_clicked,
                min_width=100,
            )
        )
        button_layout.addWidget(
            create_btn(
                "settings_btn",
                "",
                "fa5s.cog",
                "Open settings dialog",
                lambda: self.open_settings(),
                icon_only=True,
            )
        )
        
        action_layout.addLayout(button_layout)
        logger.debug("Action buttons created successfully")
        
    def open_settings(self):
        logger.debug("Opening settings dialog")
        self.settings_dialog = SettingsDialog(self.config, self)
        self.settings_dialog.exec()

    def handle_install_result(self, success, message, button):
        button.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", message)
            QTimer.singleShot(
                8000 if "install" in message else 3000,
                lambda: [
                    self.show(),
                    self.activateWindow(),
                    self.raise_(),
                    self.setFocus(),
                ],
            )
        else:
            QMessageBox.critical(self, "Error", message)

    def load_selected_effect(self):
        effect = self.config.get_value("config", "effect", fallback="1")
        if hasattr(self, "style_group") and effect in self.style_group.radio_buttons:
            self.style_group.radio_buttons[effect].setChecked(True)
            logger.debug(f"Loaded effect from config: {effect}")
        else:
            logger.warning(f"Effect {effect} not found in available options")

    def check_for_updates(self, manual=True):
        if hasattr(self, "update_checker") and self.update_checker and self.update_checker.isRunning():
            return
            
        logger.info(f"Checking for updates... (Manual: {manual})")
        self.update_checker = UpdateChecker(VERSION)
        self.update_checker.update_available.connect(self.show_update_dialog)
        self.update_checker.check_finished.connect(lambda result: self.update_check_finished(result, manual))
        self.update_checker.start()
        
    def update_check_finished(self, updates_available, manual=True):
        if manual and not updates_available:
            QMessageBox.information(self, "No Updates", "Your application is up to date.")
            
    def show_update_dialog(self, update_info):
        dialog = UpdateDialog(update_info, self)
        dialog.exec()


def main():
    logger.info("Starting Mica4U application")
    atexit.register(cleanup_temp)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))

    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"Mica4U.Application.{VERSION}"
        )
        app.setStyle(app.style().name())

    window = MainWindow()
    window.show()

    logger.info("Application started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
