"""
Path of Building main class

Sets up and connects external components.
External components are the status bar, toolbar (if exists), menus

Icons by  Yusuke Kamiyamane (https://p.yusukekamiyamane.com/)
"""
import sys

from typing import Union
import xml.etree.ElementTree as ET

import qdarktheme
from qdarktheme.qtpy.QtGui import QFontDatabase, QFont
from qdarktheme.qtpy.QtWidgets import QApplication

from windows.main_window import MainWindow

# Start here
# sys.stdout = open("PathOfBuilding.log", 'a')
app = QApplication(sys.argv)

# font for stats box. To line things up, we need a Mono font.
QFontDatabase.addApplicationFont(":/Font/Font/NotoSansMono-Regular.ttf")
# system wide font
QApplication.setFont(QFont(":Font/Font/NotoSans-Regular.ttf", 9))

window = MainWindow(app)
window.show()
window.setup_ui()
app.exec()
