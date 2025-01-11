from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QRadioButton,
    QCheckBox, QLabel, QSlider, QPushButton, QFrame, QComboBox, QGridLayout, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from utils.system import get_windows_version
from config.constants import STYLE_EFFECTS

class BaseGroup(QGroupBox):
    def __init__(self, title, config):
        super().__init__(title)
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout())

class StyleGroup(BaseGroup):
    def __init__(self, config):
        self.grid_layout = None
        super().__init__("Style", config)

    def init_ui(self):
        super().init_ui()
        self.refresh_effects()

    def refresh_effects(self):
        # Clear existing layout if it exists
        if self.grid_layout:
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.layout().removeItem(self.grid_layout)
        
        # Create new grid layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        
        # Get Windows version info
        version_info = {
            'is_win11': get_windows_version() >= (10, 0, 22000),
            'is_win11_22h2_or_earlier': get_windows_version() <= (10, 0, 22621)
        }
        
        # Check if we should show unsupported effects
        show_unsupported = self.config.get_value('gui', 'showUnsupportedEffects').lower() == 'true'
        
        # Add effects in a 2x3 grid
        row = 0
        col = 0
        for name, value, tooltip, check_fn, disabled_reason in STYLE_EFFECTS:
            # Skip unsupported effects if setting is disabled
            if not show_unsupported and not check_fn(version_info):
                continue
                
            radio = QRadioButton(name)
            radio.setToolTip(tooltip if check_fn(version_info) else disabled_reason)
            radio.setChecked(self.config.get_value('config', 'effect') == value)
            radio.setEnabled(check_fn(version_info))
            radio.clicked.connect(lambda checked, v=value: self.on_effect_changed(v))
            
            # Create a container for each radio button to control spacing
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.addWidget(radio)
            container_layout.addStretch()
            container_layout.setContentsMargins(5, 2, 5, 2)
            
            self.grid_layout.addWidget(container, row, col)
            
            # Update grid position
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.layout().addLayout(self.grid_layout)

    def on_effect_changed(self, value):
        self.config.set_value('config', 'effect', value)

class OptionsGroup(BaseGroup):
    def __init__(self, config):
        super().__init__("Options", config)

    def init_ui(self):
        super().init_ui()
        options = [
            ("Clear Address Bar", 'clearAddress', "Make address bar transparent"),
            ("Clear Toolbar", 'clearBarBg', "Make toolbar transparent"),
            ("Clear Background", 'clearWinUIBg', "Make window background transparent"),
            ("Show Separator", 'showLine', "Show line between toolbar and content")
        ]
        
        for text, key, tooltip in options:
            cb = QCheckBox(text)
            cb.setChecked(self.config.get_value('config', key) == 'true')
            cb.clicked.connect(
                lambda checked, k=key: 
                self.config.set_value('config', k, str(checked).lower())
            )
            cb.setToolTip(tooltip)
            self.layout().addWidget(cb)

class PresetGroup(BaseGroup):
    def __init__(self, config, colors_group):
        super().__init__("Presets", config)
        self.colors_group = colors_group

    def init_ui(self):
        super().init_ui()
        
        # Main layout
        layout = QHBoxLayout()
        
        # Preset combo box
        self.preset_combo = QComboBox()
        self.preset_combo.setToolTip("Select a preset")
        self.update_presets()
        
        # Set to last used preset if it exists
        last_preset = self.config.get_value('gui', 'last_preset', fallback=None)
        if last_preset and last_preset in self.config.get_preset_names():
            index = self.preset_combo.findText(last_preset)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
        
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        layout.addWidget(self.preset_combo, stretch=1)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save current settings as preset")
        save_btn.clicked.connect(self.save_preset)
        layout.addWidget(save_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setToolTip("Delete selected preset")
        delete_btn.clicked.connect(self.delete_preset)
        layout.addWidget(delete_btn)
        
        self.layout().addLayout(layout)

    def update_presets(self):
        current = self.preset_combo.currentText()
        self.preset_combo.clear()
        self.preset_combo.addItems(self.config.get_preset_names())
        if current and current in self.config.get_preset_names():
            index = self.preset_combo.findText(current)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)

    def on_preset_changed(self, name):
        if name:
            if self.config.load_preset(name):
                self.colors_group.refresh_from_config()

    def save_preset(self):
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        name, ok = QInputDialog.getText(self, 'Save Preset', 'Enter preset name:')
        if ok and name:
            self.config.save_preset(name)
            self.update_presets()
            self.preset_combo.setCurrentText(name)

    def delete_preset(self):
        from PyQt6.QtWidgets import QMessageBox
        name = self.preset_combo.currentText()
        if not name:
            return
            
        if name in self.config.get_preset_names():
            if self.config.delete_preset(name):
                self.update_presets()
                QMessageBox.information(self, 'Success', 'Preset deleted successfully!')
            else:
                QMessageBox.warning(self, 'Error', 'Cannot delete default presets.')

class ColorPreview(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(20)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)

    def update_color(self, r, g, b, a):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: rgba({r}, {g}, {b}, {a});
                border-radius: 6px;
                margin: 0px 5px 0px 5px;
            }}
            """
        )

class ColorsGroup(BaseGroup):
    def __init__(self, config):
        self.sliders = {}
        self.value_labels = {}
        self.preview = ColorPreview()
        super().__init__("Colors", config)

    def init_ui(self):
        super().init_ui()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Labels for sliders
        labels = {
            'r': 'R',
            'g': 'G',
            'b': 'B',
            'a': 'A'
        }
        
        # Create sliders vertically
        for color_key in ['r', 'g', 'b', 'a']:
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Center vertically
            
            # Label
            label = QLabel(labels[color_key])
            label.setMinimumWidth(20)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center text
            row_layout.addWidget(label)
            
            # Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(255)
            
            initial_value = int(self.config.get_value('light', color_key))
            slider.setValue(initial_value)
            
            self.sliders[color_key] = slider
            row_layout.addWidget(slider)
            
            # Value label
            value_label = QLabel(str(initial_value))
            value_label.setMinimumWidth(30)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center text
            self.value_labels[color_key] = value_label
            row_layout.addWidget(value_label)
            
            slider.valueChanged.connect(self.create_update_handler(color_key))
            
            main_layout.addLayout(row_layout)
        
        # Add preview with reduced spacing
        main_layout.addWidget(self.preview)
        
        self.layout().addLayout(main_layout)
        
        # Initial color update
        self.update_colors()

    def create_update_handler(self, color_key):
        """Create a specific update handler for each slider"""
        def handler(value):
            self.value_labels[color_key].setText(str(value))
            self.update_colors()
        return handler

    def update_colors(self):
        r = self.sliders['r'].value()
        g = self.sliders['g'].value()
        b = self.sliders['b'].value()
        a = self.sliders['a'].value()
        
        # Update both light and dark themes with the same values
        for theme in ['light', 'dark']:
            self.config.set_value(theme, 'r', str(r))
            self.config.set_value(theme, 'g', str(g))
            self.config.set_value(theme, 'b', str(b))
            self.config.set_value(theme, 'a', str(a))
        
        # Update preview
        self.preview.update_color(r, g, b, a)

    def refresh_from_config(self):
        """Update sliders and preview from current config values"""
        for color_key in ['r', 'g', 'b', 'a']:
            value = int(self.config.get_value('light', color_key))
            self.sliders[color_key].blockSignals(True)  # Block signals temporarily
            self.sliders[color_key].setValue(value)
            self.value_labels[color_key].setText(str(value))
            self.sliders[color_key].blockSignals(False)  # Re-enable signals
        
        # Update preview directly
        self.update_colors()