# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# Icono por plataforma: Windows requiere .ico, macOS .icns, Linux .png
if sys.platform == 'win32':
    _icon = None          # sin icono hasta generar un .ico
elif sys.platform == 'darwin':
    _icon = 'assets/logo.png'
else:
    _icon = 'assets/logo.png'

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets',          'assets'),
        ('language_colors', 'language_colors'),
        ('editor_colors',   'editor_colors'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinterweb',
        'markdown',
        'markdown.extensions',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
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
    a.datas,
    [],
    name='md2latex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)
