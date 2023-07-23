import re, os, platform, atexit, sys, datetime, pyperclip

from typing import Union
import xml.etree.ElementTree as ET
from pathlib import Path
import psutil

import qdarktheme
from qdarktheme.qtpy.QtCore import Qt, Slot
from qdarktheme.qtpy.QtGui import QFontDatabase, QFont
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QSpinBox,
    QWidget,
)

from constants import (
    PlayerClasses,
    bandits,
    empty_build,
    pantheon_major_gods,
    pantheon_minor_gods,
    pob_debug,
    program_title,
    resistance_penalty,
)
from ui_utils import html_colour_text, set_combo_index_by_data
from pob_config import Config, _debug, index_exists, print_a_xml_element
from flow_layout import FlowLayout
from build import Build

from player_stats import PlayerStats
from widgets.calcs_ui import CalcsUI
from widgets.config_ui import ConfigUI
from widgets.items_ui import ItemsUI
from widgets.notes_ui import NotesUI
from widgets.skills_ui import SkillsUI
from widgets.tree_ui import TreeUI
from tree_view import TreeView
from dialogs.import_dialog import ImportDlg
from dialogs.export_dialog import ExportDlg

from views.PoB_Main_Window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, _app) -> None:
        super(MainWindow, self).__init__()
        print(
            f"{datetime.datetime.now()}. {program_title}, running on {platform.system()} {platform.release()}; {platform.version()}"
        )
        self.app = _app
        self._os = platform.system()
        # self.loader = QUiLoader()
        # ToDo investigate if some settings need to be changed per o/s

        self.setupUi(self)
        # When False stop all the images being deleted and being recreated
        self.refresh_tree = True

        self._theme = "dark"
        self._border_radius = "rounded"
        self.start_pos = None
        # Flag to stop some actions happening in triggers during loading
        self.loading = False

        self.max_points = 123
        self.config = Config(self, _app)
        self.resize(self.config.size)
        self.switch_theme(self.config.theme == "Dark")
        self.action_Theme.setChecked(self.config.theme == "Dark")
        atexit.register(self.exit_handler)
        self.setWindowTitle(program_title)  # Do not translate

        # Start with an empty build
        self.build = Build(self.config, self)

        # Setup UI Classes()
        self.stats = PlayerStats(self.config, self)
        self.calcs_ui = CalcsUI(self.config, self)
        self.config_ui = ConfigUI(self.config, self.build, self)
        self.items_ui = ItemsUI(self.config, self)
        self.notes_ui = NotesUI(self.config, self)
        self.skills_ui = SkillsUI(self.config, self.build, self)
        self.tree_ui = TreeUI(self.config, self.frame_TreeTools, self)

        # share the goodness
        self.build.gems_by_name_or_id = self.skills_ui.gems_by_name_or_id

        """
            Start: Do what the QT Designer cannot yet do 
        """
        # Remove the space that the icon reserves. If you want check boxes or icons, then delete this section
        # This could be a pydarktheme issue as against the pyside6 / designer
        # ToDo: Is it best to put this in QTdesigner or here (currently in designer)
        # self.menubar_MainWindow.setStyleSheet(
        #     "QMenu {padding-left: 0px;}"
        #     "QMenu::item {padding-left: 0px;}"
        #     "QMenu::item:selected {background-color: rgb(0, 85, 127);color: rgb(255, 255, 255);}"
        #     "QAction {padding-left: 0px;}"
        # )
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
        for idx in PlayerClasses:
            self.combo_classes.addItem(idx.name.title(), idx)
        self.toolbar_MainWindow.addWidget(self.combo_classes)
        self.combo_ascendancy = QComboBox()
        self.combo_ascendancy.setMinimumSize(100, 0)
        self.combo_ascendancy.setDuplicatesEnabled(False)
        self.combo_ascendancy.addItem("None", 0)
        self.combo_ascendancy.addItem("Ascendant", 1)
        self.toolbar_MainWindow.addWidget(self.combo_ascendancy)
        # end add widgets to the Toolbar

        # Dump the placeholder Graphics View and add our own
        # Cannot be set in TreeUI() init due to recursion error.
        self.gview_Tree = TreeView(self, self.config, self.build)
        self.vlayout_tabTree.replaceWidget(self.graphicsView_PlaceHolder, self.gview_Tree)
        # destroy the old object
        self.graphicsView_PlaceHolder.setParent(None)

        # Add our FlowLayout to Config tab
        self.layout_config = FlowLayout(None, 0)
        self.frame_Config.setLayout(self.layout_config)
        self.layout_config.addItem(self.grpbox_General)
        self.layout_config.addItem(self.grpbox_Combat)
        self.layout_config.addItem(self.grpbox_SkillOptions)
        self.layout_config.addItem(self.grpbox_EffectiveDPS)
        self.layout_config.addItem(self.grpbox_5)
        self.layout_config.addItem(self.grpbox_6)

        # set the ComboBox dropdown width.
        self.combo_Bandits.view().setMinimumWidth(self.combo_Bandits.minimumSizeHint().width())

        """
            End: Do what the QT Designer cannot yet do 
        """

        self.combo_ResPenalty.clear()
        for penalty in resistance_penalty.keys():
            self.combo_ResPenalty.addItem(resistance_penalty[penalty], penalty)
        self.combo_Bandits.clear()
        for idx, bandit_name in enumerate(bandits.keys()):
            bandit_info = bandits[bandit_name]
            self.combo_Bandits.addItem(bandit_info.get("name"), bandit_name)
            self.combo_Bandits.setItemData(
                idx,
                html_colour_text("TANGLE", bandit_info.get("tooltip")),
                Qt.ToolTipRole,
            )
        self.combo_MajorGods.clear()
        for idx, god_name in enumerate(pantheon_major_gods.keys()):
            god_info = pantheon_major_gods[god_name]
            self.combo_MajorGods.addItem(god_info.get("name"), god_name)
            self.combo_MajorGods.setItemData(idx, html_colour_text("TANGLE", god_info.get("tooltip")), Qt.ToolTipRole)
        self.combo_MinorGods.clear()
        for idx, god_name in enumerate(pantheon_minor_gods.keys()):
            god_info = pantheon_minor_gods[god_name]
            self.combo_MinorGods.addItem(god_info.get("name"), god_name)
            self.combo_MinorGods.setItemData(idx, html_colour_text("TANGLE", god_info.get("tooltip")), Qt.ToolTipRole)

        self.menu_Builds.addSeparator()
        self.set_recent_builds_menu_items(self.config)

        # Connect our Actions / triggers
        self.tab_main.currentChanged.connect(self.set_tab_focus)
        self.action_Theme.triggered.connect(self.switch_theme)
        self.action_New.triggered.connect(self.build_new)
        self.action_Open.triggered.connect(self.build_open)
        self.action_Save.triggered.connect(self.build_save_as)
        # self.action_ManageTrees.triggered.connect(self.tree_ui.open_manage_trees)
        self.action_Settings.triggered.connect(self.config.open_settings_dialog)
        self.action_Import.triggered.connect(self.open_import_dialog)
        self.action_Export.triggered.connect(self.open_export_dialog)
        self.statusbar_MainWindow.messageChanged.connect(self.update_status_bar)

        self.combo_Bandits.currentTextChanged.connect(self.display_number_node_points)
        self.combo_classes.currentTextChanged.connect(self.class_changed)
        self.combo_ascendancy.currentTextChanged.connect(self.ascendancy_changed)
        self.combo_MainSkill.currentTextChanged.connect(self.main_skill_text_changed)
        self.combo_MainSkill.currentIndexChanged.connect(self.main_skill_index_changed)
        self.combo_MainSkillActive.currentTextChanged.connect(self.active_skill_changed)
        self.tree_ui.combo_manage_tree.currentTextChanged.connect(self.change_tree)

        # Start the statusbar self updating
        self.update_status_bar()

        # setup Scion by default, and this will trigger it's correct ascendancy to appear in combo_ascendancy
        # and other ui's to display properly
        # ToDo: check to see if there is a previous build to load and load it here
        self.build_loader("Default")

        """
        From time to time, comboBoxes don't show the correct colours. It could be because of changing the
            width of the dropdowns. So reapply the current theme in an attempt to force the correct colours.
        """
        # don't use self.switch_theme
        QApplication.instance().setStyleSheet(qdarktheme.load_stylesheet(self._theme, self._border_radius))

    def setup_ui(self):
        """Called after show(). Call setup_ui for all UI classes that need it"""
        self.items_ui.setup_ui()

    def exit_handler(self):
        """
        Ensure the build can be saved before exiting if needed.
        Save the configuration to settings.xml. Any other activities that might be needed
        """
        self.config.size = self.size()
        self.config.write()
        # Logic for checking we need to save and save if needed, goes here...
        # filePtr = open("edit.html", "w")
        # try:
        #     filePtr.write(self.textedit_Notes.toHtml())
        # finally:
        #     filePtr.close()
        sys.stdout.close()

    @Slot()
    def close_app(self):
        """
        Trigger closing of the app. May not get used anymore as action calls MainWindow.close().
        Kept here in case it's more sensible to run 'close down' procedures in an App that doesn't think it's closing.
            In which case, change the action back to here.

        return: N/A
        """
        self.close()

    @Slot()
    def build_new(self):
        """
        React to the New action.

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
        React to the Open action and prompt the user to open a build.

        :return: N/A
        """
        # Logic for checking we need to save and save if needed, goes here...
        # if build.needs_saving:
        # if ui_utils.yes_no_dialog(app.tr("Save build"), app.tr("build name goes here"))
        filename, selected_filter = QFileDialog.getOpenFileName(
            self,
            self.app.tr("Open a build"),
            str(self.config.build_path),
            f"{self.app.tr('Build Files')} (*.xml)",
        )
        if filename != "":
            self.build_loader(filename)

    # Open a previous build as shown on the Build Menu
    @Slot()
    def _open_previous_build(self, checked, value, index):
        """
        React to a previous build being selected from the "Build" menu.

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

    def build_loader(self, xml=Union[str, Path, ET.ElementTree]):
        """
        Common actions for UI components when we are loading a build.

        :param xml: Path: the filename of file to be loaded, or "Default" if called from the New action.
        :param xml: String: build name, commonly "Default" when called from the New action.
        :param xml: ET.ElementTree: the xml of a file that was loaded or downloaded.
        :return: N/A
        """
        self.loading = True
        new = True
        if type(xml) is ET.ElementTree:
            self.build.new(xml)
        else:
            new = xml == "Default"
            if not new:
                # open the file
                self.build.load_from_file(xml)
            else:
                self.build.new(ET.ElementTree(ET.fromstring(empty_build)))
                pass

        # if everything worked, lets update the UI
        if self.build.build is not None:
            # _debug("build_loader")
            if not new:
                self.config.add_recent_build(xml)
            # Config needs to be set before the tree, as the change_tree function uses/sets it also.
            self.config_ui.load(self.build.config)
            self.set_current_tab()
            self.tree_ui.fill_current_tree_combo()
            self.skills_ui.load(self.build.skills)
            self.items_ui.load_from_xml(self.build.items)
            self.notes_ui.load(self.build.notes_html.text, self.build.notes.text)
            self.stats.load(self.build.build)
            self.spin_level.setValue(self.build.level)
            self.combo_classes.setCurrentText(self.build.className)
            self.combo_ascendancy.setCurrentText(self.build.ascendClassName)
            self.statusbar_MainWindow.showMessage(f"Loaded: {self.build.name}", 10000)

        self.loading = False

    @Slot()
    def build_save_as(self):
        """
        Actions required to get a filename to save a build to. Should call build_save() if user doesn't cancel.

        return: N/A
        """
        # filename, selected_filter = QFileDialog.getSaveFileName(
        #     self,
        #     app.tr("Save File"),
        #     app.tr("Save build"),
        #     self.config.build_path,
        #     app.tr("Build Files (*.xml)"),
        # )
        filename = "builds/_test.xml"
        if filename != "":
            print(f"Saving to filename: {filename}")
            self.build.save_to_xml()
            # print("selected_filter: %s" % selected_filter)
            # write the file
            # self.build.save_build_to_file(filename)
            self.build.save_build_to_file(filename)

    @Slot()
    def change_tree(self, tree_id):
        """
        Actions required when the combo_manage_tree widget changes.

        :param tree_id: Current text string. We don't use it.
                "" will occur during a combobox clear
        :return: N/A
        """
        # "" will occur during a combobox clear
        if not tree_id:
            return

        full_clear = self.build.change_tree(self.tree_ui.combo_manage_tree.currentData())

        # update label_points
        self.display_number_node_points(-1)

        # stop the tree from being updated mulitple times during the class / ascendancy combo changes
        # Also stops updating build.current_spec
        self.refresh_tree = False

        _current_class = self.combo_classes.currentData()
        if self.build.current_spec.classId == _current_class:
            # update the ascendancy combo in case it's different
            self.combo_ascendancy.setCurrentIndex(self.build.current_spec.ascendClassId)
            # return

        # Protect the ascendancy value as it will get clobbered ...
        _ascendClassId = self.build.current_spec.ascendClassId
        # .. when this refreshes the Ascendancy combo box ...
        self.combo_classes.setCurrentIndex(self.build.current_spec.classId.value)
        # ... so we need to reset it's index
        self.combo_ascendancy.setCurrentIndex(_ascendClassId)

        set_combo_index_by_data(self.combo_Bandits, self.build.bandit)

        self.refresh_tree = True
        self.gview_Tree.add_tree_images(full_clear)

    @Slot()
    def class_changed(self, selected_class):
        """
        Slot for the Classes combobox. Triggers the curr_class property actions.

        :param selected_class: String of the selected text
        :return:
        """
        new_class = self.combo_classes.currentData()
        if self.build.current_spec.classId == new_class and self.refresh_tree:
            return
        # if not self.loading and len(self.build.current_spec.nodes) > 1:
        #     self.tree_ui.reset_tree()

        # GUI Changes
        # Changing the ascendancy combobox, will trigger it's signal/slot.
        # This is good as it will set the ascendancy back to 'None'
        self.combo_ascendancy.clear()
        self.combo_ascendancy.addItem("None", 0)
        _class = self.build.current_tree.classes[new_class.value]
        for idx, _ascendancy in enumerate(_class["ascendancies"], 1):
            self.combo_ascendancy.addItem(_ascendancy["name"], idx)

        if self.refresh_tree:
            # build changes
            self.build.current_spec.classId = self.combo_classes.currentData()
            self.build.current_class = self.combo_classes.currentData()
            self.build.className = selected_class
            self.build.current_class = new_class
            self.gview_Tree.add_tree_images()

    @Slot()
    def ascendancy_changed(self, selected_ascendancy):
        """
        Actions required for changing ascendancies.

        :param  selected_ascendancy: String of the selected text
                "None" will occur when refilling the combobox or when the user chooses it
                "" will occur during a combobox clear
        :return:
        """
        # "" will occur during a combobox clear
        if selected_ascendancy == "":
            return
        if self.refresh_tree:
            self.build.current_spec.ascendClassId = self.combo_ascendancy.currentData()
            self.build.ascendClassName = selected_ascendancy
            self.gview_Tree.add_tree_images()

    @Slot()
    def display_number_node_points(self, bandit_id):
        """
        Actions required when the combo_bandits widget changes.

        :param bandit_id: Current text string. We don't use it.
        :return: N/A
        """
        self.build.bandit = self.combo_Bandits.currentData()
        self.max_points = self.build.bandit == "None" and 123 or 121
        nodes_assigned = (
            self.build.nodes_assigned > self.max_points
            and html_colour_text("RED", f"{self.build.nodes_assigned}")
            or f"{self.build.nodes_assigned}"
        )
        ascnodes_assigned = (
            self.build.ascnodes_assigned > 8
            and html_colour_text("RED", f"{self.build.ascnodes_assigned}")
            or f"{self.build.ascnodes_assigned}"
        )
        self.label_points.setText(f" {nodes_assigned} / {self.max_points}    {ascnodes_assigned} / 8 ")

    # Do all actions needed to change between light and dark
    @Slot()
    def switch_theme(self, new_theme):
        """
        Set the new theme based on the state of the action.
        The text of the action has a capital letter but the qdarktheme styles are lowercase

        :param new_theme: Boolean: state of the action
        :return: N/A
        """
        if new_theme:
            self._theme = "dark"
            self.action_Theme.setText("Light")
        else:
            self._theme = "light"
            self.action_Theme.setText("Dark")

        self.config.theme = new_theme
        QApplication.instance().setStyleSheet(qdarktheme.load_stylesheet(self._theme, self._border_radius))

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
            1: self.list_SocketGroups,
            2: self.tab_main,
            3: self.textedit_Notes,
            4: self.tab_main,
            5: self.tab_main,
        }

        # Focus a Widget
        tab_focus.get(index).setFocus()
        # update the build
        self.build.current_tab = self.tab_main.tabWhatsThis(self.tab_main.currentIndex())
        # Turn on / off actions as needed
        self.action_ManageTrees.setVisible(self.build.current_tab == "TREE")

    @Slot()
    def open_import_dialog(self):
        """
        Open the import dialog. The dialog will return with either dlg.xml being valid (from a build share import)
         or dlg.character_data being valid (from a character download from PoE).
        If neither are valid (both = None) then the user did nothing.
        dlg.character_data is a dictionary of tree and items ({"tree": passive_tree, "items":  items})
        dlg.xml is a ET.ElementTree instance of the xml downloaded

        :return: N/A
        """
        dlg = ImportDlg(self.build, self.config, self)
        dlg.exec()
        if dlg.xml is not None:
            self.build_loader(dlg.xml)
        elif dlg.character_data is not None:
            self.set_current_tab("CONFIG")
            self.combo_Bandits.showPopup()
        # If neither of those two were valid, then the user closed with no actions taken

    @Slot()
    def open_export_dialog(self):
        self.build.save_to_xml(1)
        dlg = ExportDlg(self.build, self.config, self)
        dlg.exec()

    # Setup menu entries for all valid recent builds in the settings file
    def set_recent_builds_menu_items(self, config: Config):
        """
        Read the config for recent builds and create menu entries for them

        return: N/A
        """

        # Lambdas in python share the variable scope they're created in
        # so make a function containing just the lambda
        def make_connection(_idx, _filename):
            """
            Connect the menu item to _open_previous_build passing in extra information

            :param _idx:
            :param _filename:
            :return:
            """
            _action.triggered.connect(lambda checked: self._open_previous_build(checked, _idx, _filename))

        recent_builds = config.recent_builds()
        for idx, value in enumerate(recent_builds):
            if value is not None and value != "":
                filename = re.sub(".xml", "", str(Path(value).relative_to(self.config.build_path)))
                _action = self.menu_Builds.addAction(f"&{idx}.  {filename}")
                make_connection(value, idx)

    def set_current_tab(self, tab_name=""):
        """
        Actions required when setting the current tab from the configuration xml file

        :param tab_name: String;  name of a tab to switch to programatically. Doesn't set the build xml if used
        :return: N/A
        """
        if tab_name == "":
            tab_name = self.build.viewMode
        for i in range(self.tab_main.count()):
            if self.tab_main.tabWhatsThis(i) == tab_name:
                self.tab_main.setCurrentIndex(i)
                return
        # If not found, set the first
        self.tab_main.setCurrentIndex(0)

    @Slot()
    def active_skill_changed(self, _skill_text):
        """
        Actions when changing combo_MainSkillActive

        :return: N/A
        """
        pass

    def load_main_skill_combo(self, _list):
        """
        Load the left hand socket group (under "Main Skill") controls

        :param _list: list: a list of socket group names as they appear in the skills_ui() socket group listview
        :return: N/A
        """
        # print("PoB.load_main_skill_combo", len(_list))

        # clear before disconnecting.
        # This helps for "Delete All" socket groups, resetting to a new build or loading a build.
        self.combo_MainSkill.clear()

        self.combo_MainSkill.currentTextChanged.disconnect(self.main_skill_text_changed)
        self.combo_MainSkill.currentIndexChanged.disconnect(self.main_skill_index_changed)

        # backup the current index, reload combo with new values and reset to a valid current_index
        # each line is a colon separated of socket group label and gem list
        current_index = self.combo_MainSkill.currentIndex()
        # print("load_main_skill_combo.current_index 1", current_index)
        for line in _list:
            _label, _gem_list = line.split(":")
            self.combo_MainSkill.addItem(_label, _gem_list)
        self.combo_MainSkill.view().setMinimumWidth(self.combo_MainSkill.minimumSizeHint().width())
        # In case the new list is shorter or empty
        current_index = min(max(0, current_index), len(_list))
        # print("load_main_skill_combo.current_index 2", current_index)

        self.combo_MainSkill.currentTextChanged.connect(self.main_skill_text_changed)
        self.combo_MainSkill.currentIndexChanged.connect(self.main_skill_index_changed)

        # print("load_main_skill_combo.current_index 3", current_index)
        if current_index >= 0:
            self.combo_MainSkill.setCurrentIndex(current_index)

    @Slot()
    def main_skill_text_changed(self, new_text):
        """
        Fill out combo_MainSkillActive with the current text of combo_MainSkill

        :param new_text: string: the combo's text
        :return: N/A
        """
        if self.combo_MainSkill.currentData() is None:
            return
        try:
            self.combo_MainSkillActive.currentTextChanged.disconnect(self.active_skill_changed)
        except RuntimeError:
            pass

        self.combo_MainSkillActive.clear()
        self.combo_MainSkillActive.addItems(self.combo_MainSkill.currentData().split(", "))
        self.combo_MainSkillActive.view().setMinimumWidth(self.combo_MainSkillActive.minimumSizeHint().width())
        self.combo_MainSkillActive.setCurrentIndex(0)

        self.combo_MainSkillActive.currentTextChanged.connect(self.active_skill_changed)

    @Slot()
    def main_skill_index_changed(self, new_index):
        """
        Actions when changing the main skill combo. Update the Skills tab.

        :param new_index: string: the combo's index. -1 during a .clear()
        :return: N/A
        """
        if new_index == -1:
            return
        # print("main_skill_index_changed.current_index ", new_index, self.combo_MainSkill.currentText())
        # must happen before call to update_socket_group_labels
        self.build.mainSocketGroup = new_index
        self.skills_ui.update_socket_group_labels()

    @Slot()
    def update_status_bar(self, message=None):
        """
        Update the status bar. Use default text if no message is supplied.
        This triggers when the message is set and when it is cleared after the time out.

        :param message: string: the message
        :return: N/A
        """
        # we only care for when the message clears
        if pob_debug and message is None or message == "":
            process = psutil.Process(os.getpid())
            message = f"RAM: {'{:.2f}'.format(process.memory_info().rss / 1048576)}MB used:"
            self.statusbar_MainWindow.showMessage(message, 2000)

    # Overridden function
    def keyReleaseEvent(self, event):
        """
        Handle key presses into the general application (outside a widget's focus).
         Mainly for Ctrl-V for pasting skill groups and items

        :param: QKeyEvent. The event matrix
        :return: N/A
        """
        print("MainWindow", event)
        ctrl_pressed = event.keyCombination().keyboardModifiers() == Qt.ControlModifier
        alt_pressed = event.keyCombination().keyboardModifiers() == Qt.AltModifier
        shift_pressed = event.keyCombination().keyboardModifiers() == Qt.ShiftModifier
        success = False
        match event.key():
            case Qt.Key_V:
                if ctrl_pressed:
                    print("MainWindow: Ctrl-V pressed")
                    if self.skills_ui.internal_clipboard is not None:
                        self.set_tab_focus()
                        success = self.skills_ui.get_item_from_clipboard()
                    elif self.items_ui.internal_clipboard is not None:
                        self.set_tab_focus()
                        success = self.items_ui.get_item_from_clipboard()
                    else:
                        # Assume it is going to come from outside the application, ingame or trade site
                        data = pyperclip.paste()
                        if data is not None and type(data) == str and "Item Class:" in data:
                            if "Skill Gems" in data:
                                success = self.skills_ui.get_item_from_clipboard(data)
                            else:
                                success = self.items_ui.get_item_from_clipboard(data)
                        # match self.build.current_tab:
                        #     case "SKILLS":
                        #         self.skills_ui.get_item_from_clipboard()
                        #     case "ITEMS":
                        #         self.items_ui.get_item_from_clipboard()
        if not success:
            event.ignore()
        super(MainWindow, self).keyPressEvent(event)
