# nuitka-project: --standalone
# nuitka-project: --onefile
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --clean-cache=all
# nuitka-project: --debug
# nuitka-project: --trace
# nuitka-project: --experimental=disable-freelist-all

# MRE test for Nuitka pySide6 connections

import sys
from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from dialogs.browse_file_dialog import BrowseFileDlg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setFixedSize(QSize(600, 600))

        # Set the central widget of the Window.
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.menubar_MainWindow = QMenuBar(self)
        self.menu_Builds = QMenu(self.menubar_MainWindow)
        self.menubar_MainWindow.addAction(self.menu_Builds.menuAction())
        self.menu_Builds.setTitle("&Builds")
        self.menu_Builds.addSeparator()
        self.set_recent_builds_menu_items()

        self.vlayout = QVBoxLayout(self.centralwidget)

        self.list = QListWidget()
        for idx in range(0, 15):
            lwi = QListWidgetItem(f"Item {idx}")
            lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
            self.list.addItem(lwi)
        self.list.setAlternatingRowColors(True)
        self.list.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.vlayout.addWidget(self.list)

        self.list.currentItemChanged.connect(self.on_row_changed)
        self.list.itemClicked.connect(self.on_row_changed)
        self.list.itemDoubleClicked.connect(self.item_list_double_clicked)

    def set_recent_builds_menu_items(self):
        """
        Setup menu entries for all valid recent builds in the settings file
        Read the config for recent builds and create menu entries for them
        return: N/A
        """

        def make_connection(_full_path):
            """
            Connect the menu item to _open_previous_build passing in extra information
            Lambdas in python share the variable scope they're created in so make a function containing just the lambda
            :param _full_path: full path to the file, to be sent to the triggered function.
            :return: N/A
            """
            _action.triggered.connect(lambda checked: self._open_previous_build(checked, _full_path))

        for idx in range(10):
            text = f"Item {idx}"
            ql = QLabel(text)
            _action = QWidgetAction(self.menu_Builds)
            _action.setDefaultWidget(ql)
            self.menu_Builds.addAction(_action)
            make_connection(text)

    @Slot()
    def _open_previous_build(self, checked, full_path):
        """
        React to a previous build being selected from the "Build" menu.

        :param checked: Boolean: a value for if it's checked or not, always False
        :param full_path: String: Fullpath name of the build to load
        :return: N/A
        """
        # open the file using the filename in the build.
        print("_open_previous_build", full_path)
        dlg = BrowseFileDlg("Open", self)
        dlg.exec()

    @Slot()
    def item_list_double_clicked(self, lwi: QListWidgetItem):
        print("item_list_double_clicked", lwi.text())

    @Slot()
    def on_row_changed(self, item):
        print("on_row_changed", item)


app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()

# Start the event loop.
app.exec()
