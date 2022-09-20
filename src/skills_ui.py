"""
This Class manages all the UI controls and takes ownship of the controls on the "SKILLS" tab
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from qdarktheme.qtpy.QtCore import QRect, Slot, QSize, Qt
from qdarktheme.qtpy.QtGui import QColor, QBrush
from qdarktheme.qtpy.QtWidgets import QCheckBox, QComboBox, QFrame, QListWidgetItem, QSpinBox, QWidget

from PoB_Main_Window import Ui_MainWindow
from constants import ColourCodes, empty_socket_group, empty_gem
from pob_config import Config, _debug, str_to_bool, index_exists, bool_to_str, print_a_xml_element, print_call_stack
from pob_file import read_json
from ui_utils import set_combo_index_by_data, set_combo_index_by_text, yes_no_dialog, HTMLDelegate, html_colour_text


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

        self.win.btn_NewSocketGroup.clicked.connect(self.new_socket_group)
        self.win.btn_DeleteSocketGroup.clicked.connect(self.delete_socket_group)
        self.win.btn_DeleteAllSocketGroups.clicked.connect(self.delete_all_socket_groups)
        # self.win.btn_SkillsManage.clicked.connect(self.manage_skill_sets)

        self.connect_skill_triggers()

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _skills):
        """
        Load internal structures from the build object.

        :param _skills: Reference to the xml <Skills> tag set
        :return: N/A
        """
        self.xml_skills = _skills
        self.disconnect_skill_triggers()

        self.win.check_SortByDPS.setChecked(str_to_bool(self.xml_skills.get("sortGemsByDPS", "True")))
        self.win.check_MatchToLevel.setChecked(
            str_to_bool(self.xml_skills.get("matchGemLevelToCharacterLevel", "False"))
        )
        self.win.check_ShowGemQualityVariants.setChecked(
            str_to_bool(self.xml_skills.get("showAltQualityGems", "False"))
        )
        set_combo_index_by_data(self.win.combo_SortByDPS, self.xml_skills.get("sortGemsByDPSField", "FullDPS"))
        set_combo_index_by_data(self.win.combo_ShowSupportGems, self.xml_skills.get("showSupportGemTypes", "ALL"))
        self.win.spin_DefaultGemLevel.setValue(int(self.xml_skills.get("defaultGemLevel", 20)))
        self.win.spin_DefaultGemQuality.setValue(int(self.xml_skills.get("defaultGemQuality", 0)))

        # self.win.combo_SkillSet.clear()
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
            # self.win.combo_SkillSet.addItem("Default", 0)
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

        active_skill_set = max(min(int(self.xml_skills.get("activeSkillSet", 0)), len(self.skill_sets_list) - 1), 0)
        self.show_skill_set(self.skill_sets_list[active_skill_set])

        self.connect_skill_triggers()

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

    def connect_skill_triggers(self):
        """re-connect triggers"""
        # print("connect_skill_triggers", self.triggers_connected)
        if self.triggers_connected:
            # Don't re-connect
            return
        # update the socket group label when something changes
        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.check_SocketGroupEnabled.stateChanged.connect(self.enable_disable_socket_group_settings)
        self.win.check_SocketGroup_FullDPS.stateChanged.connect(self.enable_disable_socket_group_settings)
        self.win.lineedit_SkillLabel.textChanged.connect(self.enable_disable_socket_group_settings)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)
        self.triggers_connected = True

    def disconnect_skill_triggers(self):
        """disconnect skill orientated triggers when updating widgets"""
        # print("disconnect_skill_triggers", self.triggers_connected)
        if not self.triggers_connected:
            # Don't disconnect if not connected
            return
        self.win.list_SocketGroups.currentRowChanged.disconnect(self.change_socket_group)
        self.win.check_SocketGroupEnabled.stateChanged.disconnect(self.enable_disable_socket_group_settings)
        self.win.check_SocketGroup_FullDPS.stateChanged.disconnect(self.enable_disable_socket_group_settings)
        self.win.lineedit_SkillLabel.textChanged.disconnect(self.enable_disable_socket_group_settings)
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)
        self.triggers_connected = False

    def define_socket_group_label(self, index, item=None, xml_group=None):
        """
        Setup the passed in QListWidgetItem's text depending on whether it's active or not, etc.

        :param: item: QListWidgetItem:
        :param: group: ElementTree.Element:
        :return: string
        """
        if xml_group is None:
            xml_group = self.xml_current_socket_group
        if xml_group is None:
            return
        if item is None:
            item = QListWidgetItem("")

        # print_call_stack(True)
        _label = xml_group.get("label")
        # build label from active skills if needed
        if _label == "":
            # _debug("Socket group1", _label, group)
            for xml_gem in xml_group.findall("Gem"):
                # If this gem is not a support gem and is enabled (the far right widget)
                if "Support" not in xml_gem.get("skillId") and str_to_bool(xml_gem.get("enabled")):
                    _label += f'{xml_gem.get("nameSpec")}, '

        if _label == "":
            _label = "-no active skills-"
        else:
            _label = _label.rstrip(", ")

        # set enabled based on the group control and whether there is an active skill in the group
        enabled = str_to_bool(xml_group.get("enabled")) and (_label != "" or _label != "<no active skills>")
        full_dps = str_to_bool(xml_group.get("includeInFullDPS", "False"))
        active = self.build.mainSocketGroup == index and enabled
        #
        # get a copy of the label with out all the extra information or colours
        item.setWhatsThis(_label)

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
        print(_label)

        item.setText(_label)
        return item

    def change_active_socket_group_label(self):
        """
        This changes the text on the 'active' socket group list as the main skill combo (far left) is
        changed. Called from MainWindow(), so may belong in that class.

        :return: N/A
        """
        if self.win.list_SocketGroups.count() == 0:
            return
        # print_a_xml_element(self.xml_current_socket_group)
        for idx in range(self.win.list_SocketGroups.count()):
            item = self.win.list_SocketGroups.item(idx)
            print("change_active_socket_group_label", idx, item)
            self.define_socket_group_label(idx, item, None)

    @Slot()
    def change_skill_set(self, new_index):
        """
        This triggers when the user changes skill sets using the combobox. (self.load calls it too)
        Will also activate if user changes skill sets in the manage dialog.

        :param new_index: int: index of the current selection
               -1 will occur during a combobox clear
        :return: N/A
        """
        # _debug("new_index", new_index)
        if 0 <= new_index < len(self.skill_sets_list):
            self.show_skill_set(self.skill_sets_list[new_index])

    def show_skill_set(self, xml_set, current_index=0):
        """
        Show a set of skills.

        :param xml_set: ElementTree.Element. This set of skills
        :param current_index: set the current skill active at the end of the function
        :return: N/A
        """
        self.disconnect_skill_triggers()

        # unload the previous set, saving it's state
        if self.xml_current_skill_set is not None:
            # may not need to do this as we are operating straight into the xml
            # unload the previous set, saving it's state
            pass

            # clean up. If current_index = -1, then this is the only thing emptying these widgets
        self.clear_gem_ui_list()
        self.win.list_SocketGroups.clear()
        self.win.combo_MainSkill.clear()
        self.win.combo_SocketedIn.setCurrentIndex(-1)
        self.win.lineedit_SkillLabel.setText("")
        self.win.check_SocketGroupEnabled.setChecked(False)
        self.win.check_SocketGroup_FullDPS.setChecked(False)

        self.xml_current_skill_set = xml_set
        # Find all Socket Groups (<Skill> in the xml) and add them to the Socket Group list
        xml_socket_groups = xml_set.findall("Skill")
        # _debug("len, socket_groups", len(socket_groups), socket_groups)
        for idx, xml_group in enumerate(xml_socket_groups):
            self.win.list_SocketGroups.addItem(self.define_socket_group_label(idx, None, xml_group))
        # Load the left hand socket group (under "Main Skill") controls
        #   whatsThis has the un-coloured/un-altered text
        self.win.load_main_skill_combo(
            [self.win.list_SocketGroups.item(i).whatsThis() for i in range(self.win.list_SocketGroups.count())]
        )

        # Trigger the filling out of the right hand side UI elements
        # self.win.list_SocketGroups.setCurrentRow(current_index)
        self.load_socket_group(current_index)

        self.connect_skill_triggers()

    @Slot()
    def new_socket_group(self):
        """Create a new socket group. Actions for when the new socket group button is pressed."""
        self.xml_current_skill_set.append(empty_socket_group)
        self.show_skill_set(self.xml_current_skill_set, len(self.xml_current_skill_set) - 1)

    @Slot()
    def delete_socket_group(self):
        """Delete a socket group"""
        if self.xml_current_socket_group is not None:
            idx = self.win.list_SocketGroups.currentRow()
            del self.xml_current_skill_set[idx]
            if len(list(self.xml_current_skill_set)) == 0:
                self.xml_current_socket_group = None
                self.show_skill_set(self.xml_current_skill_set, -1)
            else:
                idx = min(idx, self.win.list_SocketGroups.count())
                if 0 <= idx < self.win.list_SocketGroups.count():
                    self.xml_current_socket_group = self.xml_current_skill_set[idx]
                    self.show_skill_set(self.xml_current_skill_set, idx)

    @Slot()
    def delete_all_socket_groups(self, prompt=True):
        """
        Delete all socket groups.

        :param prompt: boolean: If called programatically from importing a build, this should be false,
                                elsewise prompt the user to be sure.
        :return: N/A
        """
        if len(list(self.xml_current_skill_set)) == 0:
            return
        tr = self.pob_config.app.tr
        if yes_no_dialog(self.win, tr("Delete all Socket Groups"), tr(" This action has no undo. Are you sure ?")):
            for idx in range(len(list(self.xml_current_skill_set)) - 1, -1, -1):
                del self.xml_current_skill_set[idx]
            # clear the list widget
            self.show_skill_set(self.xml_current_skill_set, -1)

    @Slot()
    def change_socket_group(self, _new_group):
        """
        This triggers when the user changes an entry on the list of skills
        :param _new_group: int: row number.
               -1 will occur during a combobox clear
        :return: N/A
        """
        # _debug("new_group", _new_group)
        self.load_socket_group(_new_group)

    def load_socket_group(self, _index):
        """
        Load a socket group into the UI, unloading the previous one
        :param _index: index to display, 0 based integer
        :return: N/A
        """
        self.disconnect_skill_triggers()

        self.clear_gem_ui_list()
        if index_exists(self.xml_current_skill_set, _index):

            # save changes to current socket group
            if self.xml_current_socket_group is not None:
                self.xml_current_socket_group.set("slot", self.win.combo_SocketedIn.currentText())
                self.xml_current_socket_group.set("label", self.win.lineedit_SkillLabel.text())
                self.xml_current_socket_group.set("enabled", bool_to_str(self.win.check_SocketGroupEnabled.isChecked()))
                self.xml_current_socket_group.set(
                    "includeInFullDPS", bool_to_str(self.win.check_SocketGroup_FullDPS.isChecked())
                )

            # assign and setup new group
            self.xml_current_socket_group = self.xml_current_skill_set[_index]
            if self.xml_current_socket_group is not None:
                self.build.mainSocketGroup = _index + 1
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

    def gem_ui_notify(self, item):
        row = self.win.list_Skills.row(item)
        ui = self.win.list_Skills.itemWidget(item)
        print("gem_ui_notify", row, ui)
        #
        # if ui.check_GemRemove:
        #     self.win.list_Skills.itemWidget(ui)

    def create_gem_ui(self, index, gem=None):
        """
        Add a new row to the Items list

        :param index: int: number of this gem in this skill group
        :param gem: Item(): The item to be added
        :return:
        """
        print("create_gem_ui", index, gem)
        if index_exists(self.gem_ui_list, index):
            self.gem_ui_list[index].load(gem)
        else:
            row = QListWidgetItem()
            self.win.list_Skills.addItem(row)
            ui = GemUI(row, self.gems_by_name_or_id, self.gem_ui_notify, gem)
            # ui = GemUI(index, self.gems_by_name_or_id, self.update_socket_group_from_skills_list, gem)
            ui.fill_gem_list(self.json_gems, self.win.combo_ShowSupportGems.currentText())
            row.setSizeHint(ui.sizeHint())
            # ui.setFrameShape(QFrame.StyledPanel)
            self.win.list_Skills.setItemWidget(row, ui)

    def create_gem_ui1(self, index, gem=None):
        """
        Create a new GemUI class and fill it. These are the widgets set on the right

        :param index: int: number of this gem in this skill group
        :param gem: the xml element if known
        :return: N/A
        """
        _debug("create_gem_ui", index, gem)
        # print_call_stack(True)
        # In most cases this will be the first one autocreated
        if index_exists(self.gem_ui_list, index):
            self.gem_ui_list[index].load(gem)
        else:
            ui = GemUI(
                index,
                self.win.scrollAreaSkillsContents,
                self.gems_by_name_or_id,
                self.update_socket_group_from_skills_list,
                gem,
            )
            self.gem_ui_list[index] = ui
            # self.gem_ui_list[index] = GemUI(index, self.win.scrollAreaSkillsContents, self.gems_by_name_or_id, gem)
            # self.current_socket_group.append(gem)

            # ui: GemUI = self.gem_ui_list[index]
            ui.fill_gem_list(self.json_gems, self.win.combo_ShowSupportGems.currentText())

            # # this one is for deleting the gem
            ui.check_GemRemove.stateChanged.connect(lambda checked: self.gem_remove_checkbox_selected(index))

            # # update the socket label when something changes
            # ui.combo_GemList.currentTextChanged.connect(lambda checked: self.update_socket_group_from_skills_list(index))
            # ui.check_GemEnabled.stateChanged.connect(lambda checked: self.enable_disable_socket_group_settings(index))
        return self.gem_ui_list[index]

    def remove_gem_ui(self, index):
        """
        Remove a GemUI class. TBA on full actions needed.
        :param index: int: index of frame/GemUI() to remove
        :return:
        """
        if index_exists(self.gem_ui_list, index):
            # self.current_skill_set[_index].remove(self.gem_ui_list[index].gem)
            del self.gem_ui_list[index]
        # update all gem_ui's index in case the one being deleted was in the middle
        for idx, key in enumerate(self.gem_ui_list.keys()):
            self.gem_ui_list[key].index = idx

    def clear_gem_ui_list(self):
        """
        Clear the gem_ui_list, destroying the UI elements as we go
        :return: N/A
        """
        for idx in self.gem_ui_list:
            gem_ui = self.gem_ui_list[idx]
            if gem_ui.gem is not None:
                # Don't notify, cause that cause a loop
                gem_ui.save(False)
            # don't be tempted by 'del self.gem_ui_list[idx]'. You'll get a dictionary error
            del gem_ui
        self.gem_ui_list.clear()

    def load_gems_json(self):
        """
        Load gems.json and remove bad entries, like [Unused] and not released
        :return: dictionary of valid entries
        """

        def get_coloured_text(this_gem, gem_name):
            """
            Define the coloured_text for this gem instance.

            :param this_gem: dict: the current gem
            :param gem_name: str: the display name of the current gem
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
            return html_colour_text(colour, gem_name)

        # read in all gems but remove all invalid/unreleased ones
        # Afflictions will be removed by this (no display_name), so maybe a different list for them
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
            if "DNT" in base_item["display_name"]:
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

        # make a list by name and skillId, index supports using the full name (Faster Attacks Support)
        #  and the display name (Faster Attacks)
        for g in gems.keys():
            _gem = gems[g]
            display_name = _gem.get("display_name", None)
            if display_name is None:
                display_name = _gem.get("base_item").get("display_name")
            _gem["coloured_text"] = get_coloured_text(_gem, display_name)
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

    @Slot()
    def gem_remove_checkbox_selected(self, _key):
        """
        Actions required for selecting the checkbox to the left of the GemUI().

        :param _key: the index passed through to lambda, this is actually the key into gem_ui_list
        :return:
        """
        if _key in self.gem_ui_list.keys():
            self.remove_gem_ui(_key)

    @Slot()
    def enable_disable_socket_group_settings(self, info):
        """
        Actions for when the socket group settings are altered.
        Change the socket group label and save values to xml.

        :return: N/A
        """
        print("enable_disable_socket_group_settings", type(info), info)
        # print_call_stack(True)
        if self.xml_current_socket_group is not None:
            self.disconnect_skill_triggers()
            self.xml_current_socket_group.set("label", self.win.lineedit_SkillLabel.text())
            self.xml_current_socket_group.set("enabled", bool_to_str(self.win.check_SocketGroupEnabled.isChecked()))
            self.xml_current_socket_group.set(
                "includeInFullDPS", bool_to_str(self.win.check_SocketGroup_FullDPS.isChecked())
            )
            item = self.win.list_SocketGroups.currentItem()
            self.define_socket_group_label(self.win.list_SocketGroups.currentIndex(), item)
            # self.win.load_main_skill_combo(
            #     [self.win.list_SocketGroups.item(i).whatsThis() for i in range(self.win.list_SocketGroups.count())]
            # )
            self.connect_skill_triggers()

    @Slot()
    def update_socket_group_from_skills_list(self, _key):
        """
        Triggered from changing a gem. This is different to the internal GemUI() actions.
        This performs all needed actions for the SkillUI class outside the GemUI() class.
        Add gem to the xml if needed.

        :param _key: the index passed through to lambda, this is actually the key into gem_ui_list
        :return: N/A
        """
        _debug(_key, len(self.gem_ui_list) - 1)
        self.disconnect_skill_triggers()
        # Check if this is gem the last gem and add it to the xml if needed
        if _key == len(self.gem_ui_list) - 1:
            ui: GemUI = self.gem_ui_list[_key]
            # ui.save()
            if ui.xml_gem is not None and ui.xml_gem not in self.xml_current_socket_group.findall("Gem"):
                self.xml_current_socket_group.append(ui.xml_gem)
                print(f"update_socket_group_from_skills_list: {ui.skillId} not found, adding")
            # Create an empty gem at the end
            self.create_gem_ui(len(self.gem_ui_list), None)
        self.enable_disable_socket_group_settings(_key)
        self.connect_skill_triggers()


"""   ----------------------------------------------------------------------------------------------"""


class GemUI(QWidget):
    """
    A class to manage one gem/skill on the right hand side of the UI
    """

    def __init__(self, my_list_item, json_gems, parent_notify, gem=None) -> None:
        super(GemUI, self).__init__()

        self.widget_height = 30
        self.setGeometry(0, 0, 620, self.widget_height)
        self.setMinimumHeight(self.widget_height)
        self.my_list_item = my_list_item
        # reference to the loaded json so we can get data for the selected gem
        self.gem_list = json_gems
        if gem is None:
            gem = empty_gem
        self.xml_gem = gem
        self.parent_notify = parent_notify

        self.coloured_text = ""
        self.tags = []
        self.gem = None
        self.level = None
        self.count = None
        self.quality = None
        self.enabled = None
        self.qualityId = None
        self._skillId = None

        # def setupUi(self, gem_list, show_support_gems):
        self.check_GemRemove = QCheckBox(self)
        self.check_GemRemove.setGeometry(QRect(10, 3, 20, 20))
        self.check_GemRemove.setChecked(True)
        self.combo_GemList = QComboBox(self)
        self.combo_GemList.setGeometry(QRect(30, 1, 260, 22))
        self.combo_GemList.setDuplicatesEnabled(False)
        self.combo_GemList.setObjectName("combo_GemList")
        self.spin_GemLevel = QSpinBox(self)
        self.spin_GemLevel.setGeometry(QRect(300, 1, 50, 22))
        self.spin_GemLevel.setMinimum(1)
        self.spin_GemLevel.setMaximum(20)
        self.spin_GemQuality = QSpinBox(self)
        self.spin_GemQuality.setGeometry(QRect(360, 1, 50, 22))
        self.spin_GemQuality.setMaximum(40)
        self.combo_GemVariant = QComboBox(self)
        self.combo_GemVariant.setObjectName("combo_GemVariant")
        self.combo_GemVariant.addItem("Default", "Default")
        self.combo_GemVariant.addItem("Anomalous", "Alternate1")
        self.combo_GemVariant.addItem("Divergent", "Alternate2")
        self.combo_GemVariant.addItem("Phantasmal", "Alternate3")
        self.combo_GemVariant.setGeometry(QRect(420, 1, 90, 22))
        self.check_GemEnabled = QCheckBox(self)
        self.check_GemEnabled.setGeometry(QRect(530, 3, 20, 20))
        self.check_GemEnabled.setChecked(True)
        self.spin_GemCount = QSpinBox(self)
        self.spin_GemCount.setGeometry(QRect(570, 1, 50, 22))
        self.spin_GemCount.setMinimum(1)
        self.spin_GemCount.setMaximum(20)
        # !!! Why are these not visible by default
        # self.setVisible(True)

        self.load(self.gem)
        # self.fill_gem_list(gem_list, show_support_gems)

    def __del__(self):
        """
        Remove PySide elements, prior to being deleted.
        The frame appears not to have a list of children, only layouts.
        Disconnect triggers so they aren't occuring during deletion.

        :return: N/A
        """
        try:
            # Remove triggers
            self.check_GemRemove.stateChanged.disconnect(self.save)
            self.spin_GemLevel.valueChanged.disconnect(self.save)
            self.spin_GemQuality.valueChanged.disconnect(self.save)
            self.spin_GemCount.valueChanged.disconnect(self.save)
            self.check_GemEnabled.stateChanged.disconnect(self.save)
            self.combo_GemVariant.currentTextChanged.disconnect(self.save)
            self.combo_GemList.currentTextChanged.disconnect(self.save)
            self.combo_GemList.currentTextChanged.disconnect(self.combo_gem_list_changed)
        except RuntimeError:
            pass

        self.check_GemRemove.setParent(None)
        self.combo_GemList.setParent(None)
        self.spin_GemLevel.setParent(None)
        self.spin_GemQuality.setParent(None)
        self.combo_GemVariant.setParent(None)
        self.check_GemEnabled.setParent(None)
        self.spin_GemCount.setParent(None)

    def sizeHint(self) -> QSize:
        return QSize(620, self.widget_height)

    @property
    def skillId(self):
        """
        Needed so we can have a setter function.

        :return: str: The name of this gem
        """
        return self._skillId

    @skillId.setter
    def skillId(self, new_skill_id):
        if new_skill_id == "":
            return
        self._skillId = new_skill_id
        self.check_GemRemove.setEnabled(new_skill_id != "" and self.index != 0)
        self.spin_GemCount.setVisible("Support" not in new_skill_id)
        self.xml_gem.set("skillId", new_skill_id)
        if self.combo_GemList.currentText():
            self.xml_gem.set("nameSpec", self.combo_GemList.currentText())
        self.gem = self.gem_list[new_skill_id]
        self.coloured_text = self.gem.get("coloured_text")

    def load(self, gem):
        """
        load the UI elements from the xml element
        :return: N/A
        """
        self.xml_gem = gem
        # print(print_a_xml_element(gem))
        if gem is not None:
            self.level = int(gem.get("level", 1))
            self.spin_GemLevel.setValue(self.level)
            self.quality = int(gem.get("quality", 0))
            self.spin_GemQuality.setValue(self.quality)
            self.count = gem.get("count", 1) == "nil" and 1 or int(gem.get("count", 1))
            self.spin_GemCount.setValue(self.count)

            self.enabled = gem.get("enabled")
            self.check_GemEnabled.setChecked(str_to_bool(self.enabled))

            self.qualityId = gem.get("qualityId", "Default")
            set_combo_index_by_data(self.combo_GemVariant, self.qualityId)
            self.skillId = gem.get("skillId")
            # self.frame.setObjectName(f"GemUI.frame.{self.skillId}")

        # Setup triggers to save information back the the xml object
        self.check_GemRemove.stateChanged.connect(self.save)
        self.spin_GemLevel.valueChanged.connect(self.save)
        self.spin_GemQuality.valueChanged.connect(self.save)
        self.spin_GemCount.valueChanged.connect(self.save)
        self.check_GemEnabled.stateChanged.connect(self.save)
        self.combo_GemVariant.currentTextChanged.connect(self.save)

    @Slot()
    def save(self, notify=True):
        """
        Save the UI elements into the xml element
        This is called by all the elements in this class

        :param: notify: bool: If true don't use call back
        :return: N/A
        """
        if self.xml_gem is None:
            self.xml_gem = empty_gem
        self.level = self.spin_GemLevel.value()
        self.xml_gem.set("level", str(self.level))
        self.quality = self.spin_GemQuality.value()
        self.xml_gem.set("quality", str(self.quality))
        self.count = self.spin_GemCount.value()
        self.xml_gem.set("count", str(self.count))

        self.enabled = bool_to_str(self.check_GemEnabled.isChecked())
        self.xml_gem.set("enabled", self.enabled)

        self.qualityId = self.combo_GemVariant.currentData()
        self.xml_gem.set("qualityId", self.qualityId)
        self.skillId = self.combo_GemList.currentData() or ""

        if notify:
            self.parent_notify(self.my_list_item)

    @Slot()
    def combo_gem_list_changed(self, item):
        if item == "":
            return
        # when item has colour in it
        # m = match(r'<span style=.*>(.*)</span>')
        self.skillId = self.gem_list[item]["skillId"]
        #

    def fill_gem_list(self, gem_list, show_support_gems):
        """
        File the gem list combo
        :param gem_list: a list of curated gems available
        :param show_support_gems: if True, only add non-awakened gems
        :return:
        """

        def add_colour(index):
            """
            Add colour to a gem name.

            :param index: int: Index into the combolist
            :return: N/A
            """
            if "dexterity" in gem_list[g]["tags"]:
                colour = ColourCodes.DEXTERITY.value
            elif "strength" in gem_list[g]["tags"]:
                colour = ColourCodes.STRENGTH.value
            elif "intelligence" in gem_list[g]["tags"]:
                colour = ColourCodes.INTELLIGENCE.value
            else:
                colour = ColourCodes.NORMAL.value
            self.combo_GemList.setItemData(index, QBrush(colour), Qt.ForegroundRole)

        if show_support_gems == "Awakened":
            for g in gem_list:
                display_name = gem_list[g]["base_item"]["display_name"]
                if "Awakened" in display_name:
                    self.combo_GemList.addItem(display_name, g)
                    add_colour(self.combo_GemList.count() - 1)
        else:
            for g in gem_list:
                display_name = gem_list[g]["base_item"]["display_name"]
                if show_support_gems == "Normal" and "Awakened" in display_name:
                    continue
                self.combo_GemList.addItem(display_name, g)
                add_colour(self.combo_GemList.count() - 1)

        # set the ComboBox dropdown width.
        self.combo_GemList.view().setMinimumWidth(self.combo_GemList.minimumSizeHint().width())
        # ToDo: Sort by other methods
        # Sort Alphabetically
        self.combo_GemList.model().sort(0)
        if self.xml_gem is not None and self._skillId != "":
            self.combo_GemList.setCurrentIndex(set_combo_index_by_data(self.combo_GemList, self._skillId))
        else:
            self.combo_GemList.setCurrentIndex(-1)

        # Setup trigger to save information back the the xml object
        self.combo_GemList.currentTextChanged.connect(self.save)
        self.combo_GemList.currentTextChanged.connect(self.combo_gem_list_changed)


# def test() -> None:
#     skills_ui = SkillsUI()
#     print(skills_ui)
#
#
# if __name__ == "__main__":
#     test()
