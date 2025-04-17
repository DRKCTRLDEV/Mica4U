# 🎨 Mica4U

A beautiful GUI tool to add background Blur, Acrylic, or Mica effects to Windows Explorer for Windows 10 and 11.

<div align="center">

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/DRKCTRL/Mica4U)](https://github.com/DRKCTRL/Mica4U/releases)
[![GitHub all releases](https://img.shields.io/github/downloads/DRKCTRL/Mica4U/total)](https://github.com/DRKCTRL/Mica4U/releases)
[![GitHub issues](https://img.shields.io/github/issues/DRKCTRL/Mica4U)](https://github.com/DRKCTRL/Mica4U/issues)

</div>

## ⚠️ Important Notices

> **Warning**
> YMMV on Windows 11, Version 24H2 (OS Build 26100.3624) due to changes in the Windows Explorer architecture.
> However, Mica4U has been verified as working on **Win10 Pro Version 22H2 (OS Build 19045.5608), and Win11 Home Version 24H2 (OS Build 26100.3775)** by both myself and a few trusted friend.

> **Disclaimer**
> Please note that I am not liable for any damage or harm this application may cause to your system, whether during installation, usage, or any other circumstances.

## ✨ Features

<div align="center">

| Effect | Description | Compatibility |
|--------|-------------|---------------|
| Acrylic | Blur with noise | Windows 10/11 |
| Blur | Classic blur | Windows 10/11 |
| Blur (Clear) | Clean blur without noise | Windows 11/10 22H2 or earlier |
| Mica | System-colored background | Windows 11 only |
| Mica Alt | Alternative system colors | Windows 11 only |

</div>

### Additional Features
- Customizable transparency and colors
- Light/Dark mode presets
- Modern, user-friendly interface with Font Awesome icons
- Comprehensive settings panel
- Detailed logging system
- Portable mode support

## 💻 System Requirements
- Windows 10 or Windows 11
- Administrator privileges for installation
- Compatible with StartAllBack, Rectify11, and other customization software

## 📥 Installation

### Method 1: Using the Installer (Recommended)
1. Download the latest installer from the [Releases](https://github.com/DRKCTRL/Mica4U/releases) page
2. Run the installer and follow the prompts
3. Launch Mica4U from the Start Menu or Desktop shortcut

### Method 2: Portable Version
1. Download the standalone executable from the [Releases](https://github.com/DRKCTRL/Mica4U/releases) page
2. Extract the ZIP file to your desired location
3. Run `Mica4U.exe`

> **Note**: Both methods require administrator privileges for installation and usage.

## 🎮 Usage

### Basic Setup
1. Launch Mica4U
2. Choose your desired effect from the options above

### Customization Options

#### Effect Options
- Clear Address Bar: Makes address bar transparent
- Clear Toolbar: Makes toolbar transparent
- Clear Background: Makes window background transparent
- Show Separator: Shows line between toolbar and content

#### Color Settings
- Adjust RGBA values using sliders, Aswell as the inbuilt ColorPickerDialog
- Control transparency with alpha channel
- Real-time color preview
- Save custom color combinations as presets

#### Presets
- Built-in Light/Dark mode presets
- Create and manage custom presets
- Quick switching between presets

#### Settings
- **Appearance**:
  - Theme selection (System/Light/Dark)
  - Window size customization
- **Effects**:
  - Show/hide unsupported effects
  - Toggle color preview
- **Advanced**:
  - Logging level control
  - Config file location
- **About**:
  - Version information
  - Credits

### Applying Changes
1. After adjusting settings, click the Install button (download icon)
2. Windows Explorer will restart automatically
3. Your new settings will take effect immediately

### 🛠️ Troubleshooting
- If Explorer crashes, hold the `ESC` key while opening Explorer to bypass the effect
- Use the Uninstall button (trash icon) to remove effects if issues persist
- Check the Settings dialog for compatibility options
- View logs in `%APPDATA%\Mica4U\logs\mica4u.log` for detailed error information
- For portable mode, logs are stored in the application directory

## 🗑️ Uninstallation

### Method 1: Using Windows Settings (Recommended)
1. Open Windows Settings
2. Go to Apps > Apps & features
3. Search for "Mica4U"
4. Click "Uninstall"
5. Follow the prompts to complete uninstallation

### Method 2: Manual Cleanup
1. Uninstall effects using the Uninstall button in Mica4U
2. Delete the program files
3. Delete the configuration folder at `%APPDATA%\Mica4U` (optional)

## 🔨 Building from Source

### Prerequisites
- Python 3.10 or higher
- PyQt6
- qtawesome
- PyInstaller
- Inno Setup 6
- 7-Zip (optional, for better compression of portable version)

### Quick Build
1. Clone the repository:
   ```bash
   git clone https://github.com/DRKCTRL/Mica4U.git
   cd Mica4U
   ```

2. Install required Python packages:
   ```bash
   pip install PyQt6 qtawesome pyinstaller
   ```
   or
   ```bash
   pip install -r requirements.txt
   ```

3. Download and install [Inno Setup 6](https://jrsoftware.org/isdl.php)

4. Run the build script:
   - Double-click `build.cmd`, or
   - Run from command line:
     ```bash
     ./build.cmd
     ```

> **Note**: For improved compression of the portable version, download and install [7-Zip](https://www.7-zip.org/)

### Build Output
- `compiled/output/` - Standalone executable and installer
- `compiled/output/Mica4U_portable.zip` - Portable version

### Manual Compilation

> **Note**: Manual compilation will not update the version number. Use build.cmd instead to ensure proper versioning.

1. Build executable:
   ```bash
   pyinstaller compiled/Mica4U.spec
   ```

2. Create installer:
   ```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "compiled\installer.iss"
   ```