"""
This Class if communicating between the calculation Classes and the UI Classes
"""

from operator import itemgetter

from PoB_Main_Window import Ui_MainWindow
from pob_config import *
from constants import stats_list


class PlayerStats:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.config = _config
        self.win = _win

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
        for stat in build.findall("PlayerStat"):
            _stat = stat.get("stat")
            _value = float(stat.get("value"))
            self.stats[_stat] = stat
            # print("_stat", _stat, _value)
            if _value != 0:
                try:
                    # Return a dictionary of our stats or a list of dictionaries if there are multiples
                    # There are entries in the build that are not in our stats_list table, so the list will return empty
                    stat_dict = [d for d in stats_list if d.get("stat") == _stat]
                    if stat_dict:
                        if type(stat_dict) is list:
                            # ToDo: Need to use the flag attribute to separate
                            stat_dict = stat_dict[0]
                        _label = stat_dict.get("label", "")
                        _label = "{0:>24}".format(_label)
                        _colour = stat_dict.get("colour", ColourCodes.NORMAL)
                        _fmt = stat_dict.get("fmt")
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
                    # There are entries in the build that are not in our stats_list table
                    pass

    def save(self, build):
        """
        Save internal structures back to the build object
        """
        # There is no need to do anything as we update the stat element directly
        pass

    def update_stat(self, stat_name, value):
        """
        Update a stat element witht he supplied value
        :param stat_name: String: Teh string index into the stats dictionary
        :param value: The value
        :return: N/A
        """
        stat = self.stats[stat_name]
        if stat is not None:
            stat.set(stat_name, f"{value}")


# def test() -> None:
#     stats_ui = PlayerStats()
#     print(stats_ui)
#
#
# if __name__ == "__main__":
#     test()
