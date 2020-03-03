# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files
_osgeo_pyds = collect_data_files('osgeo', include_py_files=True)

osgeo_pyds = []
for p, lib in _osgeo_pyds:
    if '.pyd' in p:
        osgeo_pyds.append((p, ''))

binaries = osgeo_pyds + [
    # your binaries if any
]


a = Analysis(['pynita_gui_main.py'],
             pathex=['/Users/kelvin/Desktop/PCK/pynita_GUI'],
             binaries=binaries,
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.binaries = a.binaries - TOC([('libpng16.16.dylib',None,None)])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='pynita_gui_main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='pynita_gui_main.app',
             icon=None,
             bundle_identifier=None)
