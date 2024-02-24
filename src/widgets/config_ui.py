"""
This Class manages all the elements and owns some elements of the "CONFIG" tab
"""

from PySide6.QtWidgets import QGridLayout

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
        # General
        set_combo_index_by_data(self.win.combo_ResPenalty, self.build.resistancePenalty)
        set_combo_index_by_data(self.win.combo_Bandits, self.build.bandit)
        set_combo_index_by_data(self.win.combo_MajorPantheon, self.build.pantheonMajorGod)
        set_combo_index_by_data(self.win.combo_MinorPantheon, self.build.pantheonMinorGod)
        set_combo_index_by_data(self.win.combo_igniteMode, self.build.get_config_tag_item("Input", "igniteMode", "AVERAGE"))
        set_combo_index_by_data(self.win.combo_EHPUnluckyWorstOf, self.build.get_config_tag_item("Input", "EHPUnluckyWorstOf", 1))

        # Combat
        self.win.check_PowerCharges.setChecked(self.build.get_config_tag_item("Input", "usePowerCharges", False))
        self.win.spin_NumPowerCharges.setValue(self.build.get_config_tag_item("Input", "overridePowerCharges", 3))
        self.win.check_FrenzyCharges.setChecked(self.build.get_config_tag_item("Input", "useFrenzyCharges", False))
        self.win.spin_NumFrenzyCharges.setValue(self.build.get_config_tag_item("Input", "overrideFrenzyCharges", 3))
        self.win.check_EnduranceCharges.setChecked(self.build.get_config_tag_item("Input", "useEnduranceCharges", False))
        self.win.spin_NumEnduranceCharges.setValue(self.build.get_config_tag_item("Input", "overrideEnduranceCharges", 3))
        self.win.check_SiphoningCharges.setChecked(self.build.get_config_tag_item("Input", "useSiphoningCharges", False))
        self.win.spin_NumSiphoningCharges.setValue(self.build.get_config_tag_item("Input", "overrideSiphoningCharges", 3))
        self.win.check_ChallengerCharges.setChecked(self.build.get_config_tag_item("Input", "useChallengerCharges", False))
        self.win.spin_NumChallengerCharges.setValue(self.build.get_config_tag_item("Input", "overrideChallengerCharges", 3))
        self.win.check_BlitzCharges.setChecked(self.build.get_config_tag_item("Input", "useBlitzCharges", False))
        self.win.spin_NumBlitzCharges.setValue(self.build.get_config_tag_item("Input", "overrideBlitzCharges", 3))
        # self.win.check_multiplierGaleForce.setChecked(self.build.get_config_tag_item("Input", "multiplierGaleForce", False))
        # self.win.spin_NumInspirationCharges.setValue(self.build.get_config_tag_item("Input", "overrideInspirationCharges", 3))
        self.win.check_GhostCharges.setChecked(self.build.get_config_tag_item("Input", "useGhostCharges", False))
        self.win.spin_NumGhostCharges.setValue(self.build.get_config_tag_item("Input", "overrideGhostCharges", 3))
        # waitForMaxSeals

    def save(self):
        """
        Save internal structures back to the build object
        """
        # General
        self.build.resistancePenalty = self.win.combo_ResPenalty.currentData()
        self.build.bandit = self.win.combo_Bandits.currentData()
        self.build.pantheonMajorGod = self.win.combo_MajorPantheon.currentData()
        self.build.pantheonMinorGod = self.win.combo_MinorPantheon.currentData()
        self.build.set_config_tag_item("Input", "igniteMode", self.win.combo_igniteMode.currentData())
        self.build.set_config_tag_item("Input", "EHPUnluckyWorstOf", self.win.combo_EHPUnluckyWorstOf.currentData())
        # ignoreJewelLimits

        # Combat
        self.build.set_config_tag_item("Input", "usePowerCharges", self.win.check_PowerCharges.isChecked())
        self.build.set_config_tag_item("Input", "overridePowerCharges", self.win.spin_NumPowerCharges.value())
        self.build.set_config_tag_item("Input", "useFrenzyCharges", self.win.check_FrenzyCharges.isChecked())
        self.build.set_config_tag_item("Input", "overrideFrenzyCharges", self.win.spin_NumFrenzyCharges.value())
        self.build.set_config_tag_item("Input", "useEnduranceCharges", self.win.check_EnduranceCharges.isChecked())
        self.build.set_config_tag_item("Input", "overrideEnduranceCharges", self.win.spin_NumEnduranceCharges.value())
        if self.win.check_SiphoningCharges.isVisible():  # from Disintegrator
            self.build.set_config_tag_item("Input", "useSiphoningCharges", self.win.check_SiphoningCharges.isChecked())
            self.build.set_config_tag_item("Input", "overrideSiphoningCharges", self.win.spin_NumSiphoningCharges.isChecked())
        if self.win.check_ChallengerCharges.isVisible():
            self.build.set_config_tag_item("Input", "useChallengerCharges", self.win.check_ChallengerCharges.isChecked())
            self.build.set_config_tag_item("Input", "overrideChallengerCharges", self.win.spin_NumChallengerCharges.isChecked())
        if self.win.check_BlitzCharges.isVisible():
            self.build.set_config_tag_item("Input", "useBlitzCharges", self.win.check_BlitzCharges.isChecked())
            self.build.set_config_tag_item("Input", "overrideBlitzCharges", self.win.spin_NumBlitzCharges.isChecked())
        # self.build.set_config_tag_item("Input", "multiplierGaleForce", self.win.check_multiplierGaleForce.isChecked())
        # self.build.set_config_tag_item("Input", "overrideInspirationCharges", self.win.spin_NumInspirationCharges.isChecked())
        if self.win.check_GhostCharges.isVisible():
            self.build.set_config_tag_item("Input", "useGhostCharges", self.win.check_GhostCharges.isChecked())
            self.build.set_config_tag_item("Input", "overrideGhostCharges", self.win.spin_NumGhostCharges.isChecked())
        # waitForMaxSeals

    def initial_startup_setup(self):
        """Configure configuration tab widgets on startup"""
        self.win.label_NumPowerCharges.setVisible(False)
        self.win.spin_NumPowerCharges.setVisible(False)
        self.win.label_NumFrenzyCharges.setVisible(False)
        self.win.spin_NumFrenzyCharges.setVisible(False)
        self.win.label_NumEnduranceCharges.setVisible(False)
        self.win.spin_NumEnduranceCharges.setVisible(False)
        self.win.label_SiphoningCharges.setVisible(False)
        self.win.check_SiphoningCharges.setVisible(False)
        self.win.label_NumSiphoningCharges.setVisible(False)
        self.win.spin_NumSiphoningCharges.setVisible(False)
        self.win.label_ChallengerCharges.setVisible(False)
        self.win.check_ChallengerCharges.setVisible(False)
        self.win.label_NumChallengerCharges.setVisible(False)
        self.win.spin_NumChallengerCharges.setVisible(False)
        self.win.label_BlitzCharges.setVisible(False)
        self.win.check_BlitzCharges.setVisible(False)
        self.win.label_NumBlitzCharges.setVisible(False)
        self.win.spin_NumBlitzCharges.setVisible(False)
        self.win.label_GhostCharges.setVisible(False)
        self.win.check_GhostCharges.setVisible(False)
        self.win.label_NumGhostCharges.setVisible(False)
        self.win.spin_NumGhostCharges.setVisible(False)

        # ToDo: find things that need doing on other layouts that might get destroyed/recreated
        # Programatically set values on this layout as it will be destroyed and recreated in the Designer a lot
        general_layout: QGridLayout = self.win.label_ResPenalty.parent().layout()
        general_layout.setColumnMinimumWidth(0, 100)
        general_layout.setContentsMargins(0, 9, 3, 3)
        combat_layout: QGridLayout = self.win.label_PowerCharges.parent().layout()
        combat_layout.setColumnMinimumWidth(1, 50)
        combat_layout.setContentsMargins(0, 9, 3, 3)


# def test() -> None:
#     config_ui = ConfigUI()
#     print(config_ui)


# if __name__ == "__main__":
#     test()
