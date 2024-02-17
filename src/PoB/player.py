"""A Player represents an in-game character at a specific progression point.

A unique Player is defined by: level, class selection, ascendancy selection,
skill selection, and itemization across the item sets.
"""

import math
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
        self.item_stats = []
        self.node_stats = []
        self.all_stats = []

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

    def calc_stats(self, active_items, test_item=None, test_node=None):
        """
        Calculate Stats (eventually we want to pass in a new set of items, new item, new tree, etc to compare against.
        Examples:
        #id: 55373 ['+12 to maximum Life', '+5 to Strength']
        #id: 49772 ['+40 to Strength', '8% increased Strength']
        #id: 3723 [ "6% increased maximum Life", "5% increased Strength" ]
        #id: 27929 ["+20 to maximum Energy Shield", "+20 to maximum Mana", "+20 to Intelligence"]
        #id: 23989 ["+15 to all Attributes", ...]
        :param: active_items: list() of Item() for items that are currently selected
        :param: test_item: Item() - future comparison
        :param: test_node: Node() - future comparison
        :return:
        """
        print("Calc_Stats")
        # self.stats["WithPoisonDPS"] = 123.70

        self.clear()
        self.player_class = self.build.current_class
        self.json_player_class = self.build.current_tree.classes[self.player_class]
        self.items = active_items
        # self.build.current_spec.nodes.add(49772)
        # self.build.current_spec.nodes.add(3723)
        # self.build.current_spec.nodes.add(27929)
        # self.build.current_spec.nodes.add(23989)

        # Get all nodes that have stat values
        for node_id in self.build.current_spec.nodes:
            node = self.build.current_tree.nodes.get(node_id, None)
            # print(node_id, node.name, node.stats)
            if node is not None and node.stats:
                # print(node_id, node.stats)
                self.nodes.add(node)
                for stat in node.stats:
                    self.node_stats.append(f"{stat}::{node.name} ({node_id})")

        for node_id in self.build.current_spec.masteryEffects:
            node = self.build.current_tree.nodes.get(node_id, None)
            if node:
                # print(node_id, node.stats)
                self.nodes.add(node)
                effect_id = self.build.current_spec.get_mastery_effect(node_id)
                # the output from the list comprehansion is a list (wow), so add [0] to get the dict
                effect = [effect for effect in node.masteryEffects if effect["effect"] == effect_id][0]
                self.node_stats.append(f"{effect['stats']}::{node.name} ({node_id})")
        # print(f"{len(self.node_stats)=}, {self.node_stats=}")

        # Get stats from all active items
        # print(self.items)
        for item in self.items:
            # print(item.name)
            for mod in item.get_active_mods():
                self.item_stats.append(f"{mod}::{item.name}")
            # for mod in item.implicitMods:
            #     self.item_stats.append(f"{mod.line_with_range}::{item.name}")
            # for mod in item.explicitMods:
            #     self.item_stats.append(f"{mod.line_with_range}::{item.name}")

        # print(f"{len(self.item_stats)=}, {self.item_stats=}")
        self.all_stats = self.node_stats + self.item_stats
        print(f"{len(self.all_stats)=}, {self.all_stats=}")

        self.calc_attribs()
        self.calc_life()
        self.calc_mana()
        self.calc_es(True)

    def search_stats_for_regex(self, stat_list, regex, default_value, debug=False) -> list:
        """
        Standardise the regex searching of stats
        :param stat_list: list of stats that should match the regex.
        :param regex: the regex.
        :param default_value: int: A value that suits the calculation if no stats found (1 for multiplication, 0 for addition).
        :param debug: bool: Ease of printing facts for a given specification.
        :return: list: the list of values of the digits. Some results need to be sum'd and others product'd.
        """
        value = []
        for stat in stat_list:
            m = re.search(regex, stat)
            # print(f"{stat=}, {regex=}")
            if m:
                # if debug:
                #     print(f"{stat=}, {regex=}, {value=}, {m=}")
                value.append(int(m.group(1)))
        return value == [] and [int(default_value)] or value

    def get_simple_stat(self, start_value, search_str, spec_str="", default_value=0, debug=False, multiple_returns=False):
        """
        Get a simple "+nn to 'stat'" or "nn% incresed 'stat'". See examples in 'calc_stat'.
        Can't do minion stats as they look similar to regular stats
              'Minions have 10% increased maximum Life' vs '8% increased maximum Life' (they can use search_stats_for_regex)
        :param start_value: int / float.
        :param search_str: EG: 'Life', 'Strength'
        :param spec_str: If set, sets the self.stats with the vlaue of increases from the tree.
        :param default_value: int / float: A value that suits the calculation if no stats found.
        :param debug: bool: Ease of printing facts for a given specification.
        :param multiple_returns: bool: Return the individual values.
        :return: int: The updated value.
        """
        # find increases and additions. Some objects have things like '+21 to Dexterity and Intelligence', so use .* in regex.
        adds = sum(self.search_stats_for_regex(self.all_stats, rf"(?!Minions)([-+]?\d+) to .*{search_str}", default_value, debug))
        value = start_value + adds
        if debug:
            print(f"get_simple_stat: {search_str}: {value=}, {start_value=}, {adds=}")

        node_multiples = sum(
            self.search_stats_for_regex(self.node_stats, rf"^(?!Minion)([-+]?\d+)% increased {search_str}", default_value, debug)
        )
        node_multiples -= sum(
            self.search_stats_for_regex(self.node_stats, rf"^(?!Minions)([-+]?\d+)% reduced {search_str}", default_value, debug)
        )
        if spec_str:
            self.stats[f"{spec_str}"] = node_multiples

        item_multiples = sum(
            self.search_stats_for_regex(self.item_stats, rf"^(?!Minions)([-+]?\d+)% increased {search_str}", default_value, debug)
        )
        item_multiples -= sum(
            self.search_stats_for_regex(self.item_stats, rf"^(?!Minions)([-+]?\d+)% reduced {search_str}", default_value, debug)
        )
        multiples = node_multiples + item_multiples
        value += multiples / 100 * value
        if debug:
            print(f"get_simple_stat: {value=}, {node_multiples=}, {item_multiples=}")

        more = math.prod(self.search_stats_for_regex(self.item_stats, rf"^(?!Minions)([-+]?\d+)% more {search_str}", 0, debug))
        more -= math.prod(self.search_stats_for_regex(self.item_stats, rf"^(?!Minions)([-+]?\d+)% less {search_str}", 0, debug))
        if debug:
            print(f"get_simple_stat: {value=}, {more=}, {((more  / 100 ) + 1 )=}")
        if more:
            value = ((more / 100) + 1) * int(value)
        if debug:
            print(f"get_simple_stat: {value=}")
            # print(f"get_simple_stat: total=, ", (start_value + adds) * (1 + node_multiples + item_multiples) * (1 + (more / 100)))
        # return value
        if multiple_returns:
            return adds, multiples, more
        else:
            return value

    def calc_attribs(self, debug=False):
        """
        Calc. Str, Dex and Int.
        :param debug: bool: Ease of printing facts for a given specification
        :return: N/A
        """
        all_attribs = sum(self.search_stats_for_regex(self.all_stats, "to all Attributes", 0))
        for attrib in ("Str", "Dex", "Int"):
            # attrib = "Str"
            long_str = player_stats_list[attrib]["label"]

            # Setbase value from json
            value = self.json_player_class[f"base_{attrib.lower()}"] + all_attribs
            if debug:
                print(f"{attrib=}, {value=}, {all_attribs=}")
            self.stats[attrib] = self.get_simple_stat(value, long_str, debug=debug)

            # Find MaxReq
            required = 0
            for item in self.items:
                required = max(required, int(item.requires.get(attrib, "0")))
            self.stats[f"Req{attrib}"] = required

    def calc_life(self, debug=False):
        """
        Calc. Life. Needs Str calculated first. https://www.poewiki.net/wiki/Life
        :param debug: bool: Ease of printing facts for a given specification
        :return: N/A
        """
        # Setbase value.
        life = 38 + (12 * self.build.level)
        if debug:
            print(f"calc_life: {life=}, {self.stats['Str']=}, ")
        life += self.stats["Str"] / 2
        if debug:
            print(f"calc_life: {life=}")
        self.stats["Life"] = int(self.get_simple_stat(life, "maximum Life", "Spec:LifeInc", debug=debug))
        # life += self.search_stats_for_regex(self.all_stats, r"([-+]?\d+) to .* maximum Life", 0, debug)
        # if debug:
        #     print(f"{life=}")
        # node_multiples = self.search_stats_for_regex(self.node_stats, r"([-+]?\d+)% increased maximum Life", 0, debug)
        # Currently there are no reduced Maximum's on the tree
        # # node_multiples -= self.stats["Spec:LifeInc"] = self.search_stats_for_regex(self.node_stats, "reduced maximum Life", 0, debug)
        # self.stats["Spec:LifeInc"] = node_multiples
        # item_multiples = self.search_stats_for_regex(self.item_stats, r"([-+]?\d+)% increased maximum Life", 0)
        # item_multiples -= self.search_stats_for_regex(self.item_stats, r"([-+]?\d+)% reduced maximum Life", 0)
        # life += ((node_multiples + item_multiples) / 100) * life
        # self.stats["Life"] = life

    def calc_mana(self, debug=False):
        """
        Calc. Mana. Needs Int calculated first. https://www.poewiki.net/wiki/Mana
        :param debug: bool: Ease of printing facts for a given specification
        :return: N/A
        """
        # Setbase value.
        mana = 34 + (6 * self.build.level)
        if debug:
            print(f"{mana=}")
        mana += self.stats["Int"] / 2
        if debug:
            print(f"{mana=}, {self.stats['Int'] / 2}")
        self.stats["Mana"] = self.get_simple_stat(mana, "maximum Mana", "Spec:ManaInc", debug=debug)
        # mana += self.find_addition_to_stat(self.node_stats + self.item_stats, f" to maximum Mana")
        # self.stats["Spec:ManaInc"] = self.find_increases_to_stat(self.node_stats, f"increased maximum Mana", 100)
        # item_mana = self.find_increases_to_stat(self.item_stats, f"increased maximum Mana", 0)
        # mana *= (self.stats["Spec:ManaInc"] + item_mana) / 100
        # mana += self.search_stats_for_regex(self.all_stats, r"([-+]?\d+) to .* maximum Mana", 0, debug)
        # if debug:
        #     print(f"{mana=}")
        # node_multiples = self.search_stats_for_regex(self.node_stats, r"([-+]?\d+)% increased maximum Mana", 100, debug)
        # Currently there are no reduced Maximum's on the tree
        # node_multiples -= self.stats["Spec:LifeInc"] = self.search_stats_for_regex(self.node_stats, "reduced maximum Mana", 0, debug)
        # self.stats["Spec:ManaInc"] = node_multiples
        # item_multiples = self.search_stats_for_regex(self.item_stats, r"([-+]?\d+)% increased maximum Mana", 0)
        # item_multiples -= self.search_stats_for_regex(self.item_stats, r"([-+]?\d+)% reduced maximum Mana", 0)
        # mana += ((node_multiples + item_multiples) / 100) * mana
        # if mana < 1:
        #     mana = 1
        # if debug:
        #     print(f"{mana=}, {node_multiples=}, {item_multiples=}")
        # self.stats["Mana"] = mana

    def calc_es(self, debug=False):
        """
        Calc. Energy Shield. Needs Int calculated first. https://www.poewiki.net/wiki/Energy_shield
        :param debug: bool: Ease of printing facts for a given specification
        :return: N/A
        """
        # Setbase value.
        es = 0
        for item in self.items:
            es += int(item.energy_shield)
        if debug:
            print(f"Energy Shield: from item attribs: {es=}")
        # We need to account for Int's max ES.
        adds, multiples, more = self.get_simple_stat(es, "maximum Energy Shield", "Spec:EnergyShieldInc", 0, debug, True)
        if debug:
            print(f"ES: {adds=}, {multiples=}, {more=}, {self.stats['Int']=}, {self.stats['Int'] / 5=}")

        # Every class starts with no energy shield, and gains 2% increased maximum energy shield every 10 intelligence.
        es = (es + adds) * (((multiples + int(self.stats["Int"] / 5)) / 100) + 1)
        if debug:
            print(f"ES: {es=}, {(((multiples + (self.stats['Int'] / 5)) / 100) + 1)=}")
        if more:
            es = ((more / 100) + 1) * int(es)
        self.stats["EnergyShield"] = es

    def clear(self):
        """Erase internal variables"""
        self.items.clear()
        self.nodes.clear()
        self.node_stats.clear()
        self.item_stats.clear()

    def stat_conditions(self, stat_name, stat_value):
        """
        Check if this stat can be shown.
        :param stat_name: str
        :param stat_value: int or float
        :return: bool:
        """
        match stat_name:
            case "ReqStr":
                return stat_value > self.stats["Str"]
            case "ReqDex":
                return stat_value > self.stats["Dex"]
            case "ReqInt":
                return stat_value > self.stats["Int"]
            case "Spec:ManaInc":
                return self.stats["Mana"] != 0
            case "Spec:EnergyShieldInc":
                return self.stats.get("EnergyShield", 0) != 0
            case _:
                return True

    # def find_addition_to_stat(self, search_list, search_str, regex=r"^([-+]?\d+) to ", debug=False):
    #     """
    #     Find stats like '+1 to maximum Life' or '+1 to Summoned Totems'.
    #     Handles negatives too.
    #     :param search_list: list: either nodes or items. Stats like "Spec:LifeInc" needs nodes only.
    #     :param search_str: Something like ' to Strength
    #     :param regex: str
    #     :param debug: bool: Ease of printing facts for a given specification
    #     :return: int: the value of all the addition stats found
    #     """
    #     results = []
    #     # find stats with additions
    #     results += [n for n in search_list if search_str in n]
    #     # regex = re.compile(_regex).search
    #     # results += [m.group(1) for stat in search_list for m in [regex(search_str)] if m]
    #     # results += [m.group(1) for l in lines for m in [regex.search(l)] if m]
    #     if debug:
    #         print(f"{search_str=}, {results=}")
    #     value = self.search_stats_for_regex(results, regex, 0)
    #     if debug:
    #         print(f"find_addition_to_stat, {value=}, {search_str=}")
    #     return value

    # def find_increases_to_stat(self, search_list, search_str, default_value, regex=r"^([-+]?\d+)% increased", debug=False):
    #     """
    #     Find stats like '8% increased Strength'.
    #     Does not handle Decreased, as there doesn't appear to many (any ?).
    #     :param search_list: list: either nodes or items. Stats like "Spec:LifeInc" needs nodes only.
    #     :param search_str: Something like ' increased Strength'
    #     :param default_value: int: A value that suits the calculation if no stats found
    #     :param regex: str
    #     :param debug: bool: Ease of printing facts for a given specification
    #     :return: int: the value of all the addition stats found
    #     """
    #     results = []
    #     # find stats with increases
    #     results += [n for n in search_list if search_str in n]
    #     if debug:
    #         print(f"{search_str=}, {results=}")
    #     value = self.search_stats_for_regex(results, regex, default_value)
    #     if debug:
    #         print(f"find_increases_to_stat, {value=}, {search_str=}")
    #     return value

    # def search_stat(self, search_list, regex, default_value, debug=False):
    #     """
    #
    #     :param search_list:
    #     :param regex:
    #     :param default_value:
    #     :param debug:
    #     :return:
    #     """
    #     adds = self.search_stats_for_regex(self.all_stats, regex, 0, debug=True)
    #     multiples = self.search_stats_for_regex(search_list, regex, 1, debug=True)
    #     multiples -= self.search_stats_for_regex(search_list, regex, 0, debug=True)
    #     return adds, multiples


def test() -> None:
    player = Player()
    print(player)


if __name__ == "__main__":
    test()
