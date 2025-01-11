from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon
from utils.system import resource_path
from config.config_manager import ConfigManager
from gui.widgets.group_boxes import (
    StyleGroup,
    OptionsGroup,
    PresetGroup,
    ColorsGroup
)
from gui.widgets.action_buttons import create_action_buttons

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.init_ui()

    def init_ui(self):
        try:
            self.setWindowTitle("Mica4U")
            self.setWindowIcon(QIcon(resource_path('icon.ico')))
            self.update_window_size()
            
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            self.setup_layout(main_widget)
        except Exception as e:
            raise

    def setup_layout(self, main_widget: QWidget):
        layout = QVBoxLayout(main_widget)
        
        # Create main widget groups
        self.style_group = StyleGroup(self.config)
        self.options_group = OptionsGroup(self.config)
        self.colors_group = ColorsGroup(self.config)
        self.preset_group = PresetGroup(self.config, self.colors_group)
        
        # Add widgets to layout
        layout.addWidget(self.style_group)
        layout.addWidget(self.options_group)
        layout.addWidget(self.preset_group)
        layout.addWidget(self.colors_group)
        
        # Add action buttons
        layout.addLayout(create_action_buttons(self))

    def update_window_size(self):
        self.setFixedSize(
            int(self.config.get_value('gui', 'windowwidth')),
            int(self.config.get_value('gui', 'windowheight'))
        ) 