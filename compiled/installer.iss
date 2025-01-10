#define MyAppName "Mica4U"
#define MyAppVersion "1.0"
#define MyAppPublisher "DRKCTRL"
#define MyAppURL "https://github.com/DRKCTRL/Mica4U"
#define MyAppExeName "Mica4U.exe"

[Setup]
AppId={{2B04C122-1A7E-4BB8-95AB-E2C414D1742C}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=installer
OutputBaseFilename=Mica4U_Setup
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
CloseApplications=yes
UninstallRestartComputer=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{{2B04C122-1A7E-4BB8-95AB-E2C414D1742C}}"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\{#MyAppExeName}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{{2B04C122-1A7E-4BB8-95AB-E2C414D1742C}}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{{2B04C122-1A7E-4BB8-95AB-E2C414D1742C}}"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#MyAppURL}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{{2B04C122-1A7E-4BB8-95AB-E2C414D1742C}}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"

[UninstallRun]
; First unregister the DLL
Filename: "{userappdata}\Mica4U\Initialise.cmd"; Parameters: "uninstall"; RunOnceId: "UnregisterDLL"; Flags: runhidden

[UninstallDelete]
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"
Type: files; Name: "{group}\*.*"
Type: dirifempty; Name: "{group}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
    mRes : integer;
    appDataPath: string;
begin
    case CurUninstallStep of
        usUninstall:
        begin
            mRes := MsgBox('Do you want to remove all settings and files? Click Yes to remove everything, No to keep settings.', 
                          mbConfirmation, MB_YESNO or MB_DEFBUTTON2);
            if mRes = IDYES then
            begin
                appDataPath := ExpandConstant('{userappdata}\Mica4U');
                DelTree(appDataPath, True, True, True);
            end;
        end;
        usPostUninstall:
        begin
            // Clean up Start Menu folder if empty
            DelTree(ExpandConstant('{group}'), False, True, True);
        end;
    end;
end;

[InstallDelete]
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}" 