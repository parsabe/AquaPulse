# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

script_dir = os.path.abspath(r"C:\Users\parsa\Desktop\Code\3 - AI process")

datas = [
    (os.path.join(script_dir, "models", "*.pt"), "models"),
    (os.path.join(script_dir, "johnny.gif"), "."),
    (os.path.join(script_dir, "report_template.tex"), "."),
    (os.path.join(script_dir, "aquapulse_system_architecture_documentation.tex"), "."),
]

datas += collect_data_files('ultralytics')

hiddenimports = [
    'ultralytics',
    'ultralytics.models',
    'ultralytics.models.yolo',
    'ultralytics.nn',
    'ultralytics.nn.modules',
    'ultralytics.utils',
    'torch',
    'torchvision',
    'cv2',
    'numpy',
    'scipy',
    'scipy.optimize',
    'scipy.stats',
    'scipy.signal',
    'scipy.ndimage',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'moviepy',
    'imageio',
    'imageio_ffmpeg',
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'win32com',
    'win32com.client',
    'requests',
    'langchain_ollama',
    'tkinter',
    'tkinter.filedialog',
    'mod_00_config_and_assets',
    'mod_01_eco_census',
    'mod_02_stochastic_enkf',
    'mod_03_chart_renderer',
    'mod_04_vision_engine',
    'mod_05_dialogue_and_ollama',
    'mod_06_ui_dashboard',
    'mod_07_pdf_exporter',
    'manual_botsort',
]

hiddenimports += collect_submodules('ultralytics')

a = Analysis(
    [os.path.join(script_dir, 'main.py')],
    pathex=[script_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib.tests', 'numpy.tests'],
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
    name='AquaPulse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AquaPulse_App',
)
