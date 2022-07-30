"""
Path of Building main class

Sets up and connects external components.
External components are the status bar, toolbar (if exists), menus

Icons by  Yusuke Kamiyamane (https://p.yusukekamiyamane.com/)
"""
import atexit
import sys
import qdarktheme
from qdarktheme.qtpy.QtCore import Qt, Slot
from qdarktheme.qtpy.QtGui import QFont
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QSpinBox,
    QWidget,
)

from pob_config import *
from build import Build

from player_stats import PlayerStats
from calcs_ui import CalcsUI
from config_ui import ConfigUI
from items_ui import ItemsUI
from notes_ui import NotesUI
from skills_ui import SkillsUI
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
        self.start_pos = None
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
        self.stats = PlayerStats(self.config)
        self.calcs_ui = CalcsUI(self.config)
        self.config_ui = ConfigUI(self.config)
        self.items_ui = ItemsUI(self.config)
        self.notes_ui = NotesUI(self.config)
        self.skills_ui = SkillsUI(self.config)
        self.tree_ui = TreeUI(self.config, self.frame_TreeTools)

        """
            Start: Do what the QT Designer cannot yet do 
        """
        # add widgets to the Toolbar
        widget_spacer = QWidget()  # spacers cannot go into the toolbar, only Widgets
        widget_spacer.setMinimumSize(10, 0)
        self.toolbar_MainWindow.insertWidget(self.action_Theme, widget_spacer)
        widget_spacer = QWidget()
        widget_spacer.setMinimumSize(50, 0)
        self.toolbar_MainWindow.addWidget(widget_spacer)
        self.label_points = QLabel()
        self.label_points.setMinimumSize(100, 0)
        self.label_points.setText(" 0 / 123  0 / 8 ")
        self.label_points.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.toolbar_MainWindow.addWidget(self.label_points)
        label_level = QLabel()
        label_level.setText("Level: ")
        self.toolbar_MainWindow.addWidget(label_level)
        self.spin_level = QSpinBox()
        self.spin_level.setMinimum(1)
        self.spin_level.setMaximum(100)
        self.toolbar_MainWindow.addWidget(self.spin_level)

        widget_spacer = QWidget()
        widget_spacer.setMinimumSize(100, 0)
        self.toolbar_MainWindow.addWidget(widget_spacer)

        self.combo_classes = QComboBox()
        self.combo_classes.setMinimumSize(100, 0)
        self.combo_classes.setDuplicatesEnabled(False)
        # self.combo_classes.setInsertPolicy(QComboBox.InsertAlphabetically)
        for idx in PlayerClasses:
            self.combo_classes.addItem(idx.name.title(), idx)
        self.toolbar_MainWindow.addWidget(self.combo_classes)
        self.combo_ascendancy = QComboBox()
        self.combo_ascendancy.setMinimumSize(100, 0)
        self.combo_ascendancy.setDuplicatesEnabled(False)
        self.combo_ascendancy.addItem("None", "None")
        self.toolbar_MainWindow.addWidget(self.combo_ascendancy)

        # Dump the placeholder Graphics View and add our own
        self.gview_Tree = TreeView(self.config, self.build)
        self.vlayout_tabTree.replaceWidget(
            self.graphicsView_PlaceHolder, self.gview_Tree
        )
        # destroy the old object
        self.graphicsView_PlaceHolder.setParent(None)

        """
            End: Do what the QT Designer cannot yet do 
        """

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
        self.default_notes_text_colour = self.textedit_Notes.textColor()

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
        self.tab_main.currentChanged.connect(self.set_tab_focus)
        self.action_Theme.triggered.connect(self.set_theme)
        self.action_New.triggered.connect(self.build_new)
        self.action_Open.triggered.connect(self.build_open)
        self.action_Save.triggered.connect(self.build_save_as)
        self.action_ManageTrees.triggered.connect(self.tree_ui.open_manage_trees)
        self.combo_Bandits.currentTextChanged.connect(self.change_bandits)

        self.combo_classes.currentTextChanged.connect(self.tree_ui.change_class)
        self.combo_ascendancy.currentTextChanged.connect(self.tree_ui.change_ascendancy)
        self.tree_ui.combo_manage_tree.currentTextChanged.connect(self.change_tree)
        self.tree_ui.textEdit_Search.textChanged.connect(self.search_text_changed)
        self.tree_ui.textEdit_Search.returnPressed.connect(self.search_return_pressed)

        # setup Scion by default, and this will trigger it's correct ascendancy to appear in combo_ascendancy
        # ToDo: check to see if there is a previous build to load and load it before this
        self.build_loader("Default")
        self.tree_ui.change_class("Scion")

    def exit_handler(self):
        """
        Ensure the build can be saved before exiting if needed.
        Save the configuration to settings.xml
        Any other activities that might be needed
        """
        self.config.size = self.size()

        self.config.write()
        # Logic for checking we need to save and save if needed, goes here...
        # filePtr = open("edit.html", "w")
        # try:
        #     filePtr.write(self.textedit_Notes.toHtml())
        # finally:
        #     filePtr.close()

    @Slot()
    def close_app(self):
        """
        Trigger closing of the app. May not get used anymore as action calls MainWindow.close()
        Kept here in case it's more sensible to run 'close down' procedures in an App that doesn't think it's closing.
            In which case, change the action back to here.
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
            print(self.build.className, self.build.ascendClassName)
            self.combo_classes.setCurrentText(self.build.className)
            self.combo_ascendancy.setCurrentText(self.build.ascendClassName)
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

    @Slot()
    def change_tree(self, tree_id):
        """
        Actions required when the combo_manage_tree widget changes
        :param tree_id: Current text string. We don't use it.
        :return: N/A
        """
        self.build.change_tree(self.tree_ui.combo_manage_tree.currentData())
        self.gview_Tree.add_tree_images()
        # update label_points
        self.change_bandits(self.combo_Bandits.currentText())
        # ToDo: change class...
        self.combo_classes.setCurrentIndex(self.build.current_spec.classId.value)
        print(
            "change_tree",
            self.build.current_spec.ascendClassId,
            type(self.build.current_spec.ascendClassId),
        )

        self.combo_ascendancy.setCurrentIndex(
            self.build.current_spec.ascendClassId is None
            and 0
            or int(self.build.current_spec.ascendClassId)
        )

    @Slot()
    def change_bandits(self, bandit_id):
        """
        Actions required when the combo_manage_tree widget changes
        :param bandit_id: Current text string. We don't use it.
        :return: N/A
        """
        self.build.bandit = self.combo_Bandits.currentData()
        max_points = self.build.bandit == "None" and 123 or 121
        self.label_points.setText(
            f" {len(self.build.current_spec.nodes)} / {max_points}  0 / 8 "
        )

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_size(self, _size):
        """
        Actions required for changing the TextEdit font size. Ensure that the TextEdit gets the focus back.
        :return: N/A
        """
        self.textedit_Notes.setFontPointSize(_size)
        self.textedit_Notes.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_colour(self, colour_name):
        """
        Actions required for changing TextEdit font colour. Ensure that the TextEdit gets the focus back
        :param colour_name: String of the selected text
        :return: N/A
        """
        if colour_name == "NORMAL":
            self.textedit_Notes.setTextColor(self.default_notes_text_colour)
        else:
            self.textedit_Notes.setTextColor(ColourCodes[colour_name.upper()].value)
        self.textedit_Notes.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font(self):
        """
        Actions required for changing the TextEdit font. Ensure that the TextEdit gets the focus back.
        :return: N/A
        """
        action = self.sender()
        self.textedit_Notes.setCurrentFont(action.currentFont())
        self.textedit_Notes.setFocus()

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

    @Slot()
    def set_tab_focus(self, index):
        """
        When switching to a tab, set the focus to a control in the tab
        :param index: Which tab got selected (0 based)
        :return: N/A
        """
        # tab indexes are 0 based. Used by set_tab_focus
        tab_focus = {
            0: self.tab_main,
            1: self.list_Skills,
            2: self.tab_main,
            3: self.textedit_Notes,
            4: self.tab_main,
            5: self.tab_main,
        }

        # Focus a Widget
        tab_focus.get(index).setFocus()
        # update the build
        self.build.current_tab = self.tab_main.tabWhatsThis(
            self.tab_main.currentIndex()
        )
        # Turn on / off actions as needed
        self.action_ManageTrees.setVisible(self.build.current_tab == "TREE")

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

    def search_text_changed(self):
        self.build.search_text = self.tree_ui.textEdit_Search.text()
        print("search_text_changed", self.build.search_text)

    def search_return_pressed(self):
        self.gview_Tree.add_tree_images()
        print("search_return_pressed", self.build.search_text)


# Start here
app = QApplication(sys.argv)
font = QFont()
font.setFamily("Lucida Sans Typewriter")
app.setFont(font)

window = MainWindow(app)
window.show()
app.exec()
