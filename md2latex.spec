# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# En Linux usamos onedir (bundle tar.gz); en Windows/macOS onefile.
_onefile = sys.platform != 'linux'

# Icono: Windows requiere .ico (None hasta generarlo), Linux/macOS acepta .png
_icon = None if sys.platform == 'win32' else 'assets/logo.png'

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
    a.binaries if _onefile else [],
    a.datas    if _onefile else [],
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

# En Linux generamos el directorio con todas las libs (onedir)
if not _onefile:
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='md2latex',
    )
