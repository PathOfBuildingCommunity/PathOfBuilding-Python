"""A Player represents an in-game character at a specific progression point.

A unique Player is defined by: level, class selection, ascendancy selection,
skill selection, and itemization across the item sets.
"""

import re
import xml.etree.ElementTree as ET

from PoB.constants import PlayerClasses, PlayerAscendancy, bad_text, player_stats_list
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
        self.xml_build = build.build
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
        self.json_player_class = None
        self.nodes = set()  # set of active Nodes()
        self.items = []
        self.itemstats = []

    def __repr__(self) -> str:
        return f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n" if self.ascendancy.value is not None else "\n"

    def load(self, _build):
        """
        Load stats from the build object, even ones we may not be able to deal with (except table entries).
        We keep valid entries that we may not yet support so that we don't destroy another tool's ability

        :param _build: build xml
        :return: N/A
        """
        self.xml_build = _build
        for stat in self.xml_build.findall("PlayerStat"):
            stat_name = stat.get("stat")
            try:
                # Sometimes there is an entry like '<PlayerStat stat="SkillDPS" value="table: 0x209a50f0" />'
                stat_value = float(stat.get("value"))
                self.stats[stat_name] = stat_value
            except ValueError:
                print(f"Error in {stat_name}. Value was '{stat.get('value', 'Error Value')}'")
                self.xml_build.remove(stat)
                continue

    def save(self, _build):
        """
        Save internal structures back to the build object

        :param _build: build xml
        :return: N/A
        """
        # Remove everything and then add ours
        for stat in self.xml_build.findall("PlayerStat"):
            self.xml_build.remove(stat)
        for name in self.stats:
            self.xml_build.append(ET.fromstring(f'<PlayerStat stat="{name}" value="{self.stats[name]}" />'))

    def calc_stats(self, items):
        """
        Calculate Stats (eventually we want to pass in a new set of items, new item, new tree, etc to compare against.
        Examples:
        #id: 55373 ['+12 to maximum Life', '+5 to Strength']
        #id: 49772 ['+40 to Strength', '8% increased Strength']
        #id: 3723 [ "6% increased maximum Life", "5% increased Strength" ]
        #id: 27929 ["+20 to maximum Energy Shield", "+20 to maximum Mana", "+20 to Intelligence"]
        #id: 23989 ["+15 to all Attributes", ...]
        :param: list: list() of Item() for items that are currently selected
        :return:
        """
        print("Calc_Stats")
        # self.stats["WithPoisonDPS"] = 123.70

        self.player_class = self.build.current_class
        self.json_player_class = self.build.current_tree.classes[self.player_class]
        self.items = items
        self.itemstats = []
        # self.build.current_spec.nodes.add(49772)
        # self.build.current_spec.nodes.add(3723)
        # self.build.current_spec.nodes.add(27929)
        # self.build.current_spec.nodes.add(23989)

        # Get all nodes that have stat values
        for node_id in self.build.current_spec.nodes:
            node = self.build.current_tree.nodes.get(node_id, None)
            # if node is not None and not node.isAscendancyStart and node.classStartIndex < 0 and node.stats:
            if node is not None and node.stats:
                # print(node_id, node.stats)
                self.nodes.add(node)

        # Get stats from all active items
        # print(self.items)
        for item in self.items:
            for mod in item.implicitMods:
                self.itemstats.append(mod.line_with_range)
            for mod in item.explicitMods:
                self.itemstats.append(mod.line_with_range)
        print(f"{len(self.itemstats)=}, {self.itemstats=}")

        self.calc_attribs()
        self.calc_life()
        self.calc_mana()
        self.calc_es()

    def search_nodes_stats_for_regex(self, stat_list, regex, default_value) -> int:
        """
        Standardise the regex searching of stats
        :param stat_list: list of stats that should match the regex.
        :param regex: the regex
        :param default_value: int: A value that suits the calculation if no stats found (1 for multiplication, 0 for addition)
        :return: int: the added value of the digits
        """
        value = 0
        for stat in stat_list:
            m = re.search(regex, stat)
            # print(f"{stat=}, {m=}")
            if m:
                value += int(m.group(1))
                # print(f"{value=}")
        return value == 0 and default_value or value

    def find_addition_to_stat(self, search_str, regex=r"^([-+]?\d+) to ", debug=False):
        """
        Find stats like '+1 to maximum Life' or '+1 to Summoned Totems'.
        Handles negatives too.
        :param search_str: Something like ' to Strength
        :param regex: str
        :param debug: bool: Ease of printing facts for a given specification
        :return: int: the value of all the addition stats found
        """
        results = []
        # find stats with additions
        for node in self.nodes:
            results += [n for n in node.stats if search_str in n]
            print(f"{node.id=}, {search_str=}, {results=}")
        value = self.search_nodes_stats_for_regex(results, regex, 0)
        if debug:
            print(f"find_addition_to_stat, {value=}, {search_str=}")
        return value

    def find_increases_to_stat(self, search_str, default_value, regex=r"^([-+]?\d+)% increased", debug=False):
        """
        Find stats like '8% increased Strength'.
        Does not handle Decreased, as there doesn't appear to many (any ?).
        :param search_str: Something like ' increased Strength'
        :param default_value: int: A value that suits the calculation if no stats found
        :param regex: str
        :param debug: bool: Ease of printing facts for a given specification
        :return: int: the value of all the addition stats found
        """
        results = []
        # find stats with increases
        for node in self.nodes:
            results += [n for n in node.stats if search_str in n]
            # print(f"{node.id=}, {search_str=}, {results=}")
        value = self.search_nodes_stats_for_regex(results, regex, default_value)
        if debug:
            print(f"find_increases_to_stat, {value=}, {search_str=}")
        return value

    # fmt: off
    def calc_attribs(self):
        """
        Calc. Str, Dex and Int.
        :return: N/A
        """
        all_attribs = self.find_addition_to_stat("to all Attributes")
        for attrib in ("Str", "Dex", "Int"):
            # attrib = "Str"
            add_results = []
            inc_results = []
            long_str = player_stats_list[attrib]["label"]

            # Setbase value from json
            value = self.json_player_class[f"base_{attrib.lower()}"]
            # find increases and additions
            value += self.find_addition_to_stat(f" to {long_str}") + all_attribs
            value *= self.find_increases_to_stat(f"increased {long_str}", 1)
            self.stats[attrib] = value
            # Find MaxReq
            required = 0
            for item in self.items:
                required = max(required, int(item.requires.get(attrib, "0")))
            self.stats[f"Req{attrib}"] = required

    # fmt: on

    def calc_life(self):
        """
        Calc. Life. Needs Str calculated first
        :return: N/A
        """
        # Setbase value.
        life = 50 + (12 * (self.build.level - 1))
        life += self.stats["Str"] / 2
        life += self.find_addition_to_stat(f" to maximum Life")
        self.stats["Spec:LifeInc"] = self.find_increases_to_stat(f"increased maximum Life", 100)
        life *= self.stats["Spec:LifeInc"] / 100
        self.stats["Life"] = life

    def calc_mana(self):
        """
        Calc. Mana. Needs Int calculated first
        :return: N/A
        """
        # Setbase value.
        mana = 40 + (6 * (self.build.level - 1))
        mana += self.stats["Int"] / 2
        mana += self.find_addition_to_stat(f" to maximum Mana")
        self.stats["Spec:ManaInc"] = self.find_increases_to_stat(f"increased maximum Mana", 100)
        mana *= self.stats["Spec:ManaInc"] / 100
        self.stats["Mana"] = mana

    def calc_es(self):
        """
        Calc. Energy Shield. Needs Int calculated first
        :return: N/A
        """
        # Setbase value.
        es = 0
        es += self.find_addition_to_stat(f" to maximum Energy Shield")
        self.stats["Spec:EnergyShieldInc"] = self.find_increases_to_stat(f"increased maximum Energy Shield", 100)
        es *= (self.stats["Int"] / 5) + (self.stats["Spec:EnergyShieldInc"] / 100)
        self.stats["EnergyShield"] = es

    def stat_conditions(self, stat_name, stat_value):
        """
        Check if this stat can be shown or maybe other reason.
        :param stat_name: str
        :param stat_value: int or float
        :return: bool:
        """
        match stat_name:
            case "Spec:LifeInc" | "Spec:ManaInc" | "Spec:EnergyShieldInc":
                return stat_value > 100
            case "ReqStr":
                return stat_value > self.stats["Str"]
            case "ReqDex":
                return stat_value > self.stats["Dex"]
            case "ReqInt":
                return stat_value > self.stats["Int"]
            case _:
                return True


def test() -> None:
    player = Player()
    print(player)


if __name__ == "__main__":
    test()
