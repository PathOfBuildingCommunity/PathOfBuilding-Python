"""
This Class manages all the elements and owns some elements of the "CONFIG" tab
"""

from PoB.settings import Settings
from PoB.build import Build
from widgets.ui_utils import set_combo_index_by_data

from ui.PoB_Main_Window import Ui_MainWindow


class ConfigUI:
    def __init__(self, _settings: Settings, _build: Build, _win: Ui_MainWindow) -> None:
        """
        Config UI
        :param _build: A pointer to the currently loaded build
        :param _settings: A pointer to the settings
        :param _win: A pointer to MainWindowUI
        """
        self.settings = _settings
        self.win = _win
        self.build = _build

    def load(self, _config):
        """
        Load internal structures from the build object
        :param _config: Reference to the xml <Config> tag set
        """
        set_combo_index_by_data(self.win.combo_ResPenalty, self.build.resistancePenalty)
        set_combo_index_by_data(self.win.combo_Bandits, self.build.bandit)
        set_combo_index_by_data(self.win.combo_MajorPantheon, self.build.pantheonMajorGod)
        set_combo_index_by_data(self.win.combo_MinorPantheon, self.build.pantheonMinorGod)
        # set_combo_index_by_data(self.win.combo_EHPUnluckyWorstOf, self.build.EHPUnluckyWorstOf)
        # set_combo_index_by_data(self.win.combo_igniteMode, self.build.igniteMode)

    def save(self):
        """
        Save internal structures back to the build object
        """
        self.build.resistancePenalty = self.win.combo_ResPenalty.currentData()
        self.build.bandit = self.win.combo_Bandits.currentData()
        self.build.pantheonMajorGod = self.win.combo_MajorPantheon.currentData()
        self.build.pantheonMinorGod = self.win.combo_MinorPantheon.currentData()
        # self.build.EHPUnluckyWorstOf = self.win.combo_EHPUnluckyWorstOf.currentData()
        # self.build.igniteMode = self.win.combo_igniteMode.currentData()


# def test() -> None:
#     config_ui = ConfigUI()
#     print(config_ui)


# if __name__ == "__main__":
#     test()
