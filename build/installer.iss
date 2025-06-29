#define AppName "Mica4U"
#define Version "1.7.0"
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
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
LicenseFile=..\LICENSE
OutputDir=output
OutputBaseFilename=Mica4U_Setup
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#AppName}
UninstallDisplayName={#AppName}
Compression=lzma
SolidCompression=yes
CompressionThreads=2
WizardStyle=modern
PrivilegesRequired=admin
UninstallRestartComputer=no
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ExplorerBlur.dll"; DestDir: "{userappdata}\Mica4U"; Flags: ignoreversion

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
Filename: "regsvr32"; Parameters: "/s /u ""{userappdata}\Mica4U\ExplorerBlur.dll"""; Flags: runhidden; StatusMsg: "Unregistering DLL..."

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{group}"
Type: filesandordirs; Name: "{userappdata}\Mica4U"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  mRes: integer;
  appDataPath: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    mRes := MsgBox('Do you want to remove all settings and files? Click Yes to remove everything, No to keep settings.', 
                   mbConfirmation, MB_YESNO or MB_DEFBUTTON2);
    if mRes = IDYES then
    begin
      appDataPath := ExpandConstant('{userappdata}\Mica4U');
      if DirExists(appDataPath) then
        DelTree(appDataPath, True, True, True);
    end;
  end;
end;

[InstallDelete]
Type: filesandordirs; Name: "{app}"
