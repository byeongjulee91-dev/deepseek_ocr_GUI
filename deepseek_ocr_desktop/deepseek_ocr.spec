# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DeepSeek-OCR Desktop Application
Builds a standalone executable with all dependencies
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Path to src directory
src_dir = os.path.abspath('src')

# Collect data files
datas = [
    # QSS stylesheet
    (os.path.join(src_dir, 'resources', 'styles', 'app.qss'), 'resources/styles'),
]

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # Application modules (collected automatically)
    *collect_submodules('core'),
    *collect_submodules('ui'),
    *collect_submodules('utils'),

    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',

    # Transformers and dependencies
    'transformers',
    'transformers.models.auto',
    'transformers.models.auto.modeling_auto',
    'transformers.models.auto.tokenization_auto',
    'tokenizers',

    # PyTorch
    'torch',
    'torch.nn',
    'torch.cuda',

    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',

    # PDF processing
    'fitz',
    'img2pdf',

    # Document conversion
    'docx',
    'markdown',

    # OpenAI for vLLM
    'openai',

    # Other dependencies
    'numpy',
    'safetensors',
]

# Binaries to exclude (reduce size)
# Note: Do NOT exclude 'unittest' - PyTorch requires it internally
excludes = [
    # Development tools
    'pytest',
    # 'unittest',  # PyTorch needs this!
    'test',
    'tests',

    # Documentation
    'sphinx',
    'IPython',
    'jupyter',

    # Unused libraries
    'matplotlib',
    'scipy',
    'pandas',
]

a = Analysis(
    [os.path.join(src_dir, 'main.py')],
    pathex=[src_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    name='DeepSeek-OCR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file here if available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DeepSeek-OCR',
)

# Note: Model files (~5-10GB) are NOT included in the bundle
# They will be downloaded on first run to ~/.cache/huggingface/
