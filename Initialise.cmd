@echo off
set ACTION=%1
if "%ACTION%"=="" set ACTION=install

net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c %~dpnx0 %ACTION%' -Verb RunAs"
    exit /b
)

if "%ACTION%"=="uninstall" (
    regsvr32 /s /u "%~dp0ExplorerBlurMica.dll"
) else (
    regsvr32 /s "%~dp0ExplorerBlurMica.dll"
)

if %errorlevel% == 0 (
    taskkill /F /IM explorer.exe >nul
    start explorer.exe
    timeout /t 2 >nul
    exit /b 0
) else (
    exit /b 1
) 