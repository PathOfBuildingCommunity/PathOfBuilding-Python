# nuitka-project: --onefile
# nuitka-project: --standalone
# nuitka-project: --onefile-windows-splash-screen-image=PathOfBuilding.png
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-data-dir=src/data=data
# nuitka-project: --windows-icon-from-ico=Assets/Icons/PathOfBuilding.ico
# nuitka-project: --onefile-tempdir-spec="%TEMP%/PoB_%PID%"
# nuitka-project: --onefile-no-compression
# nuitka-project: --quiet
# nuitka-project: --clean-cache=all

"""
Path of Building main class

Sets up and connects external components.
External components are the status bar, toolbar (if exists), menus

Icons by  Yusuke Kamiyamane (https://p.yusukekamiyamane.com/)
Splashscreen by https://creator.nightcafe.studio
"""
import os
import sys

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from windows.main_window import MainWindow

# Start here
# This is  NUITKA debugging info so folk can understand the diffference between the extracted directory and
# the directory the Executable was run from:
# print("os.getcwd", os.getcwd())
# if "NUITKA_ONEFILE_PARENT" in os.environ:
#     print("TEMP: ", os.environ["TEMP"])
#     print("NUITKA_ONEFILE_PARENT: ", os.environ["NUITKA_ONEFILE_PARENT"])

# Logging to a file, not spam to screen or get lost if no console
# ToDo: Remove comment when we stop building.
# sys.stdout = open("PathOfBuilding.log", 'a')

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
main_app = QApplication(sys.argv)

# font for stats box. To line things up, we need a Mono font. (could use <pre> now that I know it exists. PSH 20230802)
QFontDatabase.addApplicationFont(":/Font/Font/NotoSansMono-Regular.ttf")
# system wide font
QApplication.setFont(QFont(":Font/Font/NotoSans-Regular.ttf", 9))

window = MainWindow(main_app)
window.show()
window.setup_ui()
main_app.exec()