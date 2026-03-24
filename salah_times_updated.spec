# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['ultra_modern_salah.py'],
    pathex=[],
    binaries=[],
    datas=[('display_features_fixed.py', '.')],
    hiddenimports=['PyQt5.QtPrintSupport', 'gi', 'gi.repository.AyatanaAppIndicator3', 'gi.repository.Gtk', 'gi.repository.GLib', 'gi.repository.GObject'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='SalahTimes',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='SalahTimes',
)
