# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
datas=[('C:\\Users\\Administrator\\PycharmProjects\\spider_image_system\\src\\gui\\config\\config.ini','.')]

a = Analysis(
    ['ui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('C:\\Users\\Administrator\\PycharmProjects\\spider_image_system\\src\\utils','utils'),
     ('C:\\Users\\Administrator\\PycharmProjects\\spider_image_system\\src\\log','log')
    ],
    hiddenimports=["PyQt5","numpy","opencv-python","loguru","configparser","selenium","requests"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='sis_v1.0.1_beta',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico'
)