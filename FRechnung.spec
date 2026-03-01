# invoice_master.spec
# PyInstaller-Konfiguration für FRechnung
# Ausführen mit: pyinstaller invoice_master.spec

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Alle Frontend-Dateien einsammeln
frontend_files = [
    ("frontend", "frontend"),          # (Quelle, Ziel im Bundle)
]

# Versteckte Imports (Flask/pywebview-Abhängigkeiten)
hidden_imports = [
    "webview",
    "webview.platforms.winforms",      # Windows-Backend
    "clr",
    "flask",
    "flask_cors",
    "jinja2",
    "markupsafe",
    "werkzeug",
    "werkzeug.serving",
    "werkzeug.debug",
    "click",
    "itsdangerous",
    "reportlab",
    "reportlab.pdfgen",
    "reportlab.lib",
    "reportlab.platypus",
    "PIL",
    "PIL.Image",
]

a = Analysis(
    ["main.py"],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=frontend_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "customtkinter", "matplotlib", "numpy", "pandas"],
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
    a.zipfiles,
    a.datas,
    [],
    name="InvoiceMaster",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # kein schwarzes CMD-Fenster
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/FRechnung.ico",   # ← Icon-Pfad hier eintragen (optional)
)
