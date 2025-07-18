$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Variables
$version = if ($args.Count -ge 1) { $args[0] } else { "1.7.3" }
$buildDir = "build"

# Helper: Exit with message if not CI
function Exit-WithMessage($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
    if (-not $env:CI) { Read-Host "Press Enter to continue..." }
    exit 1
}

function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Write-Step($message) {
    Write-Host "[STEP] $message" -ForegroundColor Yellow
}

# Detect Python 3
Write-Step "Checking for Python 3..."
$pythonCmd = $null
foreach ($cmd in @("py -3", "python3", "python")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $ver -match "Python 3") {
            # Detect architecture
            $arch = & $cmd -c "import platform; print('x64' if platform.architecture()[0] == '64bit' else 'x86')" 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = $cmd
                Write-Info "Found Python: $ver ($cmd) ($arch)"
                break
            }
        }
    } catch {}
}
if (-not $pythonCmd) { Exit-WithMessage "Python 3 not found. Please install and add to PATH." }
Write-Info "Using Python command: $pythonCmd"

# Create virtual environment
Write-Step "Creating virtual environment..."
& $pythonCmd -m venv "$buildDir\venv" || Exit-WithMessage "Failed to create virtual environment."

# Upgrade pip and install dependencies
$pythonPath = Join-Path "$buildDir\venv" "Scripts\python.exe"
$pipPath = Join-Path "$buildDir\venv" "Scripts\pip.exe"
Write-Step "Upgrading pip..."
& $pythonPath -m pip install --upgrade pip || Exit-WithMessage "Failed to upgrade pip."
Write-Step "Installing Python dependencies (PyQt6, pyinstaller)..."
& $pipPath install PyQt6 pyinstaller || Exit-WithMessage "Failed to install Python dependencies."

# Update versions
Write-Step "Updating version in main.py and installer.iss..."
try {
    (Get-Content "main.py") -replace 'VERSION = ".*"', "VERSION = `"$version`"" | Set-Content "main.py"
    (Get-Content "$buildDir\installer.iss") -replace '#define Version ".*"', "#define Version `"$version`"" | Set-Content "$buildDir\installer.iss"
} catch {
    Exit-WithMessage "Failed to update version."
}

# Build executable
Write-Step "Building executable with PyInstaller..."
$pyinstallerPath = Join-Path "$buildDir\venv" "Scripts\pyinstaller.exe"
& $pyinstallerPath "$buildDir\Mica4U.spec" --distpath "$buildDir\dist" --workpath $env:TEMP || Exit-WithMessage "Failed to build executable."

# Build installer
Write-Step "Building installer with Inno Setup..."
iscc /O+ "$buildDir\installer.iss" || Exit-WithMessage "Failed to build installer."

# Create output dir
$outputDir = Join-Path $buildDir "output"
Write-Step "Creating output directory..."
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Create portable ZIP
Write-Step "Creating portable ZIP..."
$portableDir = Join-Path $outputDir "Mica4U"
New-Item -ItemType Directory -Path $portableDir -Force | Out-Null
Copy-Item "$buildDir\dist\Mica4U.exe" -Destination $portableDir
Copy-Item "LICENSE", "ExplorerBlurMica.dll" -Destination $portableDir

$unwantedFiles = @("config.ini", "mica4u.log")
foreach ($file in $unwantedFiles) {
    $target = Join-Path $portableDir $file
    if (Test-Path $target) { Remove-Item $target -Force }
}
Compress-Archive -Path $portableDir -DestinationPath "$outputDir\Mica4U_Portable.zip" -Force || Exit-WithMessage "Failed to create portable ZIP."

# Cleanup portable folder
Write-Step "Cleaning up temporary portable files..."
Remove-Item -Recurse -Force $portableDir

# Final cleanup (preserve .iss and .spec)
Write-Step "Final cleanup of build directory..."
Get-ChildItem $buildDir |
    Where-Object { $_.Name -notlike "*.iss" -and $_.Name -notlike "*.spec" -and $_.Name -ne "output" } |
    Remove-Item -Recurse -Force

Write-Host "[SUCCESS] Build completed successfully." -ForegroundColor Green
exit 0