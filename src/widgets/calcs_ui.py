"""
This Class manages all the elements and owns some elements of the "CALCS" tab
"""

from ui.PoB_Main_Window import Ui_MainWindow
from pob_config import Config
from constants import _VERSION


class CalcsUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
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
