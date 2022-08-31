"""
This Class manages all the elements and owns some elements of the "SKILLS" tab
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from qdarktheme.qtpy.QtCore import QRect, Slot, Qt
from qdarktheme.qtpy.QtGui import QColor, QBrush
from qdarktheme.qtpy.QtWidgets import QCheckBox, QComboBox, QFrame, QListWidgetItem, QSpinBox

from PoB_Main_Window import Ui_MainWindow
from constants import ColourCodes, empty_socket_group, empty_gem
from pob_config import Config, _debug, str_to_bool, index_exists, bool_to_str, print_a_xml_element, print_call_stack
from pob_file import read_json
from ui_utils import set_combo_index_by_data, set_combo_index_by_text


class SkillsUI:
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
        self.gems_by_name = {}
        self.json_gems = self.load_gems_json()

        # dictionary for holding the GemUI representions of the gems in each socket group
        self.gem_ui_list = {}

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

        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)
        self.win.btn_NewSocketGrp.clicked.connect(self.new_socket_group)

        # update the socket group label when something changes
        self.win.check_SocketGroupEnabled.stateChanged.connect(self.enable_disable_socket_group_full_dps)
        self.win.check_SocketGroup_FullDPS.stateChanged.connect(self.enable_disable_socket_group_full_dps)

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _skills):
        """
        Load internal structures from the build object
        :param _skills: Reference to the xml <Skills> tag set
        :return: N/A
        """
        self.xml_skills = _skills
        self.win.check_SortByDPS.setChecked(str_to_bool(self.xml_skills.get("sortGemsByDPS", True)))
        self.win.check_MatchToLevel.setChecked(str_to_bool(self.xml_skills.get("matchGemLevelToCharacterLevel", False)))
        self.win.check_ShowGemQualityVariants.setChecked(str_to_bool(self.xml_skills.get("showAltQualityGems", False)))
        set_combo_index_by_data(self.win.combo_SortByDPS, self.xml_skills.get("sortGemsByDPSField", "FullDPS"))
        set_combo_index_by_data(self.win.combo_ShowSupportGems, self.xml_skills.get("showSupportGemTypes", "ALL"))
        self.win.spin_DefaultGemLevel.setValue(int(self.xml_skills.get("defaultGemLevel", 20)))
        self.win.spin_DefaultGemQuality.setValue(int(self.xml_skills.get("defaultGemQuality", 0)))

        # disconnect triggers
        self.win.list_SocketGroups.currentRowChanged.disconnect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)
        self.win.check_SocketGroupEnabled.stateChanged.disconnect(self.enable_disable_socket_group_full_dps)
        self.win.check_SocketGroup_FullDPS.stateChanged.disconnect(self.enable_disable_socket_group_full_dps)

        self.win.combo_SkillSet.clear()
        self.skill_sets_list.clear()
        _sets = self.xml_skills.findall("SkillSet")
        if len(_sets) > 0:
            for idx, _set in enumerate(self.xml_skills.findall("SkillSet")):
                self.skill_sets_list.append(_set)
                self.win.combo_SkillSet.addItem(_set.get("title", f"Default{idx + 1}"), idx)
        else:
            # The lua version won't create a <skillset> (socket group) if there is only one.
            # let's create one so we have code compatibility in all circumstances
            _set = ET.Element("SkillSet")
            self.skill_sets_list.append(_set)
            self.win.combo_SkillSet.addItem("Default", 0)
            self.xml_skills.append(_set)
            # Move skills to the new socket group
            socket_group = self.xml_skills.findall("Skill")
            for group in socket_group:
                _set.append(group)
                self.xml_skills.remove(group)

        # re-connect triggers
        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)
        self.win.check_SocketGroupEnabled.stateChanged.connect(self.enable_disable_socket_group_full_dps)
        self.win.check_SocketGroup_FullDPS.stateChanged.connect(self.enable_disable_socket_group_full_dps)

        active_skill_set = int(self.xml_skills.get("activeSkillSet", 0))
        if active_skill_set > len(self.skill_sets_list) - 1:
            active_skill_set = 0
        # triggers change_skill_set
        self.win.combo_SkillSet.setCurrentIndex(active_skill_set)

    def save(self):
        """
        Save internal structures back to the build's skills object
        """
        self.xml_skills.set("sortGemsByDPS", bool_to_str(self.win.check_SortByDPS.isChecked()))
        self.xml_skills.set("matchGemLevelToCharacterLevel", bool_to_str(self.win.check_MatchToLevel.isChecked()))
        self.xml_skills.set("showAltQualityGems", bool_to_str(self.win.check_ShowGemQualityVariants.isChecked()))
        self.xml_skills.set("sortGemsByDPSField", self.win.combo_SortByDPS.currentText())
        self.xml_skills.set("showSupportGemTypes", self.win.combo_ShowSupportGems.currentText())
        self.xml_skills.set("defaultGemLevel", str(self.win.spin_DefaultGemLevel.value()))
        self.xml_skills.set("defaultGemQuality", str(self.win.spin_DefaultGemQuality.value()))
        return self.xml_skills

    @Slot()
    def change_skill_set(self, new_index):
        """
        This triggers when the user changes skill sets using the combobox.
        Will also activate if user changes skill sets in the manage dialog
        :param new_index: int: index of the current selection
               -1 will occur during a combobox clear
        :return:
        """
        # _debug("new_index", new_index)
        if 0 <= new_index < len(self.skill_sets_list):
            self.show_skill_set(self.skill_sets_list[new_index])

    def define_socket_group_label(self, index, item=None, group=None):
        """
        Setup the passed in QListWidgetItem text depending on whether it's active or not, etc
        :param: item: QListWidgetItem:
        :param: group: ElementTree.Element:
        :return: string
        """
        if group is None:
            group = self.xml_current_socket_group
        if item is None:
            item = QListWidgetItem("")

        _label = group.get("label")
        # build label from active skills if needed
        if _label == "":
            # _debug("Socket group1", _label, group)
            for gem in group.findall("Gem"):
                # If this gen is not a support gem and is enabled (the far right control)
                if "Support" not in gem.get("skillId") and str_to_bool(gem.get("enabled")):
                    _label += f'{gem.get("nameSpec")}, '

        # set enabled based on the group control and whether there is an active skill in the group
        if _label == "":
            _label = "<no active skills>"
        else:
            _label = _label.rstrip(", ")

        full_dps = str_to_bool(group.get("includeInFullDPS"))
        enabled = str_to_bool(group.get("enabled")) and _label != ""
        active = self.build.mainSocketGroup == index
        item.setText(
            f"{_label}{not enabled and ' (Disabled)' or ''}{full_dps and ' (FullDPS)' or ''}{active and ' (Active)' or ''}"
        )
        # get a copy of the label with out all the extra information
        item.setWhatsThis(_label)

        # change colour (dim) if it's disabled or no active skills
        if not enabled:
            item.setForeground(QColor(ColourCodes.LIGHTGRAY.value))

        return item

    def change_active_socket_group_label(self, old_index, new_index):
        """
        This changes the text on the socket group list as the
        :param old_index:
        :param new_index:
        :return: N/A
        """
        _debug(old_index, new_index)
        # turn off old one by sending -1
        self.define_socket_group_label(-1, self.win.list_SocketGroups.item(old_index), self.xml_current_skill_set[old_index])
        self.define_socket_group_label(new_index, self.win.list_SocketGroups.item(new_index), self.xml_current_skill_set[new_index])

    def show_skill_set(self, _set, current_index=0):
        """
        show a set of skills
        :param _set: ElementTree.Element. This set of skills
        :param current_index: set the current one active at the end of the function
        :return: N/A
        """
        # disconnect triggers
        self.win.list_SocketGroups.currentRowChanged.disconnect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)
        self.win.check_SocketGroupEnabled.stateChanged.disconnect(self.enable_disable_socket_group_full_dps)
        self.win.check_SocketGroup_FullDPS.stateChanged.disconnect(self.enable_disable_socket_group_full_dps)

        # unload the previous set, saving it's state
        if self.xml_current_skill_set is not None:
            # may not need to do this as we are operating straight into the xml
            pass  # unload the previous set, saving it's state

        self.clear_gem_ui_list()
        self.win.list_SocketGroups.clear()
        self.xml_current_skill_set = _set

        # Find all Socket Groups (<Skill> in the xml) and add them to the Socket Group list
        socket_groups = _set.findall("Skill")
        # _debug("len, socket_groups", len(socket_groups), socket_groups)
        for idx, group in enumerate(socket_groups):
            self.win.list_SocketGroups.addItem(self.define_socket_group_label(idx, None, group))

        self.win.load_socket_group(
            [self.win.list_SocketGroups.item(i).whatsThis() for i in range(self.win.list_SocketGroups.count())]
        )

        # re-connect triggers
        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)
        self.win.check_SocketGroupEnabled.stateChanged.connect(self.enable_disable_socket_group_full_dps)
        self.win.check_SocketGroup_FullDPS.stateChanged.connect(self.enable_disable_socket_group_full_dps)

        # Trigger the filling out of the right hand side UI elements
        self.win.list_SocketGroups.setCurrentRow(current_index)

    @Slot()
    def new_socket_group(self):
        """
        Create a new socket group
        Actions for when the new socket group button is pressed
        :return:
        """
        self.xml_current_skill_set.append(ET.fromstring(empty_socket_group))
        self.show_skill_set(self.xml_current_skill_set, len(self.xml_current_skill_set) - 1)

    def load_socket_group(self, _index):
        """
        Load a socket group into the UI, unloading the previous one
        :param _index: index to display
        :return: N/A
        """
        # _debug("index", _index)
        # _debug("self.current_skill_set, len", self.current_skill_set, len(self.current_skill_set))
        self.clear_gem_ui_list()
        if index_exists(self.xml_current_skill_set, _index):
            # save changes to current group
            if self.xml_current_socket_group is not None:
                self.xml_current_socket_group.set("slot", self.win.combo_SocketedIn.currentText())
                self.xml_current_socket_group.set("label", self.win.lineedit_SkillLabel.text())
                self.xml_current_socket_group.set("enabled", bool_to_str(self.win.check_SocketGroupEnabled.isChecked()))
                self.xml_current_socket_group.set(
                    "includeInFullDPS", bool_to_str(self.win.check_SocketGroup_FullDPS.isChecked())
                )

            # assign and setup new group
            self.xml_current_socket_group = self.xml_current_skill_set[_index]
            # _debug("self.current_socket_group", self.current_socket_group)
            if self.xml_current_socket_group is not None:
                self.win.lineedit_SkillLabel.setText(self.xml_current_socket_group.get("label"))
                set_combo_index_by_text(self.win.combo_SocketedIn, self.xml_current_socket_group.get("slot"))
                self.win.check_SocketGroupEnabled.setChecked(
                    str_to_bool(self.xml_current_socket_group.get("enabled", "false"))
                )
                self.win.check_SocketGroup_FullDPS.setChecked(
                    str_to_bool(self.xml_current_socket_group.get("includeInFullDPS", "false"))
                )
                for idx, gem in enumerate(self.xml_current_socket_group.findall("Gem")):
                    self.create_gem_ui(idx, gem)
                # Create an empty gem at the end
                self.create_gem_ui(len(self.gem_ui_list), None)

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

    def create_gem_ui(self, index, gem=None):
        """
        Create a new GemUI class and fill it. These are the widgets set on the right
        :param index: int: number of this gem in this skill group
        :param gem: the xml element if known
        :return: N/A
        """
        # _debug("create_gem_ui", index, gem)
        # In most cases this will be the first one autocreated
        if index_exists(self.gem_ui_list, index):
            self.gem_ui_list[index].load(gem)
        else:
            # self.gem_ui_list[index] = GemUI(index, self.win.frame_SkillsTab, gem)
            self.gem_ui_list[index] = GemUI(index, self.win.scrollAreaSkillsContents, gem)
            # self.current_socket_group.append(gem)

        ui: GemUI = self.gem_ui_list[index]
        ui.fill_gem_list(self.json_gems, self.win.combo_ShowSupportGems.currentText())

        # this one deletes the gem
        ui.check_GemRemove.stateChanged.connect(lambda checked: self.gem_remove_checkbox_selected(index))

        # update the socket label when something changes
        ui.combo_GemList.currentTextChanged.connect(lambda checked: self.update_from_gemlist(index))
        ui.check_GemEnabled.stateChanged.connect(lambda checked: self.enable_disable_socket_group_full_dps(index))
        return ui

    def remove_gem_ui(self, index):
        """
        Remove a GemUI class. TBA on full actions needed.
        :param index: int: index of frame/GemUI() to remove
        :return:
        """
        if index_exists(self.gem_ui_list, index):
            # self.current_skill_set[_index].remove(self.gem_ui_list[index].gem)
            del self.gem_ui_list[index]
        # update all gem_ui's index incase the one being deleted was in the middle
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
                gem_ui.save()
            # don'tbe tempted by 'del self.gem_ui_list[idx]'. You'll get a dictionary error
            del gem_ui
        self.gem_ui_list.clear()

    def load_gems_json(self):
        """
        Load gems.json and remove bad entries, like [Unused] and not released
        :return: dictionary of valid entries
        """
        gems = read_json(Path(self.pob_config.exe_dir, "Data/gems.json"))
        if gems is None:
            return None
        gems_list = list(gems.keys())
        for g in gems_list:
            if "Royale" in g:
                del gems[g]
            else:
                base_item = gems[g]["base_item"]
                if base_item is None:
                    del gems[g]
                elif base_item["release_state"] == "unreleased":
                    del gems[g]
                elif "DNT" in base_item["display_name"]:
                    del gems[g]
                elif gems[g].get("is_support", False):
                    # remove 'Support' from the name
                    _name = base_item["display_name"]
                    base_item["display_name"] = _name.replace(" Support", "")
                    base_item["full_name"] = _name

        # make a list by name as well, list supports using the fullname (Faster Attacks Support)
        #  and the display name (Faster Attacks)
        for g in gems.keys():
            display_name = gems[g]["base_item"]["display_name"]
            self.gems_by_name[display_name] = gems[g]
            self.gems_by_name[display_name]["skillId"] = g
            # add supports using the full name
            full_name = gems[g]["base_item"].get("full_name", None)
            if full_name is not None:
                self.gems_by_name[full_name] = gems[g]
                self.gems_by_name[full_name]["skillId"] = g

        return gems
    # load_gems_json

    @Slot()
    def gem_remove_checkbox_selected(self, _key):
        """
        Actions required for selecting the checkbox to the left of the GemUI()
        :param _key: the index passed through to lambda, this is actually the key into gem_ui_list
        :return:
        """
        if _key in self.gem_ui_list.keys():
            self.remove_gem_ui(_key)

    @Slot()
    def enable_disable_socket_group_full_dps(self, checked):
        """
        Actions for when the socket group is enable checkbox is triggered
        Change the socket group label and save value to xml
        :param checked:
        :return:
        """
        self.xml_current_socket_group.set("enabled", bool_to_str(self.win.check_SocketGroupEnabled.isChecked()))
        self.xml_current_socket_group.set(
            "includeInFullDPS", bool_to_str(self.win.check_SocketGroup_FullDPS.isChecked())
        )
        item = self.win.list_SocketGroups.currentItem()
        self.define_socket_group_label(self.win.list_SocketGroups.currentIndex(), item)
        self.win.load_socket_group(
            [self.win.list_SocketGroups.item(i).whatsThis() for i in range(self.win.list_SocketGroups.count())]
        )

    @Slot()
    def update_from_gemlist(self, _key):
        """
        This is different to the internal GemUI() actions
        This performs all needed actions for the SkillUI class outside the GemUI() class
        Add it to the xml if needed
        :param _key: the index passed through to lambda, this is actually the key into gem_ui_list
        :return: N/A
        """
        _debug(_key, len(self.gem_ui_list) - 1)
        # Check if this is gem the last gem and add it to the xml if needed
        if _key == len(self.gem_ui_list) - 1:
            ui: GemUI = self.gem_ui_list[_key]
            ui.save()
            if ui.gem not in self.xml_current_socket_group.findall("Gem"):
                self.xml_current_socket_group.append(ui.gem)
                print("update_from_gemlist: , not found, adding")
                # Create an empty gem at the end
                self.create_gem_ui(len(self.gem_ui_list), None)
        self.enable_disable_socket_group_full_dps(_key)


"""   ----------------------------------------------------------------------------------------------"""


class GemUI:
    """
    A class to manage one gem/skill on the right hand side of the UI
    """

    def __init__(self, _index, parent, gem=None) -> None:
        self.frame_height = 40
        self._index = _index
        self.gem = gem
        if gem is None:
            gem = ET.fromstring(empty_gem)

        self.frame = QFrame(parent)
        # must be set *after* creating the frame, as it will position the frame
        self.index = _index

        self.check_GemRemove = QCheckBox(self.frame)
        self.check_GemRemove.setGeometry(QRect(10, 12, 20, 20))
        self.check_GemRemove.setChecked(True)
        self.combo_GemList = QComboBox(self.frame)
        self.combo_GemList.setGeometry(QRect(30, 10, 260, 22))
        self.combo_GemList.setDuplicatesEnabled(False)
        self.combo_GemList.setObjectName("combo_GemList")
        self.spin_GemLevel = QSpinBox(self.frame)
        self.spin_GemLevel.setGeometry(QRect(300, 10, 50, 22))
        self.spin_GemLevel.setMinimum(1)
        self.spin_GemLevel.setMaximum(20)
        self.spin_GemQuality = QSpinBox(self.frame)
        self.spin_GemQuality.setGeometry(QRect(360, 10, 50, 22))
        self.spin_GemQuality.setMaximum(40)
        self.combo_GemVariant = QComboBox(self.frame)
        self.combo_GemVariant.setObjectName("combo_GemVariant")
        self.combo_GemVariant.addItem("Default", "Default")
        self.combo_GemVariant.addItem("Anomalous", "Alternate1")
        self.combo_GemVariant.addItem("Divergent", "Alternate2")
        self.combo_GemVariant.addItem("Phantasmal", "Alternate3")
        self.combo_GemVariant.setGeometry(QRect(420, 10, 90, 22))
        self.check_GemEnabled = QCheckBox(self.frame)
        self.check_GemEnabled.setGeometry(QRect(530, 12, 20, 20))
        self.check_GemEnabled.setChecked(True)
        self.spin_GemCount = QSpinBox(self.frame)
        self.spin_GemCount.setGeometry(QRect(570, 10, 50, 22))
        self.spin_GemCount.setMinimum(1)
        self.spin_GemCount.setMaximum(20)
        # !!! Why are these not visible by default
        self.frame.setVisible(True)

        self._level = None
        self._count = None
        self._quality = None
        self._enabled = None
        self._qualityId = None
        self._skillId = None

        self.load(gem)
        # self.check_GemRemove.stateChanged.connect(self.gem_remove_checkbox_selected)

    def __del__(self):
        """
        Remove PySide elements, prior to being deleted.
        The frame appears not to have a list of children, only layouts.
        :return: N/A
        """
        # Setup triggers to save information back the the xml object
        self.spin_GemLevel.valueChanged.disconnect(self.save)
        self.spin_GemQuality.valueChanged.disconnect(self.save)
        self.spin_GemCount.valueChanged.disconnect(self.save)
        self.check_GemEnabled.stateChanged.disconnect(self.save)
        self.combo_GemVariant.currentTextChanged.disconnect(self.save)

        self.check_GemRemove.setParent(None)
        self.combo_GemList.setParent(None)
        self.spin_GemLevel.setParent(None)
        self.spin_GemQuality.setParent(None)
        self.combo_GemVariant.setParent(None)
        self.check_GemEnabled.setParent(None)
        self.spin_GemCount.setParent(None)
        self.frame.setParent(None)

    @property
    def index(self):
        """
        Needed so we can have a setter function
        :return: int: The index of this gem
        """
        return self._index

    @index.setter
    def index(self, new_index):
        """
        This will allow it to move it's y position, so when one is deleted from in the middle or a reorder
        command is given, when we can just change the index and have it magically move.
        :param new_index: int:
        :return:
        """
        self._index = new_index
        self.frame.setGeometry(10, 10 + (new_index * self.frame_height), 620, self.frame_height)
        # self.frame.setGeometry(400, 90 + (new_index * self.frame_height), 620, self.frame_height)

    @property
    def skillId(self):
        """
        Needed so we can have a setter function
        :return: str: The name of this gem
        """
        return self._skillId

    @skillId.setter
    def skillId(self, new_skill_id):
        self._skillId = new_skill_id
        self.check_GemRemove.setEnabled(new_skill_id != "" and self.index != 0)
        self.spin_GemCount.setVisible("Support" not in new_skill_id)

    def load(self, gem):
        """
        load the UI elements from the xml element
        :return: N/A
        """
        self.gem = gem
        if gem is not None:
            self._level = int(gem.get("level", 1))
            self.spin_GemLevel.setValue(self._level)
            self._quality = int(gem.get("quality", 0))
            self.spin_GemQuality.setValue(self._quality)
            self._count = int(gem.get("count", 1))
            self.spin_GemCount.setValue(self._count)

            self._enabled = gem.get("enabled")
            self.check_GemEnabled.setChecked(str_to_bool(self._enabled))

            self._qualityId = gem.get("qualityId", "Default")
            set_combo_index_by_data(self.combo_GemVariant, self._qualityId)
            self.skillId = gem.get("skillId")
            # self.frame.setObjectName(f"GemUI.frame.{self.skillId}")

        # Setup triggers to save information back the the xml object
        self.spin_GemLevel.valueChanged.connect(self.save)
        self.spin_GemQuality.valueChanged.connect(self.save)
        self.spin_GemCount.valueChanged.connect(self.save)
        self.check_GemEnabled.stateChanged.connect(self.save)
        self.combo_GemVariant.currentTextChanged.connect(self.save)

    @Slot()
    def save(self):
        """
        Save the UI elements into the xml element
        This is called by all the elements in this class
        :return: N/A
        """
        if self.gem is not None:
            self._level = self.spin_GemLevel.value()
            self.gem.set("level", str(self._level))
            self._quality = self.spin_GemQuality.value()
            self.gem.set("quality", str(self._quality))
            self._count = self.spin_GemCount.value()
            self.gem.set("count", str(self._count))

            self._enabled = bool_to_str(self.check_GemEnabled.isChecked())
            self.gem.set("enabled", self._enabled)

            self._qualityId = self.combo_GemVariant.currentData()
            self.gem.set("qualityId", self._qualityId)
            _skill_id = self.combo_GemList.currentData() or ""
            if _skill_id is not None:
                self.skillId = _skill_id
                self.gem.set("skillId", _skill_id)
                self.gem.set("nameSpec", self.combo_GemList.currentText() or "")

    def fill_gem_list(self, gem_list, show_support_gems):
        """
        File the gem list combo
        :param gem_list: a list of curated gems available
        :param show_support_gems: if True, only add non-awakened gems
        :return:
        """

        def add_colour(index):
            """
            Add colour to a gem name
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
                colour = False
            if colour:
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
        if self.gem is not None and self._skillId != "":
            self.combo_GemList.setCurrentIndex(set_combo_index_by_data(self.combo_GemList, self._skillId))
        else:
            self.combo_GemList.setCurrentIndex(-1)

        # Setup trigger to save information back the the xml object
        self.combo_GemList.currentTextChanged.connect(self.save)


# def test() -> None:
#     skills_ui = SkillsUI()
#     print(skills_ui)
#
#
# if __name__ == "__main__":
#     test()
