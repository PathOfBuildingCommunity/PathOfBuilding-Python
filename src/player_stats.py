"""
This Class if communicating between the calculation Classes and the UI Classes
"""

from PoB_Main_Window import Ui_MainWindow
from pob_config import *
from constants import stats_list


class PlayerStats:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.config = _config
        self.win = _win
        self.build = self.win.build
        self.build_root = self.build.root

        # dictionary lists of the stat elements
        self.stats = {}

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, build):
        """
        Load internal structures from the build object
        """
        # create a dictionary of stats. Still needed ?
        self.win.textedit_Statistics.clear()
        for stat in self.build.root.findall("PlayerStat"):
            _stat = stat.get("stat")
            _value = float(stat.get("value"))
            # stat.set("value", 10)
            self.stats[_stat] = stat
            if _value != 0:
                try:
                    _label = stats_list[_stat].get("label", "")
                    _label = "{0:>24}".format(_label)
                    _colour = stats_list[_stat].get("colour", ColourCodes.NORMAL)
                    _fmt = stats_list[_stat].get("fmt")
                    # if fmt is an int, force the value to be an int.
                    if "d" in _fmt:
                        _value = int(_value)
                    if _value < 0:
                        _str_value = f'<span style="color:{ColourCodes.NEGATIVE.value};">{_fmt.format(_value)}</span>'
                    else:
                        _str_value = _fmt.format(_value)
                    self.win.textedit_Statistics.append(
                        f'<span style="white-space: pre; color:{_colour.value};">{_label}:</span> {_str_value}'
                    )
                except KeyError:
                    pass

    def save(self):
        """
        Save internal structures back to the build object
        """
        #clear()
        #then readd each element -> ET.Element("PlayerStat")
        pass


# def test() -> None:
#     stats_ui = PlayerStats()
#     print(stats_ui)
#
#
# if __name__ == "__main__":
#     test()
