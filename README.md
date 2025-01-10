# Mica4U
A GUI tool to add background Blur, Acrylic, or Mica effects to Windows Explorer for Windows 10 and 11.

# NOTICE
Please note that I am not liable for any damage or harm this application may cause to your system, whether during installation, usage, or any other circumstances.


[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/DRKCTRL/Mica4U)](https://github.com/DRKCTRL/Mica4U/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/DRKCTRL/Mica4U/total)](https://github.com/DRKCTRL/Mica4U/releases)
[![GitHub issues](https://img.shields.io/github/issues/DRKCTRL/Mica4U)](https://github.com/DRKCTRL/Mica4U/issues)

This project uses [GNU LGPL v3 license](/LICENSE).

## Features
* Multiple effects available:
  - Acrylic
  - Blur
  - Blur (Clear)
  - Mica
  - Mica Alt
* Customizable transparency and colors
* Light/Dark mode presets
* Easy-to-use graphical interface

## Compatibility
- Windows *10*/11
- Compatible with StartAllBack, Rectify11, and multitudes of other software

## Installation
1. Download the latest release from the [Releases](https://github.com/DRKCTRL/Mica4U/releases) page
2. Extract the files to a permanent location (e.g., `C:\Program Files`)
3. Run the GUI application
4. Select your desired style and options
5. Click "Install" (requires administrator privileges)
6. Explorer will restart automatically to apply changes

## Usage
### Main Options
- **Style**: Choose between Acrylic, Blur, Blur (Clear), Mica, or Mica Alt effects
- **Options**:
  - Clear Address Bar: Makes the address bar transparent
  - Clear Toolbar: Makes the toolbar area transparent
  - Clear Background: Makes the window background transparent
  - Show Separator: Shows a separator line between sections

### Color Settings
- Use presets (Light/Dark) or customize colors manually:
  - Alpha: Adjust transparency
  - Red: Adjust red component
  - Green: Adjust green component
  - Blue: Adjust blue component

### Uninstallation
1. Open the GUI application
2. Click "Remove" (requires administrator privileges)
3. Delete the program files

Note: If Explorer crashes, hold the `ESC` key while opening Explorer to bypass the effect, then uninstall the program.

## Credits
This project builds upon [ExplorerBlurMica](https://github.com/Maplespe/ExplorerBlurMica) by Maplespe, which provides the core functionality for applying visual effects to Windows Explorer. The additional user-friendly graphical interface is powered by PyQt6.

## Compilation
To compile Mica4U from source, you'll need:
- Python 3.10 or higher
- PyQt6
- PyInstaller
- Inno Setup 6

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/DRKCTRL/Mica4U.git
   cd Mica4U
   ```

2. Install required Python packages:
   ```bash
   pip install PyQt6 pyinstaller
   ```

3. Download and install [Inno Setup 6](https://jrsoftware.org/isdl.php)

4. Run the build script:
   - Double-click `build.cmd`, or
   - Run from command line:
     ```bash
     build.cmd
     ```

The build process will:
1. Clean previous builds (optional)
2. Create executable using PyInstaller
3. Create installer using Inno Setup
4. Output files will be in:
   - `compiled/dist/` - Standalone executable
   - `compiled/installer/` - Windows installer

### Manual Compilation
If you prefer to compile manually:

1. Build executable:
   ```bash
   pyinstaller compiled/Mica4U.spec
   ```

2. Create installer:
   ```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "compiled\installer.iss"
   ```

### Troubleshooting
- If Explorer crashes, hold the `ESC` key while opening Explorer to bypass the effect
- Make sure all required files are in the correct locations before building
- Check the build directory for any error logs

