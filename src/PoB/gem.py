"""
A class to encapsulate one gem/skill
"""

import xml.etree.ElementTree as ET
import math
import re

from PoB.constants import bad_text, pob_debug, ColourCodes, empty_gem
from PoB.settings import Settings
from PoB.mod import Mod
from widgets.ui_utils import (
    _debug,
    html_colour_text,
    index_exists,
    str_to_bool,
    bool_to_str,
    print_a_xml_element,
    search_stats_list_for_regex,
)

colours = (
    ColourCodes.NORMAL.value,
    ColourCodes.STRENGTH.value,
    ColourCodes.DEXTERITY.value,
    ColourCodes.INTELLIGENCE.value,
    ColourCodes.WHITE.value,
)


class Gem:
    def __init__(self, _settings: Settings) -> None:
        """
        Initialise defaults
        :param _settings: A pointer to the settings
        :param _base_items: dict: the loaded base_items.json
        :param _slot: where this item is worn/carried.
        """
        self.settings = _settings
        # This gem's entry from gems.json
        self.base_gem = None
        self.name = ""
        self._type = ""  # or item_class - eg weapon
        self.sub_type = ""  # or item_class - eg claw
        self.active = False  # is this the item that is currently chosen/shown in the dropdown ?

        self.xml_gem = ET.fromstring(empty_gem)

        # this is not always available from the json character download
        self.level_req = 0

        self.id = 0
        self.rarity = "NORMAL"
        self._level = 1
        self.enabled = True
        self.quality = self.settings.default_gem_quality
        self.count = 1
        self.name = ""
        self.support = False
        self.qualityVariant = "Default"
        self.minion = False
        self.skillMinionSkillCalcs = 0
        self.skillMinionCalcs = ""
        self.skillMinionSkill = 0
        self.skillMinion = ""

        self.colour = ""  # ColourCodes value
        self.coloured_name = ""  # html formatted name
        self.levels = [{}]  # List of dict.
        self.max_reqDex = 0  # value from the json
        self.max_reqInt = 0  # value from the json
        self.max_reqStr = 0  # value from the json
        self.reqDex = 0
        self.reqInt = 0
        self.reqStr = 0
        self.naturalMaxLevel = 20

        # needs to be a string as there are entries like "Limited to: 1 Survival"
        self.limited_to = ""
        self._quality = 0
        self.unique_id = ""
        self.requires = {}
        self.influences = []
        self._armour = 0
        self.base_armour = 0  # value without quality and +nn additions/multipliers
        self._evasion = 0
        self.evasion_base_percentile = 0.0
        self.base_evasion = 0  # value without quality and +nn additions/multipliers
        self._energy_shield = 0
        self.energy_shield_base_percentile = 0.0
        self.base_energy_shield = 0  # value without quality and +nn additions/multipliers
        self.armour_base_percentile = 0.0

    def load_from_ggg_json(self, json_gem, gems_by_name_or_id):
        """
        Load gem from GGG. This should be called after load_from_gems_json so it can load the defaults.
        :param json_gem: This gem from the imported json.
        :param gems_by_name_or_id: list of gems from gems.json.
        :return: gem's xml
        """

        def get_property(_json_gem, _name, _default):
            """
            Get a property from a list of property tags. Not all properties appear mandatory.

            :param _json_gem: the gem reference from the json download
            :param _name: the name of the property
            :param _default: a default value to be used if the property is not listed
            :return:
            """
            for _prop in _json_gem.get("properties"):
                if _prop.get("name") == _name:
                    value = _prop.get("values")[0][0].replace(" (Max)", "").replace("+", "").replace("%", "")
                    return value
            return _default

        self.xml_gem.set("level", get_property(json_gem, "Level", "1"))
        self.xml_gem.set("quality", get_property(json_gem, "Quality", "0"))

        match json_gem["typeLine"]:
            case "Anomalous":
                self.xml_gem.set("qualityId", "Alternate1")
            case "Divergent":
                self.xml_gem.set("qualityId", "Alternate2")
            case "Phantasmal":
                self.xml_gem.set("qualityId", "Alternate3")

        return self.xml_gem

    def load_from_gems_json(self, json_gem):
        """

        :param json_gem:
        :return: xml verion of the gem
        """
        self.name = json_gem["grantedEffect"]["name"]
        self.support = json_gem.get("support", False)
        self.colour = colours[json_gem.get("colour", 0)]
        self.coloured_name = html_colour_text(self.colour, self.name)
        self.levels.append(json_gem["grantedEffect"]["levels"])
        self.max_reqDex = json_gem.get("reqDex", 0)
        self.max_reqInt = json_gem.get("reqInt", 0)
        self.max_reqStr = json_gem.get("reqStr", 0)
        self.naturalMaxLevel = json_gem.get("naturalMaxLevel", 20)

        self.xml_gem.set("gemId", json_gem.get("id", ""))
        self.xml_gem.set("skillId", json_gem["grantedEffectId"])

        return self.xml_gem

    def load(self, xml_gem):
        """
        Load gem from build.xml. This should be called after load_from_gems_json so it can load the defaults.
        :param: xml_gem
        :return: N/A
        """
        self.level = int(xml_gem.get("level"))
        self.enabled = str_to_bool(xml_gem.get("enabled"))
        self.quality = int(xml_gem.set("quality"))
        self.count = int(xml_gem.get("count"))
        self.qualityVariant = xml_gem.get("qualityId")
        if self.minion:
            self.skillMinionSkillCalcs = int(xml_gem.get("skillMinionSkillCalcs"))  # 1
            self.skillMinionCalcs = xml_gem.get("skillMinionCalcs")  # "GuardianRelicAll"
            self.skillMinionSkill = int(xml_gem.get("skillMinionSkill"))  # 1
            self.skillMinion = xml_gem.get("skillMinion")  # "GuardianRelicAll"

    def save(self):
        """Save"""
        self.xml_gem.set("level", f"{self.level}")
        self.xml_gem.set("enabled", f"{self.enabled}")
        self.xml_gem.set("quality", f"{self.quality}")
        self.xml_gem.set("count", f"{self.count}")
        self.xml_gem.set("nameSpec", self.name)
        self.xml_gem.set("qualityId", self.qualityVariant)
        if self.minion:
            self.xml_gem.set("skillMinionSkillCalcs", f"{self.skillMinionSkillCalcs}")  # 1
            self.xml_gem.set("skillMinionCalcs", self.skillMinionCalcs)  # "GuardianRelicAll"
            self.xml_gem.set("skillMinionSkill", f"{self.skillMinionSkill}")  # 1
            self.xml_gem.set("skillMinion", self.skillMinion)  # "GuardianRelicAll"

    def gem_stat_requirement(self, gem_level, required_stat):
        """
        -- From PyPoE's formula.py
        Calculates and returns the stat requirement for the specified level requirement.

        The calculations vary depending on the gem type (i.e. active or support gem) and on the multiplier.

        Currently only multipliers of 100, 60 and 40 are supported.
        :param gem_level: int: Level requirement for the current gem level
        :param required_stat: Stat multiplier, i.e. from SkillGems.dat (eg: reqStr = 100)
        :return: int: calculated stat requirement
        """
        if self.support:
            b = 6 * required_stat / 100
            match required_stat:
                case 100:
                    a = 1.495
                case 60:
                    a = 0.945  # 1.575 * 0.6
                case 40:
                    a = 0.6575  # 1.64375 * 0.6
                case _:
                    return 0
        else:
            b = 8 * required_stat / 100
            match required_stat:
                case 100:
                    a = 2.1
                    b = 7.75
                case 75:
                    a = 1.619
                case 60:
                    a = 1.325
                case 40:
                    a = 0.924
                case _:
                    return 0

        result = round(gem_level * a + b)
        # Gems seem to have no requirements lower then 14
        return 0 if result < 14 else result

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, new_level):
        """Set things like armour damage, required stats based on the level"""
        self._level = new_level
        if self.max_reqDex:
            self.reqDex = self.gem_stat_requirement(new_level, self.max_reqDex)
        if self.max_reqInt:
            self.reqInt = self.gem_stat_requirement(new_level, self.max_reqInt)
        if self.max_reqStr:
            self.reqStr = self.gem_stat_requirement(new_level, self.max_reqStr)
        stats = self.levels[new_level]
