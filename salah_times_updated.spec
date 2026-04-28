# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('app', 'app')],
    hiddenimports=[
        'PyQt5.QtPrintSupport',
        'gi',
        'gi.repository.AyatanaAppIndicator3',
        'gi.repository.Gtk',
        'gi.repository.GLib',
        'gi.repository.GObject',
        'app.constants',
        'app.database',
        'app.worker',
        'app.dialogs',
        'app.views',
        'app.window',
        'app.tray',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SalahTimes',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
