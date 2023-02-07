# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['/Users/chgnhyk/Desktop/Fragma-fbs/src/main/python/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['/Users/chgnhyk/Desktop/Fragma-fbs/venv/lib/python3.10/site-packages/fbs/freeze/hooks'],
    hooksconfig={},
    runtime_hooks=['/Users/chgnhyk/Desktop/Fragma-fbs/target/PyInstaller/fbs_pyinstaller_hook.py'],
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
    [],
    exclude_binaries=True,
    name='Fragma',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/chgnhyk/Desktop/Fragma-fbs/target/Icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Fragma',
)
app = BUNDLE(
    coll,
    name='Fragma.app',
    icon='/Users/chgnhyk/Desktop/Fragma-fbs/target/Icon.icns',
    bundle_identifier='com.chgnhyk.fragmaapp',
)
