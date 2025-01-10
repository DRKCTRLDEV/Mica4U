import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, QCheckBox, QLabel, QSlider, QPushButton, QDialog, QSpinBox, QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import subprocess
import os
import configparser
import atexit
import shutil
import tempfile

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def cleanup_temp():
    """Clean up PyInstaller temp folder"""
    try:
        temp_dir = tempfile._get_default_tempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith('_MEI'):
                try:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath, ignore_errors=True)
                except:
                    pass
    except:
        pass

class Config:
    def __init__(self, config_file='config.ini'):
        # Get AppData path for config storage
        self.config_dir = os.path.join(os.getenv('APPDATA'), 'Mica4U')
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        self.config_file = os.path.join(self.config_dir, config_file)
        
        # Extract files and update if newer version exists
        files_to_extract = {
            'ExplorerBlurMica.dll': os.path.join(self.config_dir, 'ExplorerBlurMica.dll'),
            'Initialise.cmd': os.path.join(self.config_dir, 'Initialise.cmd')
        }
        
        for source_name, dest_path in files_to_extract.items():
            try:
                source_path = resource_path(source_name)
                # Always try to extract if file doesn't exist
                if not os.path.exists(dest_path):
                    shutil.copyfile(source_path, dest_path)
                else:
                    # Try to update existing file
                    try:
                        # Create a temporary file first
                        temp_path = dest_path + '.tmp'
                        shutil.copyfile(source_path, temp_path)
                        # If successful, replace the old file
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                        os.rename(temp_path, dest_path)
                    except Exception as e:
                        # If update fails, keep using existing file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        print(f"Warning: Could not update {source_name}: {str(e)}")
            except Exception as e:
                print(f"Warning: Could not extract {source_name}: {str(e)}")
        
        self.defaults = {
            'gui': {'windowwidth': '400', 'windowbaseheight': '500'},
            'explorerblurmica': {
                'mode': '1', 'clearaddress': 'true', 'clearbarbg': 'true',
                'clearwinuibg': 'true', 'showline': 'false'
            },
            'light': {'r': '255', 'g': '255', 'b': '255', 'a': '120'},
            'dark': {'r': '255', 'g': '255', 'b': '255', 'a': '120'}
        }
        
        self.config = configparser.ConfigParser()
        
        # If config doesn't exist, create it with defaults
        if not os.path.exists(self.config_file):
            for section, values in self.defaults.items():
                self.config[section] = values
            self.save()
        else:
            self.config.read(self.config_file)

    def get(self, section, key):
        return self.config.get(section, key.lower(), 
                             fallback=self.defaults[section][key.lower()])

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key.lower(), str(value))
        self.save()

    def save(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.colors_group = None  # Initialize the variable
        self.preset_btns = {}     # Initialize preset buttons dictionary
        
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mica4U")
        self.update_window_size()
        
        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        
        # Create widgets in specific order
        style_group = self.create_style_group()
        options_group = self.create_options_group()
        preset_group = self.create_preset_group()
        self.colors_group = self.create_colors_group()  # Assign to self.colors_group
        
        # Add widgets to layout
        for widget in [style_group, options_group, preset_group, self.colors_group]:
            layout.addWidget(widget)
        layout.addLayout(self.create_buttons())

    def create_group(self, title, layout_class=QVBoxLayout):
        group = QGroupBox(title)
        group.setLayout(layout_class())
        return group

    def create_style_group(self):
        group = self.create_group("Style")
        current_mode = self.config.get('explorerblurmica', 'mode')
        
        styles = [
            ("Acrylic", "1", "Windows 10 style blur effect with noise texture"),
            ("Mica", "2", "Windows 11 style subtle transparency effect"),
            ("Mica Alt", "4", "Alternative Mica effect with different transparency levels")
        ]
        
        for style, mode, tooltip in styles:
            rb = QRadioButton(style)
            rb.setChecked(current_mode == mode)
            rb.clicked.connect(lambda _, m=mode: 
                             self.config.set('explorerblurmica', 'mode', m))
            rb.setToolTip(tooltip)
            group.layout().addWidget(rb)
        return group

    def create_options_group(self):
        group = self.create_group("Options")
        options = [
            ("Clear Address Bar", 'clearaddress', 
             "Makes the address bar transparent"),
            ("Clear Toolbar", 'clearbarbg', 
             "Makes the toolbar area transparent"),
            ("Clear Background", 'clearwinuibg', 
             "Makes the main window background transparent"),
            ("Show Separator", 'showline', 
             "Shows a line between the toolbar and content area")
        ]
        
        for text, key, tooltip in options:
            cb = QCheckBox(text)
            cb.setChecked(self.config.get('explorerblurmica', key) == 'true')
            cb.clicked.connect(lambda checked, k=key: 
                             self.config.set('explorerblurmica', k, str(checked).lower()))
            cb.setToolTip(tooltip)
            group.layout().addWidget(cb)
        return group

    def create_preset_group(self):
        group = self.create_group("Preset", QHBoxLayout)
        presets = {
            "Custom": "Customize colors using the sliders below",
            "Light": "White background with 47% opacity",
            "Dark": "Black background with 47% opacity"
        }
        
        self.preset_btns = {}
        for name, tooltip in presets.items():
            btn = QRadioButton(name)
            btn.setToolTip(tooltip)
            btn.toggled.connect(self.update_colors)
            self.preset_btns[name] = btn
            group.layout().addWidget(btn)
        
        self.preset_btns["Custom"].setChecked(True)
        return group

    def create_colors_group(self):
        self.colors_group = self.create_group("Colors")
        self.sliders = {}
        
        colors = [
            ("Alpha", "a", "Controls the transparency level (0-255)"),
            ("Red", "r", "Adjusts the red component of the background color"),
            ("Green", "g", "Adjusts the green component of the background color"),
            ("Blue", "b", "Adjusts the blue component of the background color")
        ]
        
        for label, key, tooltip in colors:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label}:"))
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 255)
            slider.setValue(int(self.config.get('light', key)))
            slider.setToolTip(tooltip)
            
            value_label = QLabel(str(slider.value()))
            value_label.setToolTip(tooltip)
            slider.valueChanged.connect(lambda v, k=key, l=value_label: self.update_slider(k, v, l))
            
            self.sliders[key] = (slider, value_label)
            for widget in [slider, value_label]:
                row.addWidget(widget)
            self.colors_group.layout().addLayout(row)
        return self.colors_group

    def create_buttons(self):
        layout = QHBoxLayout()
        buttons = [
            ("Install", self.install, "Install and activate the transparency effects"),
            ("Remove", self.remove, "Remove transparency effects and restore defaults"),
            ("Settings", self.show_settings, "Configure application settings")
        ]
        
        for text, handler, tooltip in buttons:
            btn = QPushButton(text)
            btn.setMinimumWidth(100)
            btn.clicked.connect(handler)
            btn.setToolTip(tooltip)
            layout.addWidget(btn)
        return layout

    def update_slider(self, key, value, label):
        label.setText(str(value))
        self.config.set('light', key, value)

    def update_colors(self):
        if hasattr(self, 'colors_group') and self.colors_group:
            is_custom = self.preset_btns["Custom"].isChecked()
            self.colors_group.setEnabled(is_custom)
            
            if not is_custom:
                value = '255' if self.preset_btns["Light"].isChecked() else '0'
                for section in ['light', 'dark']:
                    for key in ['r', 'g', 'b']:
                        self.config.set(section, key, value)
                    self.config.set(section, 'a', '120')
                
                for key, (slider, label) in self.sliders.items():
                    val = '120' if key == 'a' else value
                    slider.setValue(int(val))
                    label.setText(val)

    def update_window_size(self):
        self.setFixedSize(
            int(self.config.get('gui', 'windowwidth')),
            int(self.config.get('gui', 'windowbaseheight'))
        )

    def run_command(self, cmd_type):
        try:
            if cmd_type == 'install':
                dll_path = os.path.join(self.config.config_dir, 'ExplorerBlurMica.dll')
                if not os.path.exists(dll_path):
                    raise FileNotFoundError("ExplorerBlurMica.dll not found")
                self.config.save()
            
            cmd_path = os.path.join(self.config.config_dir, 'Initialise.cmd')
            result = subprocess.run(f"{cmd_path} {cmd_type}",
                                  shell=True, capture_output=True, text=True)
            
            if result.returncode == 2:
                raise PermissionError("Administrator privileges required")
            elif result.returncode != 0:
                raise RuntimeError(f"Command failed with code {result.returncode}")
            
            QMessageBox.information(self, "Success", 
                                  f"{cmd_type.capitalize()} Installation successful")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def install(self):
        self.run_command('install')

    def remove(self):
        self.run_command('uninstall')

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setFixedSize(400, 400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(self.create_dimensions_group())
        layout.addWidget(self.create_credits_group())
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def create_dimensions_group(self):
        group = self.create_group("Window Dimensions")
        dimensions = [
            ("Window Width:", 'windowwidth', 300, 800),
            ("Base Height:", 'windowbaseheight', 400, 800)
        ]
        
        for label, key, min_val, max_val in dimensions:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            
            spin = QSpinBox()
            spin.setRange(min_val, max_val)
            spin.setValue(int(self.config.get('gui', key)))
            spin.valueChanged.connect(lambda v, k=key: self.update_dimension(k, v))
            
            row.addWidget(spin)
            group.layout().addLayout(row)
        return group

    def create_credits_group(self):
        group = self.create_group("Credits")
        credits = QLabel(
            "Mica4U - A GUI Tool for ExplorerBlurMica\n\n"
            "Core functionality by ExplorerBlurMica\n"
            "GUI Interface developed by DRKCTRL\n"
            "Licensed under GNU LGPL v3"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group.layout().addWidget(credits)
        return group

    def update_dimension(self, key, value):
        self.config.set('gui', key, value)
        self.update_window_size()

if __name__ == '__main__':
    # Register cleanup function
    atexit.register(cleanup_temp)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('icon.ico')))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
