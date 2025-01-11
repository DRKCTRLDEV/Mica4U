# Mica4U
A GUI tool to add background Blur, Acrylic, or Mica effects to Windows Explorer for Windows 10 and 11.

# NOTICE
Please note that I am not liable for any damage or harm this application may cause to your system, whether during installation, usage, or any other circumstances.

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/DRKCTRL/Mica4U)](https://github.com/DRKCTRL/Mica4U/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/DRKCTRL/Mica4U/total)](https://github.com/DRKCTRL/Mica4U/releases)
[![GitHub issues](https://img.shields.io/github/issues/DRKCTRL/Mica4U)](https://github.com/DRKCTRL/Mica4U/issues)

## Features
* Multiple effects available:
  - Acrylic: Blur with noise (Windows 10/11)
  - Blur: Classic blur (Windows 11 22H2 or earlier)
  - Blur (Clear): Clean blur without noise (Windows 10/11)
  - Mica: System-colored background (Windows 11 only)
  - Mica Alt: Alternative system colors (Windows 11 only)
* Customizable transparency and colors
* Light/Dark mode presets
* Easy-to-use graphical interface

## Installation

### Method 1: Using the Installer (Recommended)
1. Download the latest installer from the [Releases](https://github.com/DRKCTRL/Mica4U/releases) page
2. Run the installer and follow the prompts
3. Launch Mica4U from the Start Menu or Desktop shortcut

### Method 2: Portable Version
1. Download the standalone executable from the [Releases](https://github.com/DRKCTRL/Mica4U/releases) page
2. Extract the ZIP file to your desired location
3. Run `Mica4U.exe`

**Note**: Both methods require administrator privileges for installation and usage.

## Usage

### Basic Setup
1. Launch Mica4U
2. Choose your desired effect:
   - Acrylic: Blur with noise (Windows 10/11)
   - Blur: Classic blur (Windows 11 22H2 or earlier)
   - Blur (Clear): Clean blur without noise (Windows 10/11)
   - Mica: System-colored background (Windows 11 only)
   - Mica Alt: Alternative system colors (Windows 11 only)

### Customization
1. **Effect Options**:
   - Clear Address Bar: Makes address bar transparent
   - Clear Toolbar: Makes toolbar transparent
   - Clear Background: Makes window background transparent
   - Show Separator: Shows line between toolbar and content

2. **Color Settings**:
   - Use the color picker to customize background colors
   - Adjust transparency with the alpha slider
   - Save custom color combinations as presets

3. **Presets**:
   - Choose from built-in Light/Dark mode presets
   - Create custom presets for quick switching
   - Delete unwanted custom presets

### Applying Changes
1. After adjusting settings, click "Install" to apply changes
2. Windows Explorer will restart automatically
3. Your new settings will take effect immediately

### Troubleshooting
- If Explorer crashes, hold the `ESC` key while opening Explorer to bypass the effect
- Use the "Uninstall" button to remove effects if issues persist
- Check the Settings dialog for compatibility options

## Uninstallation

### Method 1: Using Windows Settings (Recommended)
1. Open Windows Settings
2. Go to Apps > Apps & features
3. Search for "Mica4U"
4. Click "Uninstall"
5. Follow the prompts to complete uninstallation

### Method 2: Manual Cleanup
1. Uninstall effects using the "Uninstall" button in Mica4U
2. Delete the program files
3. Delete the configuration folder at `%APPDATA%\Mica4U` (optional)

## Compatibility
- Windows *10*/11
- Compatible with StartAllBack, Rectify11, and multitudes of other software

## Credits
This project builds upon [ExplorerBlurMica](https://github.com/Maplespe/ExplorerBlurMica) by Maplespe, which provides the core functionality for applying visual effects to Windows Explorer. The additional user-friendly graphical interface is powered by PyQt6.

## Building from source
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

This project uses [GNU LGPL v3 license](/LICENSE).

