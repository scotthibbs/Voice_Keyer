# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['voice_keyer_tts.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'sounddevice', 'soundfile', 'numpy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Voice_Keyer_TTS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
