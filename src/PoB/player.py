"""A Player represents an in-game character at a specific progression point.

A unique Player is defined by: level, class selection, ascendancy selection,
skill selection, and itemization across the item sets.
"""

import xml.etree.ElementTree as ET

from PoB.constants import PlayerClasses, PlayerAscendancy, player_stats_list
from PoB.build import Build
from widgets.ui_utils import html_colour_text

# 2 base accuracy per level.
# 50 life and gains additional 12 life per level.
# 40 mana and gains additional 6 mana per level.
# 15 evasion rating.
# Every 10 Strength grants
# An additional 5 maximum life
# 2% increased melee physical damage
#
# Every 10 Dexterity grants
# An additional 20 accuracy rating
# 2% increased evasion rating
#
# Every 10 Intelligence grants
# An additional 5 maximum mana
# 2% increased maximum energy shield

class_stats = {
    PlayerClasses.SCION: {"str": 20, "dex": 20, "int": 20},
    PlayerClasses.MARAUDER: {"str": 32, "dex": 14, "int": 14},
    PlayerClasses.RANGER: {"str": 14, "dex": 32, "int": 14},
    PlayerClasses.WITCH: {"str": 14, "dex": 14, "int": 32},
    PlayerClasses.DUELIST: {"str": 23, "dex": 23, "int": 14},
    PlayerClasses.TEMPLAR: {"str": 23, "dex": 14, "int": 23},
    PlayerClasses.SHADOW: {"str": 14, "dex": 23, "int": 23},
}


class Player:
    def __init__(self, settings, build) -> None:
        self.build = build
        self.settings = settings
        self.player_class = build.current_class
        # self.ascendancy = build.ascendancy
        self.level = build.level
        # dictionary lists of the stat elements
        self.stats = {}
        # self.skills = []
        # self.item_sets = set()
        # self.minions = set()
        # self.tree = None

    def __repr__(self) -> str:
        return f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n" if self.ascendancy.value is not None else "\n"

    def load(self, _build):
        """
        Load internal structures from the build object

        :param _build: build xml
        :return: N/A
        """
        self.build = _build
        for stat in self.build.findall("PlayerStat"):
            stat_name = stat.get("stat")
            print(f"player.load {stat_name}")
            try:
                # Sometimes there is an entry like '<PlayerStat stat="SkillDPS" value="table: 0x209a50f0" />'
                stat_value = float(stat.get("value"))
                self.stats[stat_name] = stat_value
            except ValueError:
                print(f"Error in {stat_name}. Value was '{stat.get('value', 'Error Value')}'")
                self.build.remove(stat)
                continue
        print(f"player.load {len(self.stats)}")

    def save(self, _build):
        """
        Save internal structures back to the build object

        :param _build: build xml
        :return: N/A
        """
        # Remove everything and then add ours
        for stat in self.build.findall("PlayerStat"):
            self.build.remove(stat)
        for name in self.stats:
            self.build.append(ET.fromstring(f'<PlayerStat stat="{name}" value="{self.stats[name]}" />'))

    def calc_stats(self):
        # Calculate Stats (eventually we want to pass in a new set of items, new item, new tree, etc to compare against.
        print("Calc_Stats")
        # self.stats["ChaosResistOverCap"] = 99.60
        # self.stats["AverageDamage"] = 99.50


def test() -> None:
    player = Player()
    print(player)


if __name__ == "__main__":
    test()
