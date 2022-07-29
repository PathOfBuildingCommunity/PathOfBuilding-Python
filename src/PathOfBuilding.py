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
from qdarktheme.qtpy.QtCore import (
    QCoreApplication,
    QDir,
    QRect,
    QRectF,
    QSize,
    Qt,
    Slot,
)
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
    QCheckBox,
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
    QPushButton,
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

from pob_config import *
from build import Build

from tree_ui import TreeUI
from tree_view import TreeView

# from tree_graphics_item import TreeGraphicsItem

# pyside6-uic Assets\PoB_Main_Window.ui -o src\PoB_Main_Window.py
from PoB_Main_Window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, _app) -> None:
        # def __init__(self, screen_rect) -> None:
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self._theme = "dark"
        self._border_radius = "rounded"
        self.startPos = None
        atexit.register(self.exit_handler)
        self.setWindowTitle(program_title)  # Do not translate

        self.config = Config(self, _app)
        self.config.read()
        self.resize(self.config.size)

        self.set_theme(self.config.theme == "Dark")
        self.action_Theme.setChecked(self.config.theme == "Dark")

        # Start with an empty build
        self.build = Build(self.config)

        # Setup UI Classes()
        self.tree_ui = TreeUI(self.config, self.frame_TreeTools)

        """ Start: Do what the QT Designer cannot yet do """
        # add widgets to the Toolbar
        toolbar_spacer1 = QWidget()
        toolbar_spacer1.setMinimumSize(10, 0)
        self.toolBar_MainWindow.insertWidget(self.action_Theme, toolbar_spacer1)
        toolbar_spacer1 = QWidget()
        toolbar_spacer1.setMinimumSize(50, 0)
        self.toolBar_MainWindow.addWidget(toolbar_spacer1)
        self.label_points = QLabel()
        self.label_points.setMinimumSize(100, 0)
        self.label_points.setText(" 0 / 123  0 / 8 ")
        self.label_points.setAlignment(Qt.AlignCenter)
        self.toolBar_MainWindow.addWidget(self.label_points)
        label_level = QLabel()
        label_level.setText("Level: ")
        self.toolBar_MainWindow.addWidget(label_level)
        self.spin_level = QSpinBox()
        self.spin_level.setMinimum(1)
        self.spin_level.setMaximum(100)
        self.toolBar_MainWindow.addWidget(self.spin_level)
        self.combo_classes = QComboBox()
        self.combo_classes.setMinimumSize(100, 0)
        self.combo_classes.setDuplicatesEnabled(False)
        # self.combo_classes.setInsertPolicy(QComboBox.InsertAlphabetically)
        for idx in PlayerClasses:
            self.combo_classes.addItem(idx.name.title(), idx)

        toolbar_spacer1 = QWidget()
        toolbar_spacer1.setMinimumSize(100, 0)
        self.toolBar_MainWindow.addWidget(toolbar_spacer1)
        self.toolBar_MainWindow.addWidget(self.combo_classes)
        self.combo_ascendancy = QComboBox()
        self.combo_ascendancy.setMinimumSize(100, 0)
        self.combo_ascendancy.setDuplicatesEnabled(False)
        self.combo_ascendancy.addItem("None", "None")
        self.toolBar_MainWindow.addWidget(self.combo_ascendancy)

        # Dump the placeholder tab and add our own
        self.gview_Tree = TreeView(self.config, self.build)
        self.vLayout_tabTree.replaceWidget(
            self.graphicsView_PlaceHolder, self.gview_Tree
        )
        self.graphicsView_PlaceHolder.setParent(None)

        """ End: Do what the QT Designer cannot yet do """

        self.build_loader("Default")
        # self.set_current_tab()

        self.combo_Bandits.clear()
        for name in bandits.keys():
            self.combo_Bandits.addItem(bandits[name], name)
        self.combo_MajorGods.clear()
        for name in pantheon_major_gods.keys():
            self.combo_MajorGods.addItem(pantheon_major_gods[name], name)
        self.combo_MinorGods.clear()
        for name in pantheon_minor_gods.keys():
            self.combo_MinorGods.addItem(pantheon_minor_gods[name], name)

        # Add content to Colour ComboBox
        self.combo_Notes_Colour.addItems(
            [colour.name.title() for colour in ColourCodes]
        )

        # get the initial colour of the edit box for later use as 'NORMAL'
        self.default_notes_text_colour = self.textEdit_Notes.textColor()

        # set the ComboBox dropdown width.
        self.combo_Bandits.view().setMinimumWidth(
            self.combo_Bandits.minimumSizeHint().width()
        )

        self.menu_Builds.addSeparator()
        self.set_recent_builds_menu_items(self.config)

        # Connect our Actions
        self.combo_Notes_Font.currentFontChanged.connect(self.set_notes_font)
        self.spin_Notes_FontSize.valueChanged.connect(self.set_notes_font_size)
        self.combo_Notes_Colour.currentTextChanged.connect(self.set_notes_font_colour)
        self.tabWidget.currentChanged.connect(self.set_tab_focus)
        self.action_Theme.triggered.connect(self.set_theme)
        self.action_New.triggered.connect(self.build_new)
        self.action_Open.triggered.connect(self.build_open)
        self.action_Save.triggered.connect(self.build_save_as)
        self.combo_ascendancy.currentTextChanged.connect(self.tree_ui.change_ascendancy)
        self.combo_classes.currentTextChanged.connect(self.tree_ui.change_class)
        self.tree_ui.combo_manage_tree.currentTextChanged.connect(self.tree_ui.change_tree)
        self.action_ManageTrees.triggered.connect(self.tree_ui.open_manage_trees)

        # setup Scion by default, and this will trigger it's correct ascendancy to appear in combo_ascendancy
        self.tree_ui.change_class("Scion")

    def exit_handler(self):
        """
        Ensure the build can be saved before exiting if needed.
        Save the configuration to settings.xml
        Any other activiites that might be needed
        """
        self.config.size = self.size()

        self.config.write()
        # Logic for checking we need to save and save if needed, goes here...
        # filePtr = open("edit.html", "w")
        # try:
        #     filePtr.write(self.textEdit_Notes.toHtml())
        # finally:
        #     filePtr.close()

    def close_app(self):
        """
        Trigger closing of the app. May not get used anymore
        return: N/A
        """
        self.close()

    @Slot()
    def build_new(self):
        """
        React to the New action
        :return: N/A
        """
        # Logic for checking we need to save and save if needed, goes here...
        # if build.needs_saving:
        # if ui_utils.yes_no_dialog(app.tr("Save build"), app.tr("build name goes here"))
        if self.build.build is not None:
            if not self.build.ask_for_save_if_modified():
                return
        self.build_loader("Default")

    @Slot()
    def build_open(self):
        """
        React to the Open action and prompt the user to open a build
        :return: N/A
        """
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
            self.build_loader(filename)

    # Open a previous build as shown on the Build Menu
    @Slot()
    def _open_previous_build(self, checked, value, index):
        """
        React to a previous build being selected from the "Build" menu
        :param checked: Boolean: a value for if it's checked or not, always False
        :param value: String: Fullpath name of the build to load
        :param index: Integer: index of chosen menu item
        :return: N/A
        """
        # Or does the logic for checking we need to save and save if needed, go here ???
        # if self.build.needs_saving:
        # if ui_utils.save_yes_no(app.tr("Save build"), app.tr("build name goes here"))

        # open the file using the filename in the build.
        self.build_loader(value)

    def build_loader(self, filename):
        """
        Common actions for UI components when we are loading a build
        :param filename: String: the filename of file that was loaded, or "Default" if called from the New action
        :return: N/A
        """
        # open the file
        new = filename == "Default"
        if not new:
            self.build.load(filename)
        else:
            self.build.new(empty_build)

        if self.build.build is not None:
            if not new:
                self.config.add_recent_build(filename)
            self.tree_ui.set_current_tab()
            self.tree_ui.fill_current_tree_combo()
            self.spin_level.setValue(self.build.level)
            self.combo_classes.setCurrentText(self.build.className)
            self.combo_ascendancy.setCurrentText(self.build.ascendClassName)
            # print(f"{self.build.bandit}, {self.build.pantheonMajorGod}, {self.build.pantheonMinorGod}")
            # self.combo_Bandits.setCurrentText(self.build.bandit)
            # self.combo_MajorGods.setCurrentText(self.build.pantheonMajorGod)
            # self.combo_MinorGods.setCurrentText(self.build.pantheonMinorGod)
            for i in range(self.combo_Bandits.count()):
                if self.combo_Bandits.itemData(i) == self.build.bandit:
                    self.combo_Bandits.setCurrentIndex(i)
                    break
            for i in range(self.combo_MajorGods.count()):
                if self.combo_MajorGods.itemData(i) == self.build.pantheonMajorGod:
                    self.combo_MajorGods.setCurrentIndex(i)
                    break
            for i in range(self.combo_MinorGods.count()):
                if self.combo_MinorGods.itemData(i) == self.build.pantheonMinorGod:
                    self.combo_MinorGods.setCurrentIndex(i)
                    break

    @Slot()
    def build_save_as(self):
        """
        Actions required to get a filename to save a build to. Should call build_save() if user doesn't cancel
        return: N/A
        """
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
            self.textEdit_Notes.setTextColor(self.default_notes_text_colour)
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

    # Do all actions needed to change between light and dark
    @Slot()
    def set_theme(self, new_theme):
        """
        Set the new theme based on the state of the action.
        The text of the action has a capital letter but the qdarktheme styles are lowercase
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
        """
        Read the config for recent builds and create menu entries for them
        return: N/A
        """

        # Lambdas in python share the variable scope they're created in
        # so make a function containing just the lambda
        def make_connection(v, i):
            _action.triggered.connect(
                lambda checked: self._open_previous_build(checked, v, i)
            )

        recent_builds = config.recent_builds()
        for idx, value in enumerate(recent_builds.values()):
            if value is not None and value != "":
                fn = re.sub(
                    ".xml", "", str(Path(value).relative_to(self.config.buildPath))
                )
                _action = self.menu_Builds.addAction(f"&{idx}.  {fn}")
                make_connection(value, idx)

    @Slot()
    def set_tab_focus(self, index):
        """
        When switching to a tab, set the focus to a control in the tab
        :param index: Which tab got selected (0 based)
        :return: N/A
        """
        # tab indexes are 0 based. Used by set_tab_focus
        tab_focus = {
            0: self.tabWidget,
            1: self.list_Skills,
            2: self.tabWidget,
            3: self.textEdit_Notes,
            4: self.tabWidget,
            5: self.tabWidget,
        }

        # Focus a Widget
        tab_focus.get(index).setFocus()
        # update the build
        self.build.current_tab = self.tabWidget.tabWhatsThis(
            self.tabWidget.currentIndex()
        )
        # Turn on / off actions as needed
        self.action_ManageTrees.setVisible(self.build.current_tab == "TREE")


# Start here
app = QApplication(sys.argv)
font = QFont()
font.setFamily("Lucida Sans Typewriter")
app.setFont(font)

window = MainWindow(app)
window.show()
app.exec()
