# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['../main.py'],
    pathex=['../'],
    binaries=[],
    datas=[
        ('../icon.ico', '.'),
        ('../assets/icons/*', 'assets/icons')
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt6.QtMultimedia',
        'PyQt6.QtSql',
        'PyQt6.QtNetwork',
        'PyQt6.QtOpenGL',
        'PyQt6.QtWebEngine',
        'PyQt6.QtDesigner',
        'PyQt6.QtTest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

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
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'msvcp140.dll',
        'python3.dll'
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    codesign_identity=None,
    entitlements_file=None,
    icon='../icon.ico',
    onefile=True,
    uac_admin=True
)