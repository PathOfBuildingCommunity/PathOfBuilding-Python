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
        self.gems = read_json(Path(self.pob_config.exeDir, "Data/gems.json"))

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

    # {label = "Default", type = "Default"},
    # {label = "Anomalous", type = "Alternate1"},
    # {label = "Divergent", type = "Alternate2"},
    # {label = "Phantasmal", type = "Alternate3"},

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _build):
        """
        Load internal structures from the build object
        :param _build: Reference to the xml tree
        :return: N/A
        """
        self.skills = _build.find("Skills")
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
        active_set = int(self.skills.get("activeSkillSet", 1))  # This will need a -1

        for _set in self.skills.iter("SkillSet"):
            self.skill_sets.append(_set)
        self.load_skill_set(self.skill_sets[active_set])

        # for idx, _set in enumerate(self.skills.get("SkillSet")):
        # for _set in self.skills["SkillSet"]:
        # for _set in self.skills:
        #     print("_set", _set)
        # self.skill_sets.append(_set)
        # for skill_group in _set["Skill"]:
        #     print("skill_group", skill_group)

    def load_skill_set(self, _set):
        """

        :param _set:
        :return:
        """
        # unload the previous set, saving it's state
        if self.current_skill_set is not None:
            pass  #unload the previous set, saving it's state

        pass

    def save(self):
        """
        Save internal structures back to the build object
        """
        return self.skills


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
