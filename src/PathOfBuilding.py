"""
Path of Building main class

Sets up and connects external components.
External components are the status bar, toolbar (if exists), menus

Icons by  Yusuke Kamiyamane (https://p.yusukekamiyamane.com/)
"""
import atexit
import sys, re
from pathlib import Path
from pprint import pprint
import qdarktheme
from qdarktheme.qtpy.QtCore import QSize, QDir, QRect, QRectF, Qt, Slot, QEvent
from qdarktheme.qtpy.QtGui import (
    QAction,
    QActionGroup,
    QFont,
    QIcon,
    QPixmap,
    QBrush,
    QColor,
    QPainter,
)
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from qdarktheme.util import get_qdarktheme_root_path
from qdarktheme.widget_gallery.ui.dock_ui import DockUI
from qdarktheme.widget_gallery.ui.frame_ui import FrameUI
from qdarktheme.widget_gallery.ui.widgets_ui import WidgetsUI
from pob_config import Config, ColourCodes, _VERSION, program_title, PlayerClasses
# from build import Build
# from tree import Tree
# from tree_view import TreeView
# from tree_graphics_item import TreeGraphicsItem

# pyside6-uic main.ui -o pob_ui.py
from PoB_Main_Window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setupUi(self)
        # self.scroll = QScrollArea()
        # self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.setCentralWidget(self.scroll)

        self._theme = "dark"
        self._border_radius = "rounded"
        self._curr_class = PlayerClasses.SCION
        self.startPos = None

        self.config = Config(app, self)
        self.config.read()
        self.set_theme(self.config.theme == "Dark")

        atexit.register(self.exit_handler)
        self.setWindowTitle(program_title)  # Do not translate
        self.resize(self.config.size)

        # Add content to Colour Combo
        self.combo_Notes_Colour.addItems([colour.name.title() for colour in ColourCodes])

        # get the initial colour of the edit box for later use as 'NORMAL'
        self.defaultTextColour = self.textEdit_Notes.textColor()

        # set the ComboBox dropdown width.
        self.combo_Bandits.view().setMinimumWidth(
            self.combo_Bandits.minimumSizeHint().width()
        )

        # Connect our Actions
        self.combo_Notes_Font.currentFontChanged.connect(self.set_notes_font)
        self.spin_Notes_FontSize.valueChanged.connect(self.set_notes_font_size)
        self.combo_Notes_Colour.currentTextChanged.connect(self.set_notes_font_colour)
        self.tabWidget.currentChanged.connect(self.set_tab_focus)
        self.action_Theme.triggered.connect(self.set_theme)
        self.action_New.triggered.connect(self.build_new)
        self.action_Open.triggered.connect(self.build_open)
        self.action_Save.triggered.connect(self.build_save_as)

    def exit_handler(self):
        self.config.size = self.size()
        self.config.write()
        # Logic for checking we need to save and save if needed, goes here...
        # filePtr = open("edit.html", "w")
        # try:
        #     filePtr.write(self.textEdit_Notes.toHtml())
        # finally:
        #     filePtr.close()

    def close_app(self):
        self.close()

    @Slot()
    def build_new(self):
        # Logic for checking we need to save and save if needed, goes here...
        # if build.needs_saving:
        # if ui_utils.yes_no_dialog(app.tr("Save build"), app.tr("build name goes here"))
        if self.build.build is not None:
            if self.build.ask_for_save_if_modified():
                self.build.new()

    @Slot()
    def build_open(self):
        # Logic for checking we need to save and save if needed, goes here...
        # if build.needs_saving:
        # if ui_utils.yes_no_dialog(app.tr("Save build"), app.tr("build name goes here"))
        filename, selected_filter = QFileDialog.getOpenFileName(
            self,
            app.tr("Open a build"),
            str(self.config.buildPath),
            f"{app.tr('Build Files')} (*.xml)",
        )
        if filename != "":
            # open the file
            self.build.load(filename)
            if self.build.build is not None:
                self.config.add_recent_build(filename)

    @Slot()
    def build_save_as(self):
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

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_size(self, size):
        """
        Actions required for changing the TextEdit font size. Ensure that the TextEdit gets the focus back.
        :return: N/A
        """
        self.textEdit_Notes.setFontPointSize(size)
        self.textEdit_Notes.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_colour(self, colour_name):
        """
        Actions required for changing TextEdit font colour. Ensure that the TextEdit gets the focus back
        :param colour_name: String of the selected text
        :return: N/A
        """
        if colour_name == "NORMAL":
            self.textEdit_Notes.setTextColor(self.defaultTextColour)
        else:
            self.textEdit_Notes.setTextColor(ColourCodes[colour_name.upper()].value)
        self.textEdit_Notes.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font(self):
        """
        Actions required for changing the TextEdit font. Ensure that the TextEdit gets the focus back.
        :return: N/A
        """
        action = self.sender()
        self.textEdit_Notes.setCurrentFont(action.currentFont())
        self.textEdit_Notes.setFocus()

    @property
    def curr_class(self):
        return self._curr_class

    @curr_class.setter
    def curr_class(self, new_class):
        """
        Actions required for changing classes
        :param new_class: Integer representing the PlayerClasses enumerations
        :return:
        """
        # GUI Changes
        _class = self.right_pane.current_tree.classes[new_class]
        # Changing the ascendancy combobox, will trigger it's signal/slot.
        # This is good as it will set the ascendancy back to None
        self.ascendancy_combobox.clear()
        self.ascendancy_combobox.addItem("None", "None")
        for _ascendancy in _class["ascendancies"]:
            self.ascendancy_combobox.addItem(_ascendancy["name"])
        # build changes
        self._curr_class = new_class
        self.build.curr_class = new_class
        self.right_pane.tabTree.switch_class(new_class)

    @Slot()
    def change_class(self, selected_class):
        """
        Slot for the Classes combobox
        :param selected_class: String of the selected text
        :return:
        """
        self.curr_class = self.classes_combobox.currentData()

    @Slot()
    def change_ascendancy(self, selected_ascendancy):
        """
        Actions required for changing ascendancies
        :param selected_ascendancy: String of the selected text
        :return:
        """
        # "" will occur during a combobox clear
        if selected_ascendancy == "":
            return
        # "None" will occur when refilling the combobox or when the user chooses it
        if selected_ascendancy == "None":
            print(f"change_ascendancy: {selected_ascendancy}")
        else:
            print(f"change_ascendancy: {selected_ascendancy}")

    # Open a previous build as shown on the Build Menu
    @Slot()
    def _open_previous_build(self, bool, value, index):
        # Or does the logic for checking we need to save and save if needed, go here ???
        # if self.build.needs_saving:
        # if ui_utils.save_yes_no(app.tr("Save build"), app.tr("build name goes here"))
        # action = self.menubar.sender()
        # print(type(action))
        # open the file using the filename in the build.
        self.build.load(value)

    @Slot()
    def set_tab_focus(self, index):
        """
        When switching to a tab, set the focus to a control in the tab
        :param index: Which tab got selected (0 based)
        :return: N/A
        """
        # tab indexes are 0 based. Used by set_tab_focus
        self.tab_focus = {
            0: self.tabWidget,
            1: self.list_Skills,
            2: self.tabWidget,
            3: self.textEdit_Notes,
        }

        self.tab_focus.get(index).setFocus()

    # Do all actions needed to change between light and dark
    @Slot()
    def set_theme(self, new_theme):
        """
        Set the new theme based on the state of the action.
        The text of the action has a capital letter but the qdarktheme styles are all lowercase
        :param new_theme: Boolean state of the action
        :return: N/A
        """
        if new_theme:
            self._theme = "dark"
            self.action_Theme.setText("Light")
        else:
            self._theme = "light"
            self.action_Theme.setText("Dark")

        self.config.theme = new_theme
        QApplication.instance().setStyleSheet(
            qdarktheme.load_stylesheet(self._theme, self._border_radius)
        )

    # Setup menu entries for all valid recent builds in the settings file
    def set_recent_builds_menu_items(self, config: Config):

        # Lambdas in python share the variable scope they're created in
        # so make a function containing just the lambda
        def make_connection(v, i):
            _action.triggered.connect(
                lambda checked: self._open_previous_build(checked, v, i)
            )

        recent_builds = config.recent_builds()
        idx = 0
        for value in recent_builds.values():
            if value is not None and value != "":
                fn = re.sub(
                    ".xml", "", str(Path(value).relative_to(self.config.buildPath))
                )
                _action = self.menu_Builds.addAction(f"&{idx}.  {fn}")
                make_connection(value, idx)
                idx += 1


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
