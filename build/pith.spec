# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for PITH.

Produces a single-file executable with all required dependencies.
Schemas ship separately — they are NOT bundled here.
"""

import platform
from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata("pithhq")

block_cipher = None

ROOT = Path(SPECPATH).parent

# Collect pith submodules
pith_tree = Path(ROOT / "pith")
pith_modules = []
for p in pith_tree.rglob("*.py"):
    rel = p.relative_to(ROOT)
    module = str(rel.with_suffix("")).replace("/", ".").replace("\\", ".")
    pith_modules.append(module)

hidden_imports = [
    "pdfplumber",
    "pytesseract",
    "docx",
    "openpyxl",
    "pandas",
    "pptx",
    "git",
    "httpx",
    "typer",
    "pydantic",
    "fpdf2",
    "yaml",
]

datas = []
binaries = []

# Windows: bundle portable git
if platform.system() == "Windows":
    git_vendor = ROOT / "build" / "vendor" / "git-windows"
    if git_vendor.exists():
        binaries.append((str(git_vendor / "*"), "git"))

a = Analysis(
    [str(ROOT / "pith" / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports + pith_modules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tests", "schemas", "tkinter", "_tkinter"],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pith",
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="pith",
)
