@echo off
echo Building Mica4U...

:: Create compile directory if it doesn't exist
if not exist "compiled" (
    mkdir "compiled"
    :: Move or copy necessary files to compile directory if they don't exist there
    if exist "Mica4U.spec" copy "Mica4U.spec" "compiled\"
    if exist "installer.iss" copy "installer.iss" "compiled\"
)

:: Set working directory to compile
cd compiled

:: Ask about cleanup
set /p CLEANUP="Do you want to clean up previous builds? (Y/N): "
if /i "%CLEANUP%"=="Y" (
    echo Cleaning up previous builds...
    :: Clean dist folder
    if exist "dist" rd /s /q "dist"
    :: Clean build folder
    if exist "build" rd /s /q "build"
    :: Clean installer folder
    if exist "installer" rd /s /q "installer"
)

:: Create PyInstaller build using spec file
echo Creating executable with PyInstaller...
pyinstaller Mica4U.spec

:: Check if PyInstaller succeeded
if %errorlevel% neq 0 (
    echo PyInstaller build failed!
    cd ..
    pause
    exit /b 1
)

:: Create installer directory
if not exist "installer" mkdir "installer"

:: Compile Inno Setup
echo Creating installer with Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer.iss"

:: Check if Inno Setup succeeded
if %errorlevel% neq 0 (
    echo Inno Setup compilation failed!
    cd ..
    pause
    exit /b 1
)

echo Build completed successfully!
echo Installer can be found in the 'compiled\installer' directory.
cd ..
pause 