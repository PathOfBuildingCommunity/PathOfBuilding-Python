import sys  # Only needed for access to command line arguments
import atexit

import qdarktheme
from qdarktheme.qtpy.QtCore import QDir, QSize, Qt, Slot
from qdarktheme.qtpy.QtGui import QAction, QActionGroup, QFont, QIcon
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QColorDialog,
    QDialogButtonBox,
    QFileDialog,
    QFontDialog,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QWidget,
)
from qdarktheme.util import get_qdarktheme_root_path
from qdarktheme.widget_gallery.ui.dock_ui import DockUI
from qdarktheme.widget_gallery.ui.frame_ui import FrameUI
from qdarktheme.widget_gallery.ui.widgets_ui import WidgetsUI

from pob_ui import PoB_UI
from pob_config import Config, color_codes
from Build import Build

import ui_utils


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle("Path of Building")  # Do not translate
        self.config = Config()
        self.config.read_config()
        self.resize(self.config.size())
        atexit.register(self.exit_handler)
        # enable again if you want icons,
        # QDir.addSearchPath("icons", f"{get_qdarktheme_root_path().as_posix()}/widget_gallery/svg")
        self._ui = PoB_UI(self, self.config)
        self._theme = "dark"
        self._border_radius = "rounded"
        self.build = Build()

        # Connect actions
        for action in self._ui.actions_theme:
            action.triggered.connect(self._change_theme)
        self._ui.actions_theme_dark_light.triggered.connect(self._change_theme2)
        self._ui.action_exit.triggered.connect(self._close_app)
        self._ui.action_open.triggered.connect(self._build_open)
        recents = self.config.recentBuilds()
        menu_builds = self._ui.menu_builds
        for value in recents.values():
            # print("value: %s" % value)
            if value != "-":
                # print("value: %s" % value)
                _action = QAction(value)
                _action.triggered.connect(self._open_previous_build)
                menu_builds.addAction(_action)

    def exit_handler(self):
        self.config.set_size(self.size())
        self.config.write_config()
        # Logic for checking we need to save and save if needed, goes here...
        # filePtr = open("edit.html", "w")
        # try:
        #     filePtr.write(self.notes_text_edit.toHtml())
        # finally:
        #     filePtr.close()

    @Slot()
    def _close_app(self):
        self.close()

    def _open_previous_build(self):
        # Or does the logic for checking we need to save and save if needed, go here ???
        # if build.needs_saving:
        # if ui_utils.save_yes_no(app.tr("Save build"), app.tr("build name goes here"))
        action = self.sender()
        print(action.text())
        # open the file using the filename in the build.
        # build.load_build(filename)

    @Slot()
    def _build_open(self):
        # Logic for checking we need to save and save if needed, goes here...
        # if build.needs_saving:
        # if ui_utils.yes_no_dialog(app.tr("Save build"), app.tr("build name goes here"))
        filename, selected_filter = QFileDialog.getOpenFileName(
            self,
            app.tr("Open a build"),
            self.config.buildPath,
            app.tr("Build Files (*.xml)"),
        )
        if filename != "":
            # print("filename: %s" % filename)
            # print("selected_filter: %s" % selected_filter)
            # open the file
            self.build.load_build(filename)

    @Slot()
    def _build_save_as(self):
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            app.tr("Save File"),
            app.tr("Save build"),
            self.config.buildPath,
            app.tr("Build Files (*.xml)"),
        )
        if filename != "":
            print("filename: %s" % filename)
            # print("selected_filter: %s" % selected_filter)
            # write the file
            # build.save_build(filename)

    # Tech Demo. Two menu items to change theme
    @Slot()
    def _change_theme(self) -> None:
        action = self.sender()
        self._theme = action.text()
        # print(action.text())
        QApplication.instance().setStyleSheet(
            qdarktheme.load_stylesheet(self._theme, self._border_radius)
        )

    # Tech Demo. Switch just one menu item
    @Slot()
    def _change_theme2(self) -> None:
        action = self._ui.actions_theme_dark_light
        if action.text() == "Dark":
            self._theme = "dark"
            action.setText("Light")
        else:
            self._theme = "light"
            action.setText("Dark")
        QApplication.instance().setStyleSheet(
            qdarktheme.load_stylesheet(self._theme, self._border_radius)
        )


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.menuBar().setNativeMenuBar(False)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window.show()
    app.exec()
