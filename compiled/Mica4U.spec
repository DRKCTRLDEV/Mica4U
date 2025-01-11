# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['..\\main.py'],
    pathex=[
        '..\\',  # Add the root directory
        '..\\utils',
        '..\\config',
        '..\\gui'
    ],
    binaries=[],
    datas=[
        ('..\\ExplorerBlurMica.dll', '.'),
        ('..\\icon.ico', '.'),
        ('..\\Initialise.cmd', '.'),
        ('..\\resources', 'resources'),
        ('..\\utils', 'utils'),
        ('..\\config', 'config'),
        ('..\\gui', 'gui')
    ],
    hiddenimports=[
        'utils',
        'utils.logging_config',
        'utils.system',
        'config',
        'config.config_manager',
        'config.constants',
        'gui',
        'gui.widgets',
        'gui.main_window'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Mica4U',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='..\\icon.ico',
    onefile=True
)
