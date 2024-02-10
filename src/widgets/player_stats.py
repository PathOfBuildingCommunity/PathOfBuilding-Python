"""
This Class is communicating between the calculation Classes and the UI Classes
"""

from PoB.settings import Settings
from PoB.constants import bad_text, player_stats_list, ColourCodes
from widgets.ui_utils import html_colour_text

from ui.PoB_Main_Window import Ui_MainWindow


class PlayerStats:
    def __init__(self, _settings: Settings, _win: Ui_MainWindow) -> None:
        self.settings = _settings
        self.win = _win
        self.build = None

        # dictionary lists of the stat elements
        self.stats = {}

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _build):
        """
        Load internal structures from the build object

        :param _build: build xml
        :return: N/A
        """
        self.build = _build
        self.win.textedit_Statistics.clear()
        for stat in self.build.findall("PlayerStat"):
            _stat = stat.get("stat")
            try:
                # Sometimes there is an entry like '<PlayerStat stat="SkillDPS" value="table: 0x209a50f0" />'
                _value = float(stat.get("value"))
            except ValueError:
                print(f"Error in {_stat}. Value was '{stat.get('value', 'Error Value')}'")
                self.build.remove(stat)
                break
            self.stats[_stat] = stat
            # print("_stat", _stat, _value)
            if _value != 0:
                try:
                    # Return a dictionary of our stats or a list of dictionaries if there are multiples
                    # There are entries in the build that are not in our player_stats_list table, so the list will return empty
                    stat_dict = [d for d in player_stats_list if d.get("stat") == _stat]
                    if stat_dict:
                        if type(stat_dict) is list:
                            # ToDo: Need to use the flag attribute to separate
                            stat_dict = stat_dict[0]
                        _label = stat_dict.get("label", "")
                        _label = "{0:>24}".format(_label)
                        _colour = stat_dict.get("colour", self.settings.qss_default_text)
                        _fmt = stat_dict.get("fmt")
                        # if fmt is an int, force the value to be an int.
                        if "d" in _fmt:
                            _value = int(_value)
                        if _value < 0:
                            _str_value = html_colour_text("NEGATIVE", _fmt.format(_value))
                        else:
                            _str_value = _fmt.format(_value)
                        # Cannot use html_colour_text() on this
                        # ToDo: Convert to <pre> like recent builds, and file Open/Save
                        self.win.textedit_Statistics.append(
                            f'<span style="white-space: pre; color:{_colour};">{_label}:</span> {_str_value}'
                        )
                except KeyError:
                    # There are entries in the build that are not in our player_stats_list table
                    pass

    def save(self, _build):
        """
        Save internal structures back to the build object

        :param _build: build xml
        :return: N/A
        """
        # There is no need to do anything as we update the stat element directly
        pass

    def update_stat(self, stat_name, value):
        """
        Update a stat element with the supplied value.

        :param stat_name: String: The string index into the stats dictionary
        :param value: The value
        :return: N/A
        """
        stat = self.stats[stat_name]
        if stat is not None:
            stat.set(stat_name, f"{value}")
        self.load(self.build)


# def test() -> None:
#     stats_ui = PlayerStats()
#     print(stats_ui)
#
#
# if __name__ == "__main__":
#     test()
