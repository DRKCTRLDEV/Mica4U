from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QLabel,
    QPushButton, QSpinBox, QHBoxLayout, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Settings')
        layout = QVBoxLayout(self)
        
        # Config Settings Group
        config_group = QGroupBox("Config")
        config_layout = QVBoxLayout()
        
        # Show unsupported effects option
        show_unsupported = QCheckBox('Show unsupported effects')
        show_unsupported.setChecked(
            self.config.get_value('gui', 'showUnsupportedEffects').lower() == 'true'
        )
        show_unsupported.clicked.connect(
            lambda checked: self.on_show_unsupported_changed(checked)
        )
        config_layout.addWidget(show_unsupported)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # GUI Settings Group
        gui_group = QGroupBox("GUI")
        gui_layout = QGridLayout()
        
        # Width setting
        gui_layout.addWidget(QLabel('Width:'), 0, 0)
        width_spin = QSpinBox()
        width_spin.setRange(300, 800)
        width_spin.setValue(int(self.config.get_value('gui', 'windowwidth')))
        width_spin.valueChanged.connect(
            lambda value: self.on_window_size_changed('windowwidth', value)
        )
        gui_layout.addWidget(width_spin, 0, 1)
        
        # Height setting
        gui_layout.addWidget(QLabel('Height:'), 1, 0)
        height_spin = QSpinBox()
        height_spin.setRange(400, 800)
        height_spin.setValue(int(self.config.get_value('gui', 'windowheight')))
        height_spin.valueChanged.connect(
            lambda value: self.on_window_size_changed('windowheight', value)
        )
        gui_layout.addWidget(height_spin, 1, 1)
        
        gui_group.setLayout(gui_layout)
        layout.addWidget(gui_group)
        
        # Credits Group
        credits_group = QGroupBox("Credits")
        credits_layout = QVBoxLayout()
        
        # GUI Credit
        gui_link = QLabel('GUI by <a href="https://github.com/DRKCTRL">DRKCTRL</a>')
        gui_link.setOpenExternalLinks(True)
        gui_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Core Credit
        core_link = QLabel('Core by <a href="https://github.com/Maplespe">Maplespe</a>')
        core_link.setOpenExternalLinks(True)
        core_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        credits_layout.addWidget(gui_link)
        credits_layout.addWidget(core_link)
        credits_layout.addWidget(version_label)
        
        credits_group.setLayout(credits_layout)
        layout.addWidget(credits_group)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def on_show_unsupported_changed(self, checked):
        self.config.set_value('gui', 'showUnsupportedEffects', str(checked).lower())
        if hasattr(self.parent, 'style_group'):
            self.parent.style_group.refresh_effects()

    def on_window_size_changed(self, setting, value):
        self.config.set_value('gui', setting, str(value))
        if hasattr(self.parent, 'update_window_size'):
            self.parent.update_window_size() 