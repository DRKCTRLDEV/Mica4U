@echo off
if "%1"=="install" goto :run
if "%1"=="uninstall" goto :run
echo Usage: initialise.cmd [install^|uninstall]
exit /b 1

:run
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process -FilePath '%~f0' -ArgumentList '%1' -Verb RunAs" >nul 2>&1
    exit /b
)
cd /d "%~dp0"

if "%1"=="install" (
    if exist "%~dp0ExplorerBlurMica.dll" (regsvr32 /s "%~dp0ExplorerBlurMica.dll") else (exit /b 1)
) else (
    if exist "%~dp0ExplorerBlurMica.dll" (regsvr32 /s /u "%~dp0ExplorerBlurMica.dll")
)
if %errorlevel% neq 0 (exit /b 1)

powershell -Command "$w=New-Object -ComObject WScript.Shell;Stop-Process -Name explorer -Force;Start-Sleep -s 2;$w.Run('explorer.exe')" >nul 2>&1
exit /b 0 