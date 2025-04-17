@echo off
set ACTION=%1
if "%ACTION%"=="" set ACTION=install

net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c %~dpnx0 %ACTION%' -Verb RunAs -WindowStyle Hidden"
    exit /b
)

rem Verify DLL exists
if not exist "%~dp0ExplorerBlurMica.dll" (
    echo ERROR: DLL file not found at "%~dp0ExplorerBlurMica.dll"
    exit /b 1
)

set OPERATION_SUCCEEDED=1

if "%ACTION%"=="uninstall" (
    echo Unregistering DLL...
    regsvr32 /s /u "%~dp0ExplorerBlurMica.dll"
    if %errorlevel% neq 0 set OPERATION_SUCCEEDED=0
) else if "%ACTION%"=="restart" (
    echo Restarting Explorer only...
    set OPERATION_SUCCEEDED=1
) else (
    echo Registering DLL...
    regsvr32 /s "%~dp0ExplorerBlurMica.dll"
    if %errorlevel% neq 0 set OPERATION_SUCCEEDED=0
)

if %OPERATION_SUCCEEDED% equ 1 (
    echo Restarting Explorer...
    taskkill /F /IM explorer.exe >nul 2>&1
    if %errorlevel% neq 0 (
        echo Warning: Failed to kill Explorer process, changes may not apply until restart.
    ) else (
        start /B explorer.exe
        timeout /t 2 >nul
        echo Explorer restarted.
    )
    exit /b 0
) else (
    echo Operation failed.
    exit /b 1
) 