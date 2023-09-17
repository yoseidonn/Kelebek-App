# -*- mode: python ; coding: utf-8 -*-

block_cipher = None  # Encryption settings (optional)

# Import the necessary PyInstaller modules
from PyInstaller.utils.hooks import collect_submodules

# Define your Analysis
a = Analysis(['main.py'],  # List of entry point Python scripts
             pathex=['/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application'],  # List of paths to search for imports
             datas=[
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/App/*.py', './App'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/App/Frames/*.py', './App/Frames'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/App/HtmlCreater/*.py', './App/HtmlCreater'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/App/Themes/*.css', './App/Themes'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/Client/*.py', './Client'),
             
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/Forms/*.ui', './Forms'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/Images/icon/*.svg', './Images/icon'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/Images/img/*.png', './Images/img'),
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/resources.qrc', '.'),
             ],# Include data files             
             binaries=[
             ('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/Env/lib/python3.10/site-packages/PyQt5/Qt5/libexec/QtWebEngineProcess', '.')
             ],  # List of binary files to include
             )

# Define the Python archive (PYZ)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)  # Optional encryption

# Define the Executable (EXE)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='KelebekApp',
          # Add any other configuration options as needed
          )

# Define the Collection (COLLECT)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[('', path, '*.*') for path in collect_submodules('/home/yusuf/Belgeler/Projects/Software/Kelebek/BETA/Application/Env')],
               name='data'
               # Add any other configuration options as needed
               )

hiddenimports = [
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtPositioning',
    'sip'
    # Add any other related imports as needed
]

# Include additional hooks, hidden imports, or other customizations here

