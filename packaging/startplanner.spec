# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for StartPlanner (one-folder)."""

import sys

from PyInstaller.utils.hooks import collect_all

datas = [("../src/startplanner/resources/icon.png", "startplanner/resources")]
binaries = []
hiddenimports = ["fpdf", "openpyxl", "lxml"]

tmp_ret = collect_all("PySide6")
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ["../src/startplanner/main.py"],
    pathex=["../src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name="StartPlanner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity="-",
    entitlements_file=None,
    icon="icon.ico" if sys.platform == "win32" else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="StartPlanner",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="StartPlanner.app",
        icon="icon.icns",
        bundle_identifier="fi.startplanner.app",
    )
