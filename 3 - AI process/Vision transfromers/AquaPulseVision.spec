# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\parsa\\Desktop\\Code\\3 - AI process\\Vision transfromers\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\parsa\\Desktop\\Code\\3 - AI process\\Vision transfromers\\fish_model.pt', '.')],
    hiddenimports=['ultralytics', 'langchain_ollama', 'pyttsx3', 'pyttsx3.drivers', 'pyttsx3.drivers.sapi5'],
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
    [],
    exclude_binaries=True,
    name='AquaPulseVision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AquaPulseVision',
)
