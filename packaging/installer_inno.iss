; Inno Setup Script for NCAA Volleyball Match Predictor
[Setup]
AppName=NCAA Volleyball Match Predictor
AppVersion=1.0
AppPublisher=AI/ML Sports Analytics
DefaultDirName={autopf}\VolleyballPredictor
DefaultGroupName=NCAA Volleyball Predictor
OutputDir=dist
OutputBaseFilename=VolleyballPredictor_Setup_x64
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\VolleyballPredictor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NCAA Volleyball Predictor"; Filename: "{app}\VolleyballPredictor.exe"
Name: "{autodesktop}\NCAA Volleyball Predictor"; Filename: "{app}\VolleyballPredictor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VolleyballPredictor.exe"; Description: "{cm:LaunchProgram,NCAA Volleyball Predictor}"; Flags: nowait postinstall skipifsilent
