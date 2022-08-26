"""
This Class manages all the elements and owns some elements of the "SKILLS" tab
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from qdarktheme.qtpy.QtCore import QRect, Slot
from qdarktheme.qtpy.QtGui import QColor
from qdarktheme.qtpy.QtWidgets import QCheckBox, QComboBox, QFrame, QListWidgetItem, QSpinBox

from PoB_Main_Window import Ui_MainWindow
from constants import ColourCodes, empty_socket_group, empty_gem
from pob_config import Config, _debug, str_to_bool, index_exists
from pob_file import read_json
from ui_utils import set_combo_index_by_data, set_combo_index_by_text


class SkillsUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self.skills = None
        self.skill_sets = []
        self.current_skill_set = None
        self.current_socket_group = None
        self.gems = self.load_gems_json()

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

        # dictionary for holding the GemUI representions of the gems in each socket group
        self.gem_ui_list = {}

        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)
        self.win.btn_NewSocketGrp.clicked.connect(self.new_socket_group)

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _skills):
        """
        Load internal structures from the build object
        :param _skills: Reference to the xml tree
        :return: N/A
        """
        self.skills = _skills
        self.win.check_SortByDPS.setChecked(str_to_bool(self.skills.get("sortGemsByDPS", True)))
        self.win.check_MatchToLevel.setChecked(str_to_bool(self.skills.get("matchGemLevelToCharacterLevel", False)))
        self.win.check_ShowGemQualityVariants.setChecked(str_to_bool(self.skills.get("showAltQualityGems", False)))
        set_combo_index_by_data(self.win.combo_SortByDPS, self.skills.get("sortGemsByDPSField", "FullDPS"))
        set_combo_index_by_data(self.win.combo_ShowSupportGems, self.skills.get("showSupportGemTypes", "ALL"))
        self.win.spin_DefaultGemLevel.setValue(int(self.skills.get("defaultGemLevel", 20)))
        self.win.spin_DefaultGemQuality.setValue(int(self.skills.get("defaultGemQuality", 0)))

        # disconnect triggers
        self.win.list_SocketGroups.currentRowChanged.disconnect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)

        self.win.combo_SkillSet.clear()
        self.skill_sets.clear()
        _sets = self.skills.findall("SkillSet")
        if len(_sets) > 0:
            for idx, _set in enumerate(self.skills.findall("SkillSet")):
                self.skill_sets.append(_set)
                self.win.combo_SkillSet.addItem(_set.get("title", f"Default{idx + 1}"), idx)
        else:
            # The lua version won't create a <skillset> (socket group) if there is only one.
            # let's create one so we have code compatibility in all circumstances
            _set = ET.Element("SkillSet")
            self.skill_sets.append(_set)
            self.win.combo_SkillSet.addItem("Default", 0)
            self.skills.append(_set)
            # Move skills to the new socket group
            socket_group = self.skills.findall("Skill")
            for group in socket_group:
                _set.append(group)
                self.skills.remove(group)

        # re-connect triggers
        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)

        active_skill_set = int(self.skills.get("activeSkillSet", 0))
        # _debug("active_skill_set, len(self.skill_sets)", active_skill_set, len(self.skill_sets))
        if active_skill_set > len(self.skill_sets) - 1:
            active_skill_set = 0
        # triggers change_skill_set
        self.win.combo_SkillSet.setCurrentIndex(active_skill_set)

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
        if 0 <= new_index < len(self.skill_sets):
            self.show_skill_set(self.skill_sets[new_index])

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

        # unload the previous set, saving it's state
        if self.current_skill_set is not None:
            pass  # unload the previous set, saving it's state

        self.clear_gem_ui_list()
        self.win.list_SocketGroups.clear()
        # if self.current_skill_set:
        #     print_a_xml_element(self.current_skill_set)
        self.current_skill_set = _set
        # print_a_xml_element(self.current_skill_set)

        # Find all Socket Groups (<Skill> in the xml) and add them to the Socket Group list
        socket_groups = _set.findall("Skill")
        # _debug("len, socket_groups", len(socket_groups), socket_groups)
        if len(socket_groups) > 0:
            _label = ""
            enabled = False
            for group in socket_groups:
                _label = group.get("label")
                _debug("Socket group", _label, group)
                enabled = str_to_bool(group.get("enabled"))
                if _label == "":
                    for gem in group.findall("Gem"):
                        skill_id = gem.get("skillId")
                        if "Support" not in skill_id:
                            _label += f'{gem.get("nameSpec")}, '
                enabled = enabled and _label != ""
                if _label == "":
                    _label = "<no active skills>"
                # use a QListWidgetItem so we can manipulate the text as we want
                item = QListWidgetItem(_label.rstrip(", "))
                if not enabled:
                    # change colour (dim) if it's disabled or no active skills
                    item.setForeground(QColor(ColourCodes.LIGHTGRAY.value))
                    item.setText(f"{_label.rstrip(', ')} (Disabled)")
                _debug("Socket group", item.text())
                self.win.list_SocketGroups.addItem(item)

        if index_exists(self.current_skill_set, 0):
            self.load_socket_group(0)

        # re-connect triggers
        self.win.list_SocketGroups.currentRowChanged.connect(self.change_socket_group)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)

        # Trigger the filling out of the right hand side UI elements
        self.win.list_SocketGroups.setCurrentRow(current_index)

    @Slot()
    def new_socket_group(self):
        """
        Create a new socket group
        Actions for when the new socket group button is pressed
        :return:
        """
        self.current_skill_set.append(ET.fromstring(empty_socket_group))
        self.show_skill_set(self.current_skill_set, len(self.current_skill_set) - 1)

    def load_socket_group(self, _index):
        """
        Load a socket group into the UI, unloading the previous one
        :param _index: index to display
        :return: N/A
        """
        # _debug("index", _index)
        # _debug("self.current_skill_set, len", self.current_skill_set, len(self.current_skill_set))
        self.clear_gem_ui_list()
        if index_exists(self.current_skill_set, _index):
            self.current_socket_group = self.current_skill_set[_index]
            _debug("self.current_socket_group", self.current_socket_group)
            if self.current_socket_group is not None:
                self.win.lineedit_SkillLabel.setText(self.current_socket_group.get("label"))
                set_combo_index_by_text(self.win.combo_SocketedIn, self.current_socket_group.get("slot"))
                self.win.check_SocketGroupEnabled.setChecked(
                    str_to_bool(self.current_socket_group.get("enabled", "false"))
                )
                self.win.check_SocketGroup_FullDPS.setChecked(
                    str_to_bool(self.current_socket_group.get("includeInFullDPS", "false"))
                )
                for idx, gem in enumerate(self.current_socket_group.findall("Gem")):
                    self.create_gem_ui(idx, gem)
                # Create an empty one at the end
                self.create_gem_ui(len(self.gem_ui_list), None)

    @Slot()
    def change_socket_group(self, new_skill):
        """
        This triggers when the user changes an entry on the list of skills
        :param new_skill: int: row number.
               -1 will occur during a combobox clear
        :return: N/A
        """
        # _debug("new_skill", new_skill)
        self.load_socket_group(new_skill)

    def save(self):
        """
        Save internal structures back to the build object
        """
        return self.skills

    def create_gem_ui(self, index, gem=None):
        """
        Create a new GemUI class and fill it. This is the dropdown on the right
        :param index: int: number of this gem in this skill group
        :param gem: the xml element if known
        :return: N/A
        """
        # _debug("create_gem_ui", index, gem)
        # In most cases this will be the first one autocreated
        if index_exists(self.gem_ui_list, index):
            self.gem_ui_list[index].load(gem)
        else:
            self.gem_ui_list[index] = GemUI(index, self.win.frame_SkillsTab, gem)
        ui: GemUI = self.gem_ui_list[index]
        ui.fill_gem_list(self.gems, self.win.combo_ShowSupportGems.currentText())

        ui.check_GemRemove.stateChanged.connect(lambda checked: self.gem_remove_checkbox_selected(index))
        return ui

    def remove_gem_ui(self, index):
        """
        Remove a GemUI class. TBA onfull actions needed.
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
            self.gem_ui_list[idx].save()
            # don'tbe tempted by 'del self.gem_ui_list[idx]'. You'll get a dictionary error
            gem_ui = self.gem_ui_list[idx]
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
        return gems

    @Slot()
    def gem_remove_checkbox_selected(self, _key):
        """
        Actions required for selecting the checkbox to the left of the GemUI()
        :param _key: the index passed through to lambda, this is actually the key into gem_ui_list
        :return:
        """
        if _key in self.gem_ui_list.keys():
            self.remove_gem_ui(_key)


class GemUI:
    """
    A class to manage one gem/skill on the right hand side of the UI
    """

    def __init__(self, _index, parent, gem=None) -> None:
        self._index = _index
        self.gem = gem
        if gem is None:
            self.gem = ET.fromstring(empty_gem)
        self.frame_height = 40

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
        Remove PySide elements, prior to being deleted
        :return: N/A
        """
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
        Needed so we can have a setter
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
        self.frame.setGeometry(400, 90 + (new_index * self.frame_height), 620, self.frame_height)

    def load(self, gem):
        """
        load the UI elements from the xml element
        :return: N/A
        """
        self.gem = gem
        if gem is not None:
            self._level = int(gem.get("level"))
            self.spin_GemLevel.setValue(self._level)
            self._quality = int(gem.get("quality"))
            self.spin_GemQuality.setValue(self._quality)
            self._count = int(gem.get("count"))
            self.spin_GemCount.setValue(self._count)

            self._enabled = gem.get("enabled")
            self.check_GemEnabled.setChecked(str_to_bool(self._enabled))

            self._qualityId = gem.get("qualityId")
            set_combo_index_by_data(self.combo_GemVariant, self._qualityId)
            self._skillId = gem.get("skillId")
            self.frame.setObjectName(f"GemUI.frame.{self._skillId}")
        self.check_GemRemove.setEnabled(self._skillId != "")

    def save(self):
        """
        Save the UI elements into the xml element
        :return: N/A
        """
        if self.gem is not None:
            self._level = self.spin_GemLevel.value()
            self.gem.set("level", str(self._level))
            self._quality = self.spin_GemQuality.value()
            self.gem.set("quality", str(self._quality))
            self._count = self.spin_GemCount.value()
            self.gem.set("count", str(self._count))

            self._enabled = self.check_GemEnabled.isChecked() and "true" or "false"
            self.gem.set("enabled", self._enabled)

            self.gem.set("qualityId", self._qualityId)
            self.gem.set("skillId", self._skillId)

    def fill_gem_list(self, gem_list, show_support_gems):
        """
        File the gem list combo
        :param gem_list: a list of curated gems available
        :param show_support_gems: if True, only add non-awakened gems
        :return:
        """
        if show_support_gems == "Awakened":
            for g in gem_list:
                display_name = gem_list[g]["base_item"]["display_name"]
                if "Awakened" in display_name:
                    self.combo_GemList.addItem(display_name, g)
        else:
            for g in gem_list:
                display_name = gem_list[g]["base_item"]["display_name"]
                if show_support_gems == "Normal" and "Awakened" in display_name:
                    continue
                self.combo_GemList.addItem(display_name, g)
        # set the ComboBox dropdown width.
        self.combo_GemList.view().setMinimumWidth(self.combo_GemList.minimumSizeHint().width())
        # ToDo: Sort by other methods
        # Sort Alphabetically
        self.combo_GemList.model().sort(0)
        if self.gem is not None and self._skillId != "":
            self.combo_GemList.setCurrentIndex(set_combo_index_by_data(self.combo_GemList, self._skillId))
        else:
            self.combo_GemList.setCurrentIndex(-1)
            self.combo_GemList.showPopup()


# def test() -> None:
#     skills_ui = SkillsUI()
#     print(skills_ui)
#
#
# if __name__ == "__main__":
#     test()
