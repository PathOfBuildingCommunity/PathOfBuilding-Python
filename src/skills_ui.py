"""
This Class manages all the UI controls and takes ownship of the controls on the "SKILLS" tab
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from qdarktheme.qtpy.QtCore import Qt, Slot
from qdarktheme.qtpy.QtWidgets import QListWidgetItem

from PoB_Main_Window import Ui_MainWindow
from constants import ColourCodes, empty_socket_group, empty_gem
from pob_config import Config, _debug, str_to_bool, index_exists, bool_to_str, print_a_xml_element, print_call_stack
from pob_file import read_json
from ui_utils import set_combo_index_by_data, set_combo_index_by_text, HTMLDelegate, html_colour_text
from popup_dialogs import yes_no_dialog
from gem_ui import GemUI


class SkillsUI:
    """Functions and variables to drive the interactions on the Skills Tab."""

    def __init__(self, _config: Config, _build, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.build = _build
        self.win = _win
        # this is the whole <Skills>...</Skills> tag set
        self.xml_skills = None
        # list of xml elements for the <SkillSet>...</SkillSet>
        self.skill_sets_list = []
        # xml element for the currently chosen skillset
        self.xml_current_skill_set = None
        # xml element for the currently chosen socket group (the <Skill>...<Skill> tags inside a skill set)
        self.xml_current_socket_group = None
        # list of gems from gems.json
        self.gems_by_name_or_id = {}
        self.json_gems = self.load_gems_json()
        # tracks the state of the triggers, to stop setting triggers more than once or disconnecting when not connected
        self.triggers_connected = False

        # dictionary for holding the GemUI representions of the gems in each socket group
        self.gem_ui_list = {}

        # Allow us to print in colour
        # ToDo: update list_SocketGroups to use colours
        delegate = HTMLDelegate()
        delegate._list = self.win.list_SocketGroups
        self.win.list_SocketGroups.setItemDelegate(delegate)

        tr = self.pob_config.app.tr
        self.win.combo_SortByDPS.addItem(tr("Full DPS"), "Full DPS")
        self.win.combo_SortByDPS.addItem(tr("Combined DPS"), "CombinedDPS")
        self.win.combo_SortByDPS.addItem(tr("Total DPS"), "TotalDPS")
        self.win.combo_SortByDPS.addItem(tr("Average Hit"), "AverageDamage")
        self.win.combo_SortByDPS.addItem(tr("DoT DPS"), "TotalDot")
        self.win.combo_SortByDPS.addItem(tr("Bleed DPS"), "BleedDPS")
        self.win.combo_SortByDPS.addItem(tr("Ignite DPS"), "IgniteDPS")
        self.win.combo_SortByDPS.addItem(tr("Poison DPS"), "TotalPoisonDPS")
        self.win.combo_ShowSupportGems.addItem(tr("All"), "ALL")
        self.win.combo_ShowSupportGems.addItem(tr("Normal"), "NORMAL")
        self.win.combo_ShowSupportGems.addItem(tr("Awakened"), "AWAKENED")

        # Button triggers are right to remain connected at all times as they are user initiated.
        self.win.btn_NewSocketGroup.clicked.connect(self.new_socket_group)
        self.win.btn_DeleteSocketGroup.clicked.connect(self.delete_socket_group)
        self.win.btn_DeleteAllSocketGroups.clicked.connect(self.delete_all_socket_groups)
        # self.win.btn_SkillsManage.clicked.connect(self.manage_skill_sets)

        self.socket_group_to_be_moved = None
        self.win.list_SocketGroups.model().rowsMoved.connect(self.socket_groups_rows_moved, Qt.QueuedConnection)
        self.win.list_SocketGroups.model().rowsAboutToBeMoved.connect(
            self.socket_groups_rows_about_to_be_moved, Qt.QueuedConnection
        )
        self.skill_gem_to_be_moved = None
        self.win.list_Skills.model().rowsMoved.connect(self.skill_gem_rows_moved, Qt.QueuedConnection)
        self.win.list_Skills.model().rowsAboutToBeMoved.connect(
            self.skill_gem_rows_about_to_be_moved, Qt.QueuedConnection
        )

        # Do NOT turn on skill triggers here

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    @property
    def activeSkillSet(self):
        # Use a property to ensure the correct +/- 1
        return max(int(self.xml_skills.get("activeSkillSet", 1)) - 1, 0)

    @activeSkillSet.setter
    # Use a property to ensure the correct +/- 1
    def activeSkillSet(self, new_set):
        self.xml_skills.set("activeSkillSet", f"{new_set + 1}")

    def load(self, _skills):
        """
        Load internal structures from the build object.

        :param _skills: Reference to the xml <Skills> tag set
        :return: N/A
        """
        self.xml_skills = _skills
        self.disconnect_skill_triggers()
        # clean up
        self.change_skill_set(-1)

        self.win.check_SortByDPS.setChecked(str_to_bool(self.xml_skills.get("sortGemsByDPS", "True")))
        self.win.check_MatchToLevel.setChecked(
            str_to_bool(self.xml_skills.get("matchGemLevelToCharacterLevel", "False"))
        )
        self.win.check_ShowGemQualityVariants.setChecked(
            str_to_bool(self.xml_skills.get("showAltQualityGems", "False"))
        )
        set_combo_index_by_data(self.win.combo_SortByDPS, self.xml_skills.get("sortGemsByDPSField", "FullDPS"))
        set_combo_index_by_data(self.win.combo_ShowSupportGems, self.xml_skills.get("showSupportGemTypes", "ALL"))
        level = self.xml_skills.get("defaultGemLevel", 20)
        if level == "nil":
            level = 0
        self.win.spin_DefaultGemLevel.setValue(int(level))
        quality = self.xml_skills.get("defaultGemQuality", 0)
        if quality == "nil":
            quality = 0
        self.win.spin_DefaultGemQuality.setValue(int(quality))

        self.win.combo_SkillSet.clear()
        self.skill_sets_list.clear()
        _sets = self.xml_skills.findall("SkillSet")
        # if len(_sets) > 0:
        # for idx, _set in enumerate(self.xml_skills.findall("SkillSet")):
        #     self.skill_sets_list.append(_set)
        #     self.win.combo_SkillSet.addItem(_set.get("title", f"Default{idx + 1}"), idx)
        # else:
        if len(_sets) == 0:
            # The lua version won't create a <skillset> (socket group) if there is only one skill set.
            # let's create one so we have code compatibility in all circumstances
            _set = ET.Element("SkillSet")
            self.skill_sets_list.append(_set)
            self.xml_skills.append(_set)
            # Move skills to the new socket group
            xml_socket_groups = self.xml_skills.findall("Skill")
            for group in xml_socket_groups:
                _set.append(group)
                self.xml_skills.remove(group)

        for idx, _set in enumerate(self.xml_skills.findall("SkillSet")):
            self.skill_sets_list.append(_set)
            self.win.combo_SkillSet.addItem(_set.get("title", f"Default{idx + 1}"), idx)
        # set the SkillSet ComboBox dropdown width.
        self.win.combo_SkillSet.view().setMinimumWidth(self.win.combo_SkillSet.minimumSizeHint().width())

        self.connect_skill_triggers()

        # activate trigger to run change_skill_set
        active_skill_set = min(self.activeSkillSet, len(self.skill_sets_list) - 1)
        self.win.combo_SkillSet.setCurrentIndex(active_skill_set)

    def save(self):
        """
        Save internal structures back to the build's skills object.
        The gems have been saving themselves to the xml object whenever there was a change,
          so we only need to get the other UI widget's values
        """
        self.xml_skills.set("sortGemsByDPS", bool_to_str(self.win.check_SortByDPS.isChecked()))
        self.xml_skills.set("matchGemLevelToCharacterLevel", bool_to_str(self.win.check_MatchToLevel.isChecked()))
        self.xml_skills.set("showAltQualityGems", bool_to_str(self.win.check_ShowGemQualityVariants.isChecked()))
        self.xml_skills.set("sortGemsByDPSField", self.win.combo_SortByDPS.currentData())
        self.xml_skills.set("showSupportGemTypes", self.win.combo_ShowSupportGems.currentData())
        self.xml_skills.set("defaultGemLevel", str(self.win.spin_DefaultGemLevel.value()))
        self.xml_skills.set("defaultGemQuality", str(self.win.spin_DefaultGemQuality.value()))
        return self.xml_skills

    def load_gems_json(self):
        """
        Load gems.json and remove bad entries, like [Unused] and not released
        :return: dictionary of valid entries
        """

        def get_coloured_text(this_gem):
            """
            Define the coloured_text for this gem instance.

            :param this_gem: dict: the current gem
            :return: N/A
            """
            tags = this_gem["tags"]
            colour = ColourCodes.NORMAL.value
            if tags is not None:
                if "dexterity" in tags:
                    colour = ColourCodes.DEXTERITY.value
                elif "strength" in tags:
                    colour = ColourCodes.STRENGTH.value
                elif "intelligence" in tags:
                    colour = ColourCodes.INTELLIGENCE.value
            return colour

        # read in all gems but remove all invalid/unreleased ones
        # "Afflictions" will be removed by this (no display_name), so maybe a different list for them
        gems = read_json(Path(self.pob_config.exe_dir, "Data/gems.json"))
        if gems is None:
            return None
        gems_list = list(gems.keys())
        for g in gems_list:
            if "Royale" in g:
                del gems[g]
                continue
            base_item = gems[g]["base_item"]
            display_name = gems[g].get("display_name", None)
            if base_item is None and display_name is None:
                del gems[g]
                continue
            if display_name is None:
                display_name = base_item.get("display_name")
            if "DNT" in display_name:
                del gems[g]
                continue
            if base_item is not None:
                if base_item["release_state"] == "unreleased":
                    del gems[g]
                    continue
                if gems[g].get("is_support", False):
                    # remove 'Support' from the name, but keep the full name as full_name
                    _name = display_name
                    gems[g]["full_name"] = _name
                    gems[g]["display_name"] = _name.replace(" Support", "")
                    base_item["display_name"] = _name.replace(" Support", "")

        # make a list by name and skill_id. Index supports using the full name (Faster Attacks Support)
        #  and the display name (Faster Attacks)
        for g in gems.keys():
            _gem = gems[g]
            display_name = _gem.get("display_name", None)
            if display_name is None:
                display_name = _gem.get("base_item").get("display_name")
            _gem["colour"] = get_coloured_text(_gem)
            _gem["coloured_text"] = html_colour_text(_gem["colour"], display_name)
            self.gems_by_name_or_id[g] = _gem
            self.gems_by_name_or_id[display_name] = _gem
            self.gems_by_name_or_id[display_name]["skillId"] = g
            # add supports using the full name
            full_name = _gem.get("full_name", None)
            if full_name is not None:
                self.gems_by_name_or_id[full_name] = _gem
                self.gems_by_name_or_id[full_name]["skillId"] = g

        return gems
        # load_gems_json

    def connect_skill_triggers(self):
        """re-connect triggers"""
        # print("connect_skill_triggers", self.triggers_connected)
        # print_call_stack(idx=-4)
        if self.triggers_connected:
            # Don't re-connect
            return
        self.triggers_connected = True
        # update the socket group label when something changes
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)
        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.check_SocketGroupEnabled.stateChanged.connect(self.save_socket_group_settings)
        self.win.check_SocketGroup_FullDPS.stateChanged.connect(self.save_socket_group_settings)
        self.win.lineedit_SkillLabel.textChanged.connect(self.save_socket_group_settings)
        self.win.combo_SocketedIn.currentIndexChanged.connect(self.save_socket_group_settings)

    def disconnect_skill_triggers(self):
        """disconnect skill orientated triggers when updating widgets"""
        # print("disconnect_skill_triggers", self.triggers_connected)
        # print_call_stack(idx=-4)
        if not self.triggers_connected:
            # Don't disconnect if not connected
            return
        self.triggers_connected = False
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)
        self.win.list_SocketGroups.currentRowChanged.disconnect(self.change_socket_group)
        self.win.check_SocketGroupEnabled.stateChanged.disconnect(self.save_socket_group_settings)
        self.win.check_SocketGroup_FullDPS.stateChanged.disconnect(self.save_socket_group_settings)
        self.win.lineedit_SkillLabel.textChanged.disconnect(self.save_socket_group_settings)
        self.win.combo_SocketedIn.currentIndexChanged.disconnect(self.save_socket_group_settings)

    """
    ################################################### SKILL SET ###################################################
    """

    @Slot()
    def change_skill_set(self, new_index):
        """
        This triggers when the user changes skill sets using the combobox. (self.load calls it too)
        Will also activate if user changes skill sets in the manage dialog.

        :param new_index: int: index of the current selection
               -1 will occur during a combobox clear, or some internal calls
        :return: N/A
        """
        # print("change_skill_set", new_index)
        self.disconnect_skill_triggers()
        self.xml_current_socket_group = None
        self.clear_socket_group_settings()
        self.win.list_SocketGroups.clear()
        if 0 <= new_index < len(self.skill_sets_list):
            self.show_skill_set(self.skill_sets_list[new_index])
        self.connect_skill_triggers()

    def show_skill_set(self, xml_set, _index=0):
        """
        Show a set of skills.

        :param xml_set: ElementTree.Element. This set of skills
        :param _index: set the current socket group active at the end of the function
        :return: N/A
        """
        # print("show_skill_set", _index, self.win.combo_SkillSet.currentText())
        self.disconnect_skill_triggers()

        self.xml_current_skill_set = xml_set
        # Find all Socket Groups (<Skill> in the xml) and add them to the Socket Group list
        xml_socket_groups = xml_set.findall("Skill")

        for idx, xml_group in enumerate(xml_socket_groups):
            self.win.list_SocketGroups.addItem(self.define_socket_group_label(None, xml_group))

        # Load the left hand socket group (under "Main Skill") widgets
        self.load_main_skill_combo()

        self.connect_skill_triggers()
        # Trigger the filling out of the right hand side UI elements using change_socket_group -> load_socket_group
        self.win.list_SocketGroups.setCurrentRow(0)
        # Use change_socket_group using mainActiveSkill -1

    """
    ################################################### SOCKET GROUP ###################################################
    """

    def define_socket_group_label(self, item=None, xml_group=None):
        """
        Setup the passed in QListWidgetItem's text depending on whether it's active or not, etc.

        :param: item: QListWidgetItem:
        :param: group: ElementTree.Element:
        :return: QListWidgetItem
        """
        # print("define_socket_group_label", item, xml_group)
        if xml_group is None:
            xml_group = self.xml_current_socket_group
        if xml_group is None:
            return
        if item is None:
            item = QListWidgetItem("")

        _label = xml_group.get("label")
        # build a gem list from active skills if needed
        _gem_list = ""
        for xml_gem in xml_group.findall("Gem"):
            # If this gem is not a support gem and is enabled (the far right widget)
            if "Support" not in xml_gem.get("skillId") and str_to_bool(xml_gem.get("enabled")):
                _gem_list += f'{xml_gem.get("nameSpec")}, '

        if _gem_list == "":
            _gem_list = "-no active skills-"
        else:
            _gem_list = _gem_list.rstrip(", ")
        if _label == "":
            _label = _gem_list

        # set enabled based on the group control and whether there is an active skill in the group
        enabled = str_to_bool(xml_group.get("enabled")) and not (_label == "" or _label == "-no active skills-")
        full_dps = str_to_bool(xml_group.get("includeInFullDPS", "False"))
        active = self.win.combo_MainSkill.currentText() == _label and enabled

        # get a copy of the label with out all the extra information or colours
        item.setWhatsThis(f"{_label}:{_gem_list}")

        _label += (
            f"{not enabled and ' Disabled' or ''}"
            f"{full_dps and html_colour_text('TANGLE', ' (FullDPS)') or ''}"
            f"{active and html_colour_text('RELIC', ' (Active)') or ''}"
        )

        # change colour (dim) if it's disabled or no active skills
        if enabled:
            _label = html_colour_text("NORMAL", _label)
        else:
            _label = html_colour_text("LIGHTGRAY", _label)
        # print(_label)

        item.setText(_label)
        return item

    def update_socket_group_labels(self):
        """
        This changes the text on the 'active' socket group list as the main skill combo (far left) is
        changed. Called from MainWindow(), so may belong in that class.

        :return: N/A
        """
        # print("update_socket_group_labels")
        if self.win.list_SocketGroups.count() == 0:
            return
        # print_a_xml_element(self.xml_current_socket_group)
        for idx in range(self.win.list_SocketGroups.count()):
            item = self.win.list_SocketGroups.item(idx)
            # print("update_socket_group_labels", idx, item)
            self.define_socket_group_label(item, self.xml_current_skill_set[idx])

    @Slot()
    def delete_socket_group(self):
        """Delete a socket group"""
        # print("delete_socket_group")
        self.disconnect_skill_triggers()
        if self.xml_current_skill_set is not None and self.xml_current_socket_group is not None:
            idx = self.win.list_SocketGroups.currentRow()
            self.win.list_SocketGroups.takeItem(idx)
            del self.xml_current_skill_set[idx]
            if len(self.xml_current_skill_set.findall("Skill")) == 0:
                # empty all skill/socket widgets
                self.change_skill_set(-1)
            else:
                self.connect_skill_triggers()
                # Trigger the filling out of the RHS UI elements using change_socket_group -> load_socket_group
                self.win.list_SocketGroups.setCurrentRow(min(idx, self.win.list_SocketGroups.count()))
        self.update_socket_group_labels()
        self.load_main_skill_combo()
        self.connect_skill_triggers()

    @Slot()
    def delete_all_socket_groups(self, prompt=True):
        """
        Delete all socket groups.

        :param prompt: boolean: If called programatically from importing a build, this should be false,
                                elsewise prompt the user to be sure.
        :return: N/A
        """
        # print("delete_all_socket_groups")
        if len(list(self.xml_current_skill_set)) == 0:
            return
        tr = self.pob_config.app.tr
        if yes_no_dialog(self.win, tr("Delete all Socket Groups"), tr(" This action has no undo. Are you sure ?")):
            self.disconnect_skill_triggers()
            for idx in range(len(list(self.xml_current_skill_set)) - 1, -1, -1):
                del self.xml_current_skill_set[idx]
            # empty all skill/socket widgets
            self.change_skill_set(-1)
            self.load_main_skill_combo()
            self.connect_skill_triggers()

    @Slot()
    def new_socket_group(self):
        """Create a new socket group. Actions for when the new socket group button is pressed."""
        # print("new_socket_group")
        # Add new group to xml and Socket Group list, and then show the update
        self.xml_current_skill_set.append(ET.fromstring(empty_socket_group))
        idx = len(self.xml_current_skill_set) - 1
        self.win.list_SocketGroups.addItem(self.define_socket_group_label(xml_group=self.xml_current_skill_set[idx]))
        self.update_socket_group_labels()
        # Trigger the filling out of the right hand side UI elements using change_socket_group -> load_socket_group
        self.win.list_SocketGroups.setCurrentRow(idx)

    def load_main_skill_combo(self):
        """
        Load the left hand socket group (under "Main Skill") controls

        :return: N/A
        """
        self.win.load_main_skill_combo(
            # whatsThis has the un-coloured/un-altered text
            [self.win.list_SocketGroups.item(i).whatsThis() for i in range(self.win.list_SocketGroups.count())]
        )

    def clear_socket_group_settings(self):
        """
        Clear all the widgets on the top right of the Skills tab.

        :return: N/A
        """
        self.disconnect_skill_triggers()
        self.clear_gem_ui_list()
        self.win.combo_SocketedIn.setCurrentIndex(-1)
        self.win.lineedit_SkillLabel.setText("")
        self.win.check_SocketGroupEnabled.setChecked(False)
        self.win.check_SocketGroup_FullDPS.setChecked(False)
        self.connect_skill_triggers()

    @Slot()
    def change_socket_group(self, _new_group):
        """
        This triggers when the user changes an entry on the list of skills.

        :param _new_group: int: row number.
               -1 will occur during a combobox clear
        :return: N/A
        """
        # print("change_socket_group", _new_group)
        self.disconnect_skill_triggers()

        # Set mainActiveSkill +1

        # Clean up and save objects. If _index = -1, then this is the only thing emptying these widgets
        if index_exists(self.xml_current_skill_set, _new_group):
            self.clear_socket_group_settings()
            self.load_socket_group(_new_group)

    def load_socket_group(self, _index):
        """
        Load a socket group into the UI, unloading the previous one.

        :param _index: index to display, 0 based integer
        :return: N/A
        """
        # print("load_socket_group")
        self.disconnect_skill_triggers()

        if index_exists(self.xml_current_skill_set, _index):
            # assign and setup new group
            self.xml_current_socket_group = self.xml_current_skill_set[_index]
            if self.xml_current_socket_group is not None:
                self.build.check_socket_group_for_an_active_gem(self.xml_current_socket_group)
                self.win.lineedit_SkillLabel.setText(self.xml_current_socket_group.get("label"))
                set_combo_index_by_text(self.win.combo_SocketedIn, self.xml_current_socket_group.get("slot"))
                self.win.check_SocketGroupEnabled.setChecked(
                    str_to_bool(self.xml_current_socket_group.get("enabled", "False"))
                )
                self.win.check_SocketGroup_FullDPS.setChecked(
                    str_to_bool(self.xml_current_socket_group.get("includeInFullDPS", "False"))
                )
                for idx, gem in enumerate(self.xml_current_socket_group.findall("Gem")):
                    self.create_gem_ui(idx, gem)
                # Create an empty gem at the end
                self.create_gem_ui(len(self.gem_ui_list), None)

        self.connect_skill_triggers()

    @Slot()
    def save_socket_group_settings(self, info):
        """
        Actions for when the socket group settings are altered. Save to xml. Do *NOT* call internally.

        :param: Any: Some sort of info for a widget. EG: checked state for a checkBox, text for a comboBox.
        :return: N/A
        """
        if self.xml_current_socket_group is not None:
            # print(f"save_socket_group_settings, {type(info)}, '{info}'")
            self.xml_current_socket_group.set("slot", self.win.combo_SocketedIn.currentText())
            self.xml_current_socket_group.set("label", self.win.lineedit_SkillLabel.text())
            self.xml_current_socket_group.set("enabled", bool_to_str(self.win.check_SocketGroupEnabled.isChecked()))
            self.xml_current_socket_group.set(
                "includeInFullDPS", bool_to_str(self.win.check_SocketGroup_FullDPS.isChecked())
            )
            item = self.win.list_SocketGroups.currentItem()
            # stop a recursion error as save_socket_group_settings is called from define_socket_group_label as well
            if info is not None:
                self.define_socket_group_label(item)
            self.load_main_skill_combo()

    @Slot()
    def socket_groups_rows_moved(self, parent, start, end, destination, destination_row):
        """
        Respond to a socket group being moved, by moving it's matching xml element. It's called 4 times (sometimes)

        :param parent: QModelIndex: not Used.
        :param start: int: where the row was moved from.
        :param end: int: not Used. It's the same as start as multi-selection is not allowed.
        :param destination: QModelIndex: not Used.
        :param destination_row: int: The destination row.
        :return: N/A
        """
        print("socket_groups_rows_moved")
        # if not None, do move in current_xml_group and set self.socket_group_to_be_moved = None
        # this way the last three are ignored.
        if self.socket_group_to_be_moved is None:
            return
        # Do move
        if self.xml_current_skill_set is not None:
            xml_sg = self.xml_current_skill_set[start]
            if start < destination_row:
                # need to decrement dest by one as we are going to remove start first
                destination_row -= 1
            self.xml_current_skill_set.remove(xml_sg)
            self.xml_current_skill_set.insert(destination_row, xml_sg)

        # reset to none, this one we only respond to the first call of the four.
        self.socket_group_to_be_moved = None

    @Slot()
    def socket_groups_rows_about_to_be_moved(
        self, source_parent, source_start, source_end, destination_parent, destination_row
    ):
        """
        Setup for a socket group move. It's called 4 times (sometimes)

        :param source_parent: QModelIndex: Used to notify the move
        :param source_start: int: not Used
        :param source_end: int: not Used
        :param destination_parent: QModelIndex: not Used
        :param destination_row: int: not Used
        :return: N/A
        """
        # print("socket_groups_rows_about_to_be_moved")
        self.socket_group_to_be_moved = source_parent

    """
    ################################################### GEM UI ###################################################
    """

    def gem_ui_notify(self, item):
        """
        React to a wigdet change from an instance of GemUI(), where that widget is not the remove button.

        :param item: the triggering WidgetItem from list_Skills.
        :return: N/A
        """
        row = self.win.list_Skills.row(item)
        gem_ui = self.win.list_Skills.itemWidget(item)
        # print("gem_ui_notify", item, row, gem_ui)
        if (
            gem_ui.xml_gem is not None
            and gem_ui.skill_id != ""
            and gem_ui.xml_gem not in self.xml_current_socket_group.findall("Gem")
        ):
            self.xml_current_socket_group.append(gem_ui.xml_gem)
            # print(f"gem_ui_notify: {gem_ui.skill_id} not found, adding.")
            # Create an empty gem at the end
            self.create_gem_ui(len(self.gem_ui_list), None)
        self.update_socket_group_labels()
        self.load_main_skill_combo()

    def create_gem_ui(self, index, gem=None):
        """
        Add a new row to the Skills list.

        :param index: int: number of this gem in this skill group
        :param gem: ET.elementtree: The item to be added
        :return:
        """
        # print("create_gem_ui", index, gem)
        item = QListWidgetItem()
        self.win.list_Skills.addItem(item)
        gem_ui = GemUI(item, self.gems_by_name_or_id, self.gem_ui_notify, gem)
        gem_ui.fill_gem_list(self.json_gems, self.win.combo_ShowSupportGems.currentText())
        item.setSizeHint(gem_ui.sizeHint())
        self.win.list_Skills.setItemWidget(item, gem_ui)

        # this one is for deleting the gem
        gem_ui.btn_GemRemove.clicked.connect(lambda checked: self.gem_remove_checkbox_selected(item, gem_ui))

    def clear_gem_ui_list(self):
        """
        Clear the gem_ui_list, destroying the UI elements as we go.

        :return: N/A
        """
        # print(
        #     f"clear_gem_ui_list, len(self.gem_ui_list)={len(self.gem_ui_list)},"
        #     f"self.win.list_Skills.count()={self.win.list_Skills.count()}"
        # )
        for idx in range(self.win.list_Skills.count()):
            item = self.win.list_Skills.item(idx)
            gem_ui = self.win.list_Skills.itemWidget(item)
            # print("clear_gem_ui_list", idx)
            if gem_ui is not None and gem_ui.gem is not None:
                # Don't notify, cause that cause a loop
                gem_ui.save(False)
            # del gem_ui
        # self.gem_ui_list.clear()
        self.win.list_Skills.clear()

    # def remove_gem_ui(self, index):
    #     """
    #     Remove a GemUI class. TBA on full actions needed.
    #
    #     :param index: int: index of frame/GemUI() to remove
    #     :return:
    #     """
    #     print("remove_gem_ui")
    #     if index_exists(self.gem_ui_list, index):
    #         # self.current_skill_set[_index].remove(self.gem_ui_list[index].gem)
    #         del self.gem_ui_list[index]
    #     # update all gem_ui's index in case the one being deleted was in the middle
    #     for idx, key in enumerate(self.gem_ui_list.keys()):
    #         self.gem_ui_list[key].index = idx

    @Slot()
    def gem_remove_checkbox_selected(self, item, gem_ui):
        """
        Actions required for selecting the red cross to the left of the GemUI().

        :param item: the row passed through to lambda
        :param gem_ui: the GemUI passed through to lambda
        :return: N/A
        """
        print("gem_remove_checkbox_selected", item, gem_ui)
        row = self.win.list_Skills.row(item)
        self.win.list_Skills.takeItem(row)
        xml_gem = gem_ui.xml_gem
        if self.xml_current_socket_group is not None and xml_gem in self.xml_current_socket_group.findall("Gem"):
            # print("gem_ui_notify", row, ui)
            # self.remove_gem_ui(_key)
            self.xml_current_socket_group.remove(xml_gem)
        if self.win.list_Skills.count() == 0:
            self.create_gem_ui(0)
        self.update_socket_group_labels()
        self.load_main_skill_combo()

    def skill_gem_rows_moved(self, parent, start, end, destination, destination_row):
        """
        Respond to a socket group being moved, by moving it's matching xml element. It's called 4 times (sometimes)

        :param parent: QModelIndex: not Used.
        :param start: int: where the row was moved from.
        :param end: int: not Used. It's the same as start as multi-selection is not allowed.
        :param destination: QModelIndex: not Used.
        :param destination_row: int: The destination row.
        :return: N/A
        """
        # print("skill_gem_rows_moved")
        # if not None, do move in current_xml_group and set self.socket_group_to_be_moved = None
        # this way the last three are ignored.
        if self.socket_group_to_be_moved is None:
            return
        # Do move
        if self.xml_current_socket_group is not None:
            # item = self.win.list_SocketGroups.item(start)
            xml_sg = self.xml_current_socket_group[start]
            if start < destination_row:
                # need to decrement dest by one as we are going to remove start first
                destination_row -= 1
            self.xml_current_socket_group.remove(xml_sg)
            self.xml_current_socket_group.insert(destination_row, xml_sg)

        # reset to none, this one we only respond to the first call of the four.
        self.socket_group_to_be_moved = None

    @Slot()
    def skill_gem_rows_about_to_be_moved(
        self, source_parent, source_start, source_end, destination_parent, destination_row
    ):
        """
        Setup for a socket group move. It's called 4 times (sometimes)

        :param source_parent: QModelIndex: Used to notify the move
        :param source_start: int: not Used
        :param source_end: int: not Used
        :param destination_parent: QModelIndex: not Used
        :param destination_row: int: not Used
        :return: N/A
        """
        # print("skill_gem_rows_about_to_be_moved")
        self.socket_group_to_be_moved = source_parent


# def test() -> None:
#     skills_ui = SkillsUI()
#     print(skills_ui)
#
#
# if __name__ == "__main__":
#     test()
