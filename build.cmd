@echo off
cls
setlocal enabledelayedexpansion

:: Enable ANSI color support
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

:: Define ANSI color codes using PowerShell
for /f "delims=" %%a in ('powershell -Command "[char]27"') do set "ESC=%%a"
set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"

:: Check for verbose flag
set "VERBOSE=false"
if "%1"=="-v" set "VERBOSE=true"
if "%1"=="--verbose" set "VERBOSE=true"

:: Build Configuration
set "BUILD_VERSION=1.6.8"
set "LOG_FILE=build.log"
set "BUILD_DIR=compiled"
set "OUTPUT_DIR=%BUILD_DIR%\output"
set "DIST_DIR=%BUILD_DIR%\dist"
set "BUILD_TEMP=%BUILD_DIR%\build"
set "INSTALLER_DIR=%BUILD_DIR%\installer"

echo %BOLD%%BLUE%Starting Mica4U build process v%BUILD_VERSION%...%RESET%
echo %BOLD%%BLUE%----------------------------------------%RESET%

:: Initialize logging
echo [%date% %time%] Starting build process (Version %BUILD_VERSION%) > "%CD%\%LOG_FILE%"

echo %BOLD%%YELLOW%[1/6]%RESET% %CYAN%Updating version information...%RESET%
call :update_version
if errorlevel 1 (
    echo %BOLD%%RED%ERROR: Version update failed! Check %LOG_FILE% for details.%RESET%
    exit /b 1
)

echo %BOLD%%YELLOW%[2/6]%RESET% %CYAN%Cleaning previous build files...%RESET%
call :cleanup
if errorlevel 1 (
    echo %BOLD%%RED%ERROR: Cleanup failed! Check %LOG_FILE% for details.%RESET%
    exit /b 1
)

echo %BOLD%%YELLOW%[3/6]%RESET% %CYAN%Building application...%RESET%
if "%VERBOSE%"=="true" (
    call :build_verbose
) else (
    call :build
)
if errorlevel 1 (
    echo %BOLD%%RED%ERROR: Build failed! Check %LOG_FILE% for details.%RESET%
    exit /b 1
)

echo %BOLD%%YELLOW%[4/6]%RESET% %CYAN%Creating portable version...%RESET%
call :create_portable
if errorlevel 1 (
    echo %BOLD%%RED%ERROR: Portable version creation failed! Check %LOG_FILE% for details.%RESET%
    exit /b 1
)

echo %BOLD%%YELLOW%[5/6]%RESET% %CYAN%Creating installer...%RESET%
call :create_installer
if errorlevel 1 (
    echo %BOLD%%RED%ERROR: Installer creation failed! Check %LOG_FILE% for details.%RESET%
    exit /b 1
)

echo %BOLD%%YELLOW%[6/6]%RESET% %CYAN%Performing final cleanup...%RESET%
call :final_cleanup
if errorlevel 1 (
    echo %BOLD%%RED%ERROR: Final cleanup failed! Check %LOG_FILE% for details.%RESET%
    exit /b 1
)

echo.
echo %BOLD%%GREEN%Build completed successfully!%RESET%
echo %BOLD%%BLUE%----------------------------------------%RESET%
echo %CYAN%The portable version can be found in: %OUTPUT_DIR%%RESET%
if exist "%OUTPUT_DIR%\Mica4U_Setup.exe" (
    echo %CYAN%The installer can be found in: %OUTPUT_DIR%%RESET%
)
echo.
pause
exit /b 0

:cleanup
echo [%date% %time%] Cleaning up previous build... >> "%CD%\%LOG_FILE%"
if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Cleaning up previous build...%RESET%
)
for %%d in ("%OUTPUT_DIR%" "%DIST_DIR%" "%BUILD_TEMP%" "%INSTALLER_DIR%") do (
    if exist "%%~d" (
        if "%VERBOSE%"=="true" echo %MAGENTA%[LOG]%RESET% %CYAN%Removing directory: %%~d%RESET%
        rmdir /s /q "%%~d" 2>> "%CD%\%LOG_FILE%"
        if errorlevel 1 (
            echo [%date% %time%] Failed to remove directory: %%~d >> "%CD%\%LOG_FILE%"
            exit /b 1
        )
    )
)
exit /b 0

:build
echo [%date% %time%] Building application... >> "%CD%\%LOG_FILE%"
cd "%BUILD_DIR%"
pyinstaller Mica4U.spec --clean 2>> "%CD%\..\%LOG_FILE%"
if errorlevel 1 (
    echo [%date% %time%] PyInstaller build failed! >> "%CD%\..\%LOG_FILE%"
    exit /b 1
)
cd ..
exit /b 0

:build_verbose
echo [%date% %time%] Building application... >> "%CD%\%LOG_FILE%"
cd "%BUILD_DIR%"
echo %MAGENTA%[LOG]%RESET% %CYAN%Running PyInstaller...%RESET%
pyinstaller Mica4U.spec --clean 2>&1 | tee -a "%CD%\..\%LOG_FILE%"
if errorlevel 1 (
    echo [%date% %time%] PyInstaller build failed! >> "%CD%\..\%LOG_FILE%"
    exit /b 1
)
cd ..
exit /b 0

:create_portable
echo [%date% %time%] Creating portable version... >> "%CD%\%LOG_FILE%"
if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Creating portable version directories...%RESET%
)
if not exist "%OUTPUT_DIR%\portable\Mica4U" mkdir "%OUTPUT_DIR%\portable\Mica4U" 2>> "%CD%\%LOG_FILE%"
if errorlevel 1 exit /b 1

:: Create portable.ini file
echo [Settings] > "%OUTPUT_DIR%\portable\Mica4U\portable.ini"
echo Version=%BUILD_VERSION% >> "%OUTPUT_DIR%\portable\Mica4U\portable.ini"
echo Portable=true >> "%OUTPUT_DIR%\portable\Mica4U\portable.ini"

:: Copy files in parallel using start
if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Copying files to portable directory...%RESET%
    start /b /wait cmd /c "copy "%DIST_DIR%\Mica4U.exe" "%OUTPUT_DIR%\portable\Mica4U\" 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "README.md" "%OUTPUT_DIR%\portable\Mica4U\" 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "LICENSE" "%OUTPUT_DIR%\portable\Mica4U\" 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "ExplorerBlurMica.dll" "%OUTPUT_DIR%\portable\Mica4U\" 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "initialise.cmd" "%OUTPUT_DIR%\portable\Mica4U\" 2>> "%CD%\%LOG_FILE%"""
) else (
    start /b /wait cmd /c "copy "%DIST_DIR%\Mica4U.exe" "%OUTPUT_DIR%\portable\Mica4U\" >nul 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "README.md" "%OUTPUT_DIR%\portable\Mica4U\" >nul 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "LICENSE" "%OUTPUT_DIR%\portable\Mica4U\" >nul 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "ExplorerBlurMica.dll" "%OUTPUT_DIR%\portable\Mica4U\" >nul 2>> "%CD%\%LOG_FILE%"""
    start /b /wait cmd /c "copy "initialise.cmd" "%OUTPUT_DIR%\portable\Mica4U\" >nul 2>> "%CD%\%LOG_FILE%"""
)

:: Wait for all copy operations to complete
powershell -Command "Start-Sleep -Seconds 2" >nul

if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Creating portable zip archive...%RESET%
)

:: Check if 7-Zip is installed
where 7z >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] 7-Zip not found. Using built-in zip command... >> "%CD%\%LOG_FILE%"
    if "%VERBOSE%"=="true" (
        echo %MAGENTA%[LOG]%RESET% %CYAN%Using built-in zip command...%RESET%
    )
    powershell -Command "Add-Type -Assembly 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('%OUTPUT_DIR%\portable\Mica4U', '%OUTPUT_DIR%\Mica4U_portable.zip')" 2>> "%CD%\%LOG_FILE%"
) else (
    if "%VERBOSE%"=="true" (
        echo %MAGENTA%[LOG]%RESET% %CYAN%Using 7-Zip...%RESET%
        echo %MAGENTA%[LOG]%RESET% %CYAN%Creating archive...%RESET%
        cd "%OUTPUT_DIR%\portable\Mica4U"
        7z a -tzip "..\..\Mica4U_portable.zip" "*" -mx9 -r
        cd ..\..\..\..
    ) else (
        cd "%OUTPUT_DIR%\portable\Mica4U"
        7z a -tzip "..\..\Mica4U_portable.zip" "*" -mx9 -r >nul 2>> "%CD%\%LOG_FILE%"
        cd ..\..\..\..
    )
)

if errorlevel 1 (
    echo [%date% %time%] Failed to create portable zip >> "%CD%\%LOG_FILE%"
    exit /b 1
)

if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Cleaning up temporary portable files...%RESET%
)
rmdir /s /q "%OUTPUT_DIR%\portable" 2>> "%CD%\%LOG_FILE%"
exit /b 0

:create_installer
echo [%DATE% %TIME%] Creating installer... >> "%CD%\%LOG_FILE%"

if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Creating installer using Inno Setup...%RESET%
    iscc "%BUILD_DIR%\installer.iss" /O"%OUTPUT_DIR%" /F"Mica4U_Setup"
) else (
    iscc "%BUILD_DIR%\installer.iss" /O"%OUTPUT_DIR%" /F"Mica4U_Setup" >nul 2>> "%CD%\%LOG_FILE%"
)

if errorlevel 1 (
    echo %BOLD%%RED%[%DATE% %TIME%]%RESET% Error creating installer. Check %OUTPUT_DIR%\Setup.log for details.
    echo [%DATE% %TIME%] Error creating installer. Check %OUTPUT_DIR%\Setup.log for details. >> "%CD%\%LOG_FILE%"
    exit /b 1
)

echo [%DATE% %TIME%] Installer created successfully. >> "%CD%\%LOG_FILE%"
goto :eof

:final_cleanup
echo [%date% %time%] Cleaning up temporary files... >> "%CD%\%LOG_FILE%"
if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Cleaning up temporary build files...%RESET%
)
for %%d in ("%DIST_DIR%" "%BUILD_TEMP%" "%INSTALLER_DIR%") do (
    if exist "%%~d" (
        if "%VERBOSE%"=="true" echo %MAGENTA%[LOG]%RESET% %CYAN%Removing directory: %%~d%RESET%
        rmdir /s /q "%%~d" 2>> "%CD%\%LOG_FILE%"
        if errorlevel 1 (
            echo [%date% %time%] Failed to remove directory: %%~d >> "%CD%\%LOG_FILE%"
            exit /b 1
        )
    )
)
exit /b 0

:update_version
echo [%date% %time%] Updating version in main.py... >> "%CD%\%LOG_FILE%"
if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Updating version in main.py...%RESET%
)
powershell -Command "(Get-Content 'main.py') -replace 'VERSION = \"[0-9]+\.[0-9]+\.[0-9]+\"', 'VERSION = \"%BUILD_VERSION%\"' | Set-Content 'main.py'"
if errorlevel 1 (
    echo [%date% %time%] Failed to update version in main.py >> "%CD%\%LOG_FILE%"
    exit /b 1
)

if "%VERBOSE%"=="true" (
    echo %MAGENTA%[LOG]%RESET% %CYAN%Updating version in installer.iss...%RESET%
)
echo [%date% %time%] Updating version in installer.iss... >> "%CD%\%LOG_FILE%"
powershell -Command "(Get-Content 'compiled\installer.iss') -replace '#define MyAppVersion \"[0-9]+\.[0-9]+\.[0-9]+\"', '#define MyAppVersion \"%BUILD_VERSION%\"' | Set-Content 'compiled\installer.iss'"
if errorlevel 1 (
    echo [%date% %time%] Failed to update version in installer.iss >> "%CD%\%LOG_FILE%"
    exit /b 1
)
exit /b 0 