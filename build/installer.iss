#define AppName "Mica4U"
#define Version "1.7.1"
#define Dev "DRK"
#define AppURL "https://github.com/DRKCTRLDEV/Mica4U"
#define ExeName "Mica4U.exe"

[Setup]
AppId={{2B04C122-1A7E-4BB8-95AB-E2C414D1742C}}
AppName={#AppName}
AppVersion={#Version}
AppPublisher={#Dev}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Directories
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=output

; Output
OutputBaseFilename=Mica4U_Setup
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#AppName}
UninstallDisplayName={#AppName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
CompressionThreads=6

; Privileges
PrivilegesRequired=admin
UninstallRestartComputer=no

; Architecture
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os

; License
LicenseFile=..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ExplorerBlurMica.dll"; DestDir: "{userappdata}\Mica4U"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#ExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#AppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; ValueType: string; ValueName: "UninstallString"; ValueData: "{uninstallexe}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\{#ExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#Dev}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#AppURL}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#Version}"; Flags: uninsdeletekey

[UninstallRun]
Filename: "regsvr32"; Parameters: "/s /u ""{userappdata}\Mica4U\ExplorerBlurMica.dll"""; Flags: runhidden; StatusMsg: "Unregistering DLL..."; RunOnceId: "UnregisterExplorerBlurDLL"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{group}"
Type: filesandordirs; Name: "{userappdata}\Mica4U"

[InstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function CompareVersion(ver1, ver2: string): Integer;
begin
  Result := CompareStr(ver1, ver2);
end;

function InitializeSetup: Boolean;
var
  InstalledVersion: string;
begin
  if RegQueryStringValue(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}', 'DisplayVersion', InstalledVersion) then
  begin
    if CompareVersion(InstalledVersion, '{#Version}') > 0 then
    begin
      MsgBox('A newer version of {#AppName} (' + InstalledVersion + ') is already installed.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
  Result := True;
end;
