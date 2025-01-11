from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
import subprocess
import os
import sys
from .dialogs import SettingsDialog

def create_action_buttons(parent):
    """Create and return a layout with action buttons"""
    button_layout = QHBoxLayout()
    
    # Install button
    install_btn = QPushButton("Install")
    install_btn.setToolTip("Install current settings")
    def install_clicked():
        try:
            cmd_path = parent.config.get_init_path()
            subprocess.run([cmd_path, "install"], check=True)
            QMessageBox.information(parent, "Success", "Effects installed successfully!")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to install effects: {str(e)}")
    install_btn.clicked.connect(install_clicked)
    button_layout.addWidget(install_btn)
    
    # Uninstall button
    uninstall_btn = QPushButton("Uninstall")
    uninstall_btn.setToolTip("Remove all effects")
    def uninstall_clicked():
        try:
            cmd_path = parent.config.get_init_path()
            subprocess.run([cmd_path, "uninstall"], check=True)
            QMessageBox.information(parent, "Success", "Effects uninstalled successfully!")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to uninstall effects: {str(e)}")
    uninstall_btn.clicked.connect(uninstall_clicked)
    button_layout.addWidget(uninstall_btn)
    
    # Get the standard button height
    button_height = install_btn.sizeHint().height()
    
    # Settings button
    settings_btn = QPushButton()
    settings_btn.setToolTip("Open settings dialog")
    settings_btn.setFixedSize(button_height, button_height)  # Make it square using the standard height
    
    # Get the icon path from resources
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    icon_path = os.path.join(base_path, 'resources', 'settings.png')
    settings_btn.setIcon(QIcon(icon_path))
    settings_btn.setIconSize(QSize(button_height - 8, button_height - 8))  # Larger icon (reduced padding from 12 to 8)
    settings_btn.clicked.connect(lambda: SettingsDialog(parent.config, parent).exec())
    button_layout.addWidget(settings_btn)
    
    return button_layout 