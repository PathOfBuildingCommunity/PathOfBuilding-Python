"""Path of Building main class, sets up and connects external components.

External components are the status bar, toolbar (if exists), menus.
"""

import atexit

import qdarktheme
from qdarktheme.qtpy.QtCore import QSize, Slot
from qdarktheme.qtpy.QtGui import QAction
from qdarktheme.qtpy.QtWidgets import QApplication, QFileDialog, QMainWindow

from pob_ui import PobUi
from pob_config import Config
from build import Build


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle("Path of Building")
        self.build = Build()
        self.config = Config()
        self.config.read()
        print("config", self.config)
        self.resize(self.config.size())
        # enable again if you want icons,
        # QDir.addSearchPath("icons", f"{get_qdarktheme_root_path().as_posix()}/widget_gallery/svg")
        self._ui = PobUi(self, self.config)
        self._ui.build = self.build
        self._theme = "dark"
        self._border_radius = "rounded"
        atexit.register(self.exit_handler)
        # Connect actions
        for action in self._ui.actions_theme:
            action.triggered.connect(self._change_theme)
        self._ui.actions_theme_dark_light.triggered.connect(self._change_theme2)
        self._ui.action_exit.triggered.connect(self._close_app)
        self._ui.action_open.triggered.connect(self._build_open)
        recent_builds = self.config.recentBuilds()
        menu_builds = self._ui.menu_builds
        for value in recent_builds.values():
            if value:
                _action = QAction(value)
                _action.triggered.connect(self._open_previous_build)
                menu_builds.addAction(_action)

    def exit_handler(self):
        self.config.set_size(self.size())
        self.config.write()
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
        # open the file using the filename in the build.
        # build.load_build(filename)

    @Slot()
    def _build_open(self):
        # Logic for checking we need to save and save if needed, goes here...
        # if build.needs_saving:
        # if ui_utils.yes_no_dialog(app.tr("Save build"), app.tr("build name goes here"))
        file_name, selected_filter = QFileDialog.getOpenFileName(
            self,
            app.tr("Open a build"),
            self.config.build_path,
            app.tr("Build Files (*.xml)"),
        )
        if file_name:
            self.build.load(file_name)

    @Slot()
    def _build_save_as(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self,
            app.tr("Save File"),
            app.tr("Save build"),
            self.config.build_path,
            app.tr("Build Files (*.xml)"),
        )
        if file_name:
            self.build.save(file_name)

    # Tech Demo. Two menu items to change theme
    @Slot()
    def _change_theme(self) -> None:
        action = self.sender()
        self._theme = action.text()
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
