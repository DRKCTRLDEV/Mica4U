import os
import json
from config.constants import DEFAULT_CONFIG, DEFAULT_PRESETS
import shutil
from pathlib import Path
import sys
from configparser import ConfigParser
import time

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.join(os.getenv('APPDATA', ''), 'Mica4U')
        self.config_path = os.path.join(self.config_dir, 'config.ini')
        self.dll_path = os.path.join(self.config_dir, 'ExplorerBlurMica.dll')
        self.init_path = os.path.join(self.config_dir, 'Initialise.cmd')
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Copy required files to AppData if they don't exist
        self.setup_required_files()
        
        self.config = ConfigParser()
        self.presets = {
            "Light Mode": {
                "r": "220",
                "g": "220",
                "b": "220",
                "a": "160"
            },
            "Dark Mode": {
                "r": "0",
                "g": "0",
                "b": "0",
                "a": "120"
            }
        }
        self.load_config()
        
        # Load last used preset if it exists
        last_preset = self.get_value('gui', 'last_preset', fallback=None)
        if last_preset and last_preset in self.presets:
            self.load_preset(last_preset)

    def setup_required_files(self):
        """Copy required files to AppData"""
        try:
            # Get the base path for resources
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                base_path = sys._MEIPASS
            else:
                # Running from source
                base_path = os.path.dirname(os.path.dirname(__file__))

            # Copy DLL with retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if not os.path.exists(self.dll_path):
                        shutil.copy2(os.path.join(base_path, 'ExplorerBlurMica.dll'), self.dll_path)
                    break
                except PermissionError:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait a second before retrying
                    else:
                        raise

            # Copy Initialise.cmd
            if not os.path.exists(self.init_path):
                shutil.copy2(os.path.join(base_path, 'Initialise.cmd'), self.init_path)

            # Create default config if it doesn't exist
            if not os.path.exists(self.config_path):
                self.create_default_config()

        except Exception as e:
            raise

    def create_default_config(self):
        """Create default config.ini file"""
        with open(self.config_path, 'w') as f:
            f.write("""[config]
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
windowwidth = 400
windowbaseheight = 550
showUnsupportedEffects = false
last_preset = Light Mode

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
}""")

    def load_config(self):
        """Load config from file"""
        if not os.path.exists(self.config_path):
            self.create_default_config()
            return

        # Read the file content
        with open(self.config_path, 'r') as f:
            content = f.read()

        # Split content into main config and presets
        main_config, _, presets_section = content.partition('[presets]')

        # Parse main config
        self.config = ConfigParser()
        self.config.read_string(main_config)

        # Parse presets if they exist
        if presets_section:
            try:
                # Extract preset entries
                preset_lines = presets_section.strip().split('\n')[1:]  # Skip the [presets] line
                current_preset = None
                preset_data = ""
                
                for line in preset_lines:
                    if '=' in line and not current_preset:
                        name, data = line.split('=', 1)
                        current_preset = name.strip()
                        preset_data = data.strip()
                    elif current_preset:
                        preset_data += line
                        if line.strip() == '}':
                            try:
                                self.presets[current_preset] = json.loads(preset_data)
                                current_preset = None
                                preset_data = ""
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                pass

    def save_config(self):
        """Save config to file in INI format"""
        try:
            with open(self.config_path, 'w') as f:
                f.write("[config]\n")
                f.write(f"effect = {self.config.get('config', 'effect')}\n")
                f.write(f"clearAddress = {self.config.get('config', 'clearAddress')}\n")
                f.write(f"clearBarBg = {self.config.get('config', 'clearBarBg')}\n")
                f.write(f"clearWinUIBg = {self.config.get('config', 'clearWinUIBg')}\n")
                f.write(f"showLine = {self.config.get('config', 'showLine')}\n\n")
                
                f.write("[light]\n")
                f.write(f"r = {self.config.get('light', 'r')}\n")
                f.write(f"g = {self.config.get('light', 'g')}\n")
                f.write(f"b = {self.config.get('light', 'b')}\n")
                f.write(f"a = {self.config.get('light', 'a')}\n\n")
                
                f.write("[dark]\n")
                f.write(f"r = {self.config.get('dark', 'r')}\n")
                f.write(f"g = {self.config.get('dark', 'g')}\n")
                f.write(f"b = {self.config.get('dark', 'b')}\n")
                f.write(f"a = {self.config.get('dark', 'a')}\n\n")
                
                f.write("[gui]\n")
                f.write(f"windowwidth = {self.config.get('gui', 'windowwidth')}\n")
                f.write(f"windowbaseheight = {self.config.get('gui', 'windowbaseheight')}\n")
                f.write(f"showUnsupportedEffects = {self.config.get('gui', 'showUnsupportedEffects')}\n")
                
                # Add last_preset if it exists
                try:
                    last_preset = self.config.get('gui', 'last_preset')
                    f.write(f"last_preset = {last_preset}\n")
                except:
                    pass
                
                f.write("\n[presets]\n")
                for preset_name, preset_data in self.presets.items():
                    f.write(f'{preset_name} = {{\n')
                    for key, value in preset_data.items():
                        f.write(f'    "{key}": "{value}"')
                        if key != 'a':  # Don't add comma after last item
                            f.write(',')
                        f.write('\n')
                    f.write('}\n')
        
        except Exception as e:
            raise

    def get_value(self, section, key, default=None, fallback=None):
        """Get value from config with fallback to default"""
        try:
            return self.config[section][key]
        except KeyError:
            if fallback is not None:
                return fallback
            if default is None and section in DEFAULT_CONFIG and key in DEFAULT_CONFIG[section]:
                return DEFAULT_CONFIG[section][key]
            return default

    def set_value(self, section, key, value):
        """Set value in config"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def get_preset_names(self):
        """Get list of preset names"""
        return list(self.presets.keys())

    def get_preset(self, name):
        """Get preset values by name"""
        if name in self.presets:
            return self.presets[name]
        return None

    def add_preset(self, name, values):
        """Add a new preset"""
        self.presets[name] = values
        self.save_config()

    def remove_preset(self, name):
        """Remove a preset"""
        if name in self.presets:
            del self.presets[name]
            self.save_config()

    def save_preset(self, name):
        """Save current light theme settings as a new preset"""
        try:
            # Get current light theme values
            preset_data = {
                'r': self.get_value('light', 'r'),
                'g': self.get_value('light', 'g'),
                'b': self.get_value('light', 'b'),
                'a': self.get_value('light', 'a')
            }
            
            # Add to presets dictionary
            self.presets[name] = preset_data
            
            # Save config to update the file
            self.save_config()
            return True
        except Exception as e:
            return False

    def delete_preset(self, name):
        """Delete a preset by name"""
        if name in self.presets and name not in ['Light Mode', 'Dark Mode']:
            del self.presets[name]
            self.save_config()
            return True
        return False

    def get_dll_path(self):
        """Return the path to the DLL in AppData"""
        return self.dll_path

    def get_init_path(self):
        """Return the path to the Initialise.cmd in AppData"""
        return self.init_path 

    def load_preset(self, name):
        """Load a preset by name"""
        if name in self.presets:
            preset = self.presets[name]
            # Update the config with preset values
            for key, value in preset.items():
                self.set_value('light', key, value)
            # Save the last used preset
            self.set_value('gui', 'last_preset', name)
            return True
        return False 