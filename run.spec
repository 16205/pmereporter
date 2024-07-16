# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=['C:\\Users\\Gabriel\\Workspace\\pmereporter\\', 'C:\\Users\\Gabriel\\Workspace\\pmereporter\\app\\', 'C:\\Users\\Gabriel\\Workspace\\pmereporter\\modules\\', 'C:\\Users\\Gabriel\\Workspace\\pmereporter\\temp\\', 'C:\\Users\\Gabriel\\Workspace\\pmereporter\\media\\', 'C:\\Users\\Gabriel\\Workspace\\pmereporter\\ui\\'],
    binaries=[],
    datas=[
        ('media/*', 'media'),  # Include the media folder and its contents
        ('ui/*.py', 'ui'),  # Include all Python files in the ui folder
        ('modules/*.py', 'modules'),  # Include all Python files in the modules folder
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PMEReporter',
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
    icon='./media/icon.png',
)