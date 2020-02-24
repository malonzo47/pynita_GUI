pyinstaller --onefile --windowed --hidden-import pkg_resources.py2_warn pynita_gui_main.py
pause
#pyinstaller --onefile --windowed --icon icon.ico --add-data '/Library/Frameworks/Python.framework/Versions/3.7/lib/tcl8.6/':'tcl' --add-data '/Library/Frameworks/Python.framework/Versions/3.7/lib/tk8.6/':'tk' main.py