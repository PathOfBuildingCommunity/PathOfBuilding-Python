"""
This Class manages all the elements and owns some elements of the "CALCS" tab
"""

from PoB.settings import Settings
from PoB.build import Build

from ui.PoB_Main_Window import Ui_MainWindow


class CalcsUI:
    def __init__(self, _settings: Settings, _build: Build, _win: Ui_MainWindow) -> None:
        """
        Config UI
        :param _settings: A pointer to the settings
        :param _build: A pointer to the currently loaded build
        :param _win: A pointer to MainWindowUI
        """
        self.settings = _settings
        self.win = _win

    def __repr__(self) -> str:
        return (
            f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
            if self.ascendancy.value is not None
            else "\n"
        )

    def load(self):
        """
        Load internal structures from the build object
        """
        pass

    def save(self):
        """
        Save internal structures back to the build object
        """
        pass


# def test() -> None:
#     calcs_ui = CalcsUI()
#     print(calcs_ui)


if __name__ == "__main__":
    test()
