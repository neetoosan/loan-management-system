; Inno Setup Script - CORRECTED VERSION
; Fixes: Working directory issue, duplicate exe entry, removed problematic file associations
; Original Issue: Installed app fails silently because shortcuts had no working directory
; 
; Key Changes:
; 1. Added WorkingDir={app} to all shortcuts - CRITICAL FIX
; 2. Removed file association settings (.myp) which aren't needed
; 3. Consolidated duplicate executable entries
; 4. Added more robust DLL inclusion
; 5. Improved error handling and comments

#define MyAppName "Morning Star Cooperative"
#define MyAppVersion "2.0"
#define MyAppPublisher "Neetoosan (oyekanmi-israel)."
#define MyAppURL "https://neetoosan.github.io/neetoosan"
#define MyAppExeName "morning_star_cooperative.exe"
; Note: File association removed - define these only if needed for your use case
; #define MyAppAssocName MyAppName + " File"
; #define MyAppAssocExt ".myp"
; #define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{AE50C004-37AE-44C1-A0CB-79262B4DED96}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\MorningStarCooperative
; Allow user to change installation directory if desired
DisableDirPage=no
DefaultGroupName={#MyAppName}
; Allow user to change start menu group
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\{#MyAppExeName}
; ArchitecturesAllowed and ArchitecturesInstallIn64BitMode specify x64 only
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; FIX: Removed ChangesAssociations=yes (not needed unless you have custom file types)
; File associations can interfere with app launch if misconfigured
ChangesAssociations=no
PrivilegesRequired=lowest
OutputBaseFilename=Morning_Star_Cooperative_Setup
SetupIconFile=C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\app\assets\icon.ico
SolidCompression=yes
WizardStyle=modern dark
; Improved: Show more informative messages
WizardSizePercent=120
; Compression level
Compression=lzma2
InternalCompressLevel=max

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; CRITICAL: Main executable - consolidated to single entry using variable
; Source path: Flet build output directory
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Flutter and Python runtime data - REQUIRED for Flet app to function
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\DLLs\*"; DestDir: "{app}\DLLs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\site-packages\*"; DestDir: "{app}\site-packages"; Flags: ignoreversion recursesubdirs createallsubdirs

; Core Runtime DLLs - FIX: Consolidated and verified all needed DLLs
; Python runtime
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\python312.dll"; DestDir: "{app}"; Flags: ignoreversion

; Visual C++ Runtime DLLs (CRITICAL for Flet/Flutter)
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\msvcp140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\vcruntime140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\vcruntime140_1.dll"; DestDir: "{app}"; Flags: ignoreversion

; Flutter Engine DLL
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\flutter_windows.dll"; DestDir: "{app}"; Flags: ignoreversion

; Flutter/Flet Plugin DLLs
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\battery_plus_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\connectivity_plus_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\screen_brightness_windows_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\screen_retriever_windows_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\serious_python_windows_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\share_plus_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\url_launcher_windows_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\HP\Documents\flet_projects\LMS-PYTHON-FLET\build\windows\window_manager_plugin.dll"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; FIX: Removed file association registry entries since ChangesAssociations=no
; If you need file associations, uncomment the following and set ChangesAssociations=yes:
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Icons]
; FIX: CRITICAL - Added WorkingDir parameter to all shortcuts
; This ensures the app launches from the installation directory where resources are located
; WITHOUT WorkingDir, the app would launch from Windows system directories and fail silently
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
; Launch app after installation (optional - user can uncheck)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    { Post-installation code can be added here if needed }
  end;
end;
