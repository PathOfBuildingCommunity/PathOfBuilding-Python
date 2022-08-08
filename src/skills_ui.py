"""
This Class manages all the elements and owns some elements of the "SKILLS" tab
"""

import xml.etree.ElementTree as ET

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

from PoB_Main_Window import Ui_MainWindow
from constants import *
from constants import _VERSION
from pob_config import *
from pob_file import *
from ui_utils import *


class SkillsUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self.skills = None
        self.skill_sets = []
        self.current_skill_set = None
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

        self.gem_ui_list = {}
        self.create_gem_ui(0)

        self.win.list_Skills.currentRowChanged.connect(self.change_skill)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _skills):
        """
        Load internal structures from the build object
        :param _build: Reference to the xml tree
        :return: N/A
        """
        self.skills = _skills
        self.win.check_SortByDPS.setChecked(
            str_to_bool(self.skills.get("sortGemsByDPS", True))
        )
        self.win.check_MatchToLevel.setChecked(
            str_to_bool(self.skills.get("matchGemLevelToCharacterLevel", False))
        )
        self.win.check_ShowGemQualityVariants.setChecked(
            str_to_bool(self.skills.get("showAltQualityGems", False))
        )
        set_combo_index_by_data(
            self.win.combo_SortByDPS, self.skills.get("sortGemsByDPSField", "FullDPS")
        )
        set_combo_index_by_data(
            self.win.combo_ShowSupportGems,
            self.skills.get("showSupportGemTypes", "ALL"),
        )
        self.win.spin_DefaultGemLevel.setValue(
            int(self.skills.get("defaultGemLevel", 20))
        )
        self.win.spin_DefaultGemQuality.setValue(
            int(self.skills.get("defaultGemQuality", 0))
        )

        # disconnect triggers
        self.win.list_Skills.currentRowChanged.disconnect(self.change_skill)
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)

        self.win.combo_SkillSet.clear()
        _sets = self.skills.findall("SkillSet")
        if len(_sets) > 0:
            for idx, _set in enumerate(self.skills.findall("SkillSet")):
                self.skill_sets.append(_set)
                self.win.combo_SkillSet.addItem(
                    _set.get("title", f"Default{idx + 1}"), idx
                )
        else:
            _set = ET.Element("SkillSet")
            self.skill_sets.append(_set)
            self.win.combo_SkillSet.addItem("Default", 0)
            self.skills.append(_set)
            # add the skills to this one
            skills = self.skills.findall("Skill")
            for skill in skills:
                _set.append(skill)
                self.skills.remove(skill)

        # re-connect triggers
        self.win.list_Skills.currentRowChanged.connect(self.change_skill)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)

        active_set = int(self.skills.get("activeSkillSet", 1)) - 1
        self.win.combo_SkillSet.setCurrentIndex(active_set)

    @Slot()
    def change_skill_set(self, new_set):
        """
        This triggers when the user changes skill sets using the combobox.
        Will also activate if user changes skill sets in the manage dialog
        :param new_set: int: index of the current selection
               -1 will occur during a combobox clear
        :return:
        """
        self.load_skill_set(self.skill_sets[self.win.combo_SkillSet.currentData()])

    def load_skill_set(self, _set):
        """

        :param _set:
        :return:
        """
        # disconnect triggers
        self.win.list_Skills.currentRowChanged.disconnect(self.change_skill)
        self.win.combo_SkillSet.currentIndexChanged.disconnect(self.change_skill_set)

        # unload the previous set, saving it's state
        if self.current_skill_set is not None:
            pass  # unload the previous set, saving it's state

        self.win.list_Skills.clear()
        self.current_skill_set = _set
        skills = _set.findall("Skill")
        if len(skills) > 0:
            for skill in skills:
                _label = skill.get("label")
                if _label == "":
                    # _label = "Need to decide skills"
                    for gem in skill.findall("Gem"):
                        skillId = gem.get("skillId")
                        if "Support" not in skillId:
                            _label += f'{gem.get("nameSpec")}, '
                self.win.list_Skills.addItem(_label.rstrip(", "))

        # re-connect triggers
        self.win.list_Skills.currentRowChanged.connect(self.change_skill)
        self.win.combo_SkillSet.currentIndexChanged.connect(self.change_skill_set)

        # Trigger the filling out of the right hand side UI elements
        self.win.list_Skills.setCurrentRow(0)
        pass

    @Slot()
    def change_skill(self, new_skill):
        """
        This triggers when the user changes an entry on the list of skills
        :param new_skill: int: row number.
               -1 will occur during a combobox clear
        :return: N/A
        """
        print(new_skill, type(new_skill))

    def save(self):
        """
        Save internal structures back to the build object
        """
        return self.skills

    def load_gems_json(self):
        """
        Load gems.json and remove bad entries, like [Unused] and not released
        :return: dictionary of valid entries
        """
        gems = read_json(Path(self.pob_config.exeDir, "Data/gems.json"))
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
        return gems

    def create_gem_ui(self, index, gem=None):
        """
        Create a new GemUI class and fill it
        :param index: int: number of this gem in this skill group
        :param gem: the xml element
        :return: N/A
        """
        # In most cases this will be the first one autocreated
        if index_exists(self.gem_ui_list, index):
            self.gem_ui_list[index].load(gem)
        else:
            self.gem_ui_list[index] = GemUI(index, self.win.frame_SkillsTab, gem)
        ui: GemUI = self.gem_ui_list[index]
        ui.fill_gem_list(self.gems)

    def remove_gem_ui(self, index):
        """
        Remove a GemUI class. TBA onfull actions needed.
        :param index: index of frame/GemUI() to remove
        :return:
        """


# def test() -> None:
#     skills_ui = SkillsUI()
#     print(skills_ui)
#
#
# if __name__ == "__main__":
#     test()


class SkillGroup:
    def __init__(self, _group) -> None:
        self.set = _group
        print(_group)


class GemUI:
    """
    A class to manage one gem/skill on the right hand side of the UI
    """

    def __init__(self, _index, tag: QFrame, gem=None) -> None:
        self._index = _index
        self.gem = gem

        self.frame = QFrame(tag)
        # must be set *after* creating the frame, as it will position the frame
        self.index = _index

        self.check_GemRemove = QCheckBox(self.frame)
        self.check_GemRemove.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemRemove.setChecked(True)
        self.check_GemRemove.setEnabled(_index != 0)
        self.combo_GemList = QComboBox(self.frame)
        self.combo_GemList.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel = QSpinBox(self.frame)
        self.spin_GemLevel.setGeometry(QRect(210, 10, 50, 22))
        self.spin_GemLevel.setMinimum(1)
        self.spin_GemLevel.setMaximum(20)
        self.spin_GemQuality = QSpinBox(self.frame)
        self.spin_GemQuality.setGeometry(QRect(270, 10, 50, 22))
        self.spin_GemQuality.setMaximum(40)
        self.combo_GemVariant = QComboBox(self.frame)
        self.combo_GemVariant.addItem("Default", "Default")
        self.combo_GemVariant.addItem("Anomalous", "Alternate1")
        self.combo_GemVariant.addItem("Divergent", "Alternate2")
        self.combo_GemVariant.addItem("Phantasmal", "Alternate3")
        self.combo_GemVariant.setGeometry(QRect(330, 10, 80, 22))
        self.check_GemEnabled = QCheckBox(self.frame)
        self.check_GemEnabled.setGeometry(QRect(430, 10, 20, 20))
        self.check_GemEnabled.setChecked(True)
        self.spin_GemCount = QSpinBox(self.frame)
        self.spin_GemCount.setGeometry(QRect(465, 10, 50, 22))
        self.spin_GemCount.setMinimum(1)
        self.spin_GemCount.setMaximum(20)

        self._level = None
        self._count = None
        self._quality = None
        self._enabled = None
        self._qualityId = None
        self._skillId = None

        self.load(gem)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, new_index):
        self._index = new_index
        self.frame.setGeometry(
            QRect(400, 100 + (new_index * self.frame.height()), 520, 40)
        )

    def load(self, gem):
        """
        load the UI elements from the xml element
        :return: N/A
        """
        if gem is not None:
            self._level = gem.get("level")
            self.spin_GemLevel.setValue(self._level)
            self._quality = gem.get("quality")
            self.spin_GemQuality.setValue(self._quality)
            self._count = gem.get("count")
            self.spin_GemCount.setValue(self._count)

            self._enabled = gem.get("enabled")
            self.check_GemEnabled.setChecked(str_to_bool(self._enabled))

            self._qualityId = gem.get("qualityId")
            set_combo_index_by_data(self.combo_GemVariant, self._qualityId)
            self._skillId = gem.get("skillId")
            set_combo_index_by_data(self.combo_GemList, self._skillId)

    def save(self, gem):
        """
        Save the UI elements into the xml element
        :return: N/A
        """
        if gem is not None:
            self._level = self.spin_GemLevel.value()
            gem.set("level", self._level)
            self._quality = self.spin_GemQuality.value()
            gem.set("quality", self._quality)
            self._count = self.spin_GemCount.value()
            gem.set("count", self._count)

            self._enabled = self.check_GemEnabled.checkState()
            gem.set("enabled", self._enabled)

            set_combo_index_by_data(self.combo_GemVariant, self._qualityId)
            self._qualityId = gem.get("qualityId")
            set_combo_index_by_data(self.combo_GemList, self._skillId)
            self._skillId = gem.get("skillId")

    def fill_gem_list(self, gem_list):
        """
        File the gem list combo
        :param gem_list:
        :return:
        """
        for g in gem_list:
            self.combo_GemList.addItem(gem_list[g]["base_item"]["display_name"], g)
        # set the ComboBox dropdown width.
        self.combo_GemList.view().setMinimumWidth(
            self.combo_GemList.minimumSizeHint().width()
        )
        # Sort Alphabetically
        self.combo_GemList.model().sort(0)
        self.combo_GemList.setCurrentIndex(-1)


# property index
# this will allow it to move it's y position, so when one is deleted from in the middle or a reorder command is given
# when can just change the index and have it magically move
