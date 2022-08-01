"""
Configuration Class

Defines reading and writing the settings xml as well as the settings therein
The variables that come from the lua version of Path of Building retain their current naming
As the settings.xml can be altered by humans, care must be taken to ensure data integrity, where possible

Global constants as found in all locations in the lua version

This is a base PoB class. It doesn't import any other PoB ui classes
Imports pob_file
"""

import re
from pathlib import Path
from collections import OrderedDict
from enum import Enum, IntEnum

from qdarktheme.qtpy.QtCore import QSize

import pob_file

program_title = "Path of Building"

"""global_scale_factor
this is used to divide all x and y data coming in from the tree.json, but not Height and Width.
without this, items are too far apart and items are far too small on screen.
All values should only be scaled on point of entry, ie: when they are first processed out of the json
"""
global_scale_factor = 2

_VERSION = 3.18

# Default config incase the settings file doesn't exist
default_config = {
    "PathOfBuilding": {
        "Misc": {
            "theme": "Dark",
            "slotOnlyTooltips": "true",
            "showTitlebarName": "true",
            "showWarnings": "true",
            "defaultCharLevel": "1",
            "nodePowerTheme": "RED/BLUE",
            "connectionProtocol": "nil",
            "thousandsSeparator": ",",
            "betaTest": "false",
            "decimalSeparator": ".",
            "defaultGemQuality": "0",
            "showThousandsSeparators": "true",
            "buildSortMode": "NAME",
            "numRecentBuilds": "5",
        },
        "recentBuilds": {
            "r0": "",
            "r1": "",
            "r2": "",
            "r3": "",
            "r4": "",
        },
    }
}

empty_build = {
    "PathOfBuilding": {
        "Build": {
            "@level": 1,
            "@targetVersion": "3_0",
            "@pantheonMajorGod": "None",
            "@bandit": "None",
            "@className": "Scion",
            "@ascendClassName": "None",
            "@mainSocketGroup": 1,
            "@viewMode": "TREE",
            "@pantheonMinorGod": "None",
            "PlayerStat": [
                {"@stat": "AverageHit", "@value": ""},
                {"@stat": "Speed", "@value": ""},
                {"@stat": "HitSpeed", "@value": ""},
                {"@stat": "PreEffectiveCritChance", "@value": ""},
                {"@stat": "CritChance", "@value": ""},
                {"@stat": "CritMultiplier", "@value": ""},
                {"@stat": "TotalDPS", "@value": ""},
                {"@stat": "TotalDot", "@value": ""},
                {"@stat": "WithBleedDPS", "@value": ""},
                {"@stat": "WithIgniteDPS", "@value": ""},
                {"@stat": "WithPoisonDPS", "@value": ""},
                {"@stat": "TotalDotDPS", "@value": ""},
                {"@stat": "CullingDPS", "@value": ""},
                {"@stat": "CombinedDPS", "@value": ""},
                {"@stat": "Cooldown", "@value": ""},
                {"@stat": "AreaOfEffectRadius", "@value": ""},
                {"@stat": "ManaCost", "@value": ""},
                {"@stat": "LifeCost", "@value": ""},
                {"@stat": "ESCost", "@value": ""},
                {"@stat": "RageCost", "@value": ""},
                {"@stat": "ManaPercentCost", "@value": ""},
                {"@stat": "LifePercentCost", "@value": ""},
                {"@stat": "ManaPerSecondCost", "@value": ""},
                {"@stat": "LifePerSecondCost", "@value": ""},
                {"@stat": "ManaPercentPerSecondCost", "@value": ""},
                {"@stat": "LifePercentPerSecondCost", "@value": ""},
                {"@stat": "ESPerSecondCost", "@value": ""},
                {"@stat": "ESPercentPerSecondCost", "@value": ""},
                {"@stat": "Str", "@value": ""},
                {"@stat": "Dex", "@value": ""},
                {"@stat": "Int", "@value": ""},
                {"@stat": "Omni", "@value": ""},
                {"@stat": "ReqOmni", "@value": ""},
                {"@stat": "Devotion", "@value": ""},
                {"@stat": "TotalEHP", "@value": ""},
                {"@stat": "SecondMinimalMaximumHitTaken", "@value": ""},
                {"@stat": "Life", "@value": ""},
                {"@stat": "Spec:LifeInc", "@value": ""},
                {"@stat": "LifeUnreserved", "@value": ""},
                {"@stat": "LifeUnreservedPercent", "@value": ""},
                {"@stat": "LifeRegen", "@value": ""},
                {"@stat": "LifeLeechGainRate", "@value": ""},
                {"@stat": "Mana", "@value": ""},
                {"@stat": "Spec:ManaInc", "@value": ""},
                {"@stat": "ManaUnreserved", "@value": ""},
                {"@stat": "ManaUnreservedPercent", "@value": ""},
                {"@stat": "ManaRegen", "@value": ""},
                {"@stat": "ManaLeechGainRate", "@value": ""},
                {"@stat": "Ward", "@value": ""},
                {"@stat": "EnergyShield", "@value": ""},
                {"@stat": "Spec:EnergyShieldInc", "@value": ""},
                {"@stat": "EnergyShieldRegen", "@value": ""},
                {"@stat": "EnergyShieldLeechGainRate", "@value": ""},
                {"@stat": "Evasion", "@value": ""},
                {"@stat": "Spec:EvasionInc", "@value": ""},
                {"@stat": "MeleeEvadeChance", "@value": ""},
                {"@stat": "ProjectileEvadeChance", "@value": ""},
                {"@stat": "Armour", "@value": ""},
                {"@stat": "Spec:ArmourInc", "@value": ""},
                {"@stat": "PhysicalDamageReduction", "@value": ""},
                {"@stat": "EffectiveMovementSpeedMod", "@value": ""},
                {"@stat": "BlockChance", "@value": ""},
                {"@stat": "SpellBlockChance", "@value": ""},
                {"@stat": "AttackDodgeChance", "@value": ""},
                {"@stat": "SpellDodgeChance", "@value": ""},
                {"@stat": "SpellSuppressionChance", "@value": ""},
                {"@stat": "FireResist", "@value": ""},
                {"@stat": "FireResistOverCap", "@value": ""},
                {"@stat": "ColdResist", "@value": ""},
                {"@stat": "ColdResistOverCap", "@value": ""},
                {"@stat": "LightningResist", "@value": ""},
                {"@stat": "LightningResistOverCap", "@value": ""},
                {"@stat": "ChaosResist", "@value": ""},
                {"@stat": "ChaosResistOverCap", "@value": ""},
                {"@stat": "FullDPS", "@value": ""},
                {"@stat": "PowerCharges", "@value": ""},
                {"@stat": "PowerChargesMax", "@value": ""},
                {"@stat": "FrenzyCharges", "@value": ""},
                {"@stat": "FrenzyChargesMax", "@value": ""},
                {"@stat": "EnduranceCharges", "@value": ""},
                {"@stat": "EnduranceChargesMax", "@value": ""},
            ],
            "FullDPSSkill": [
                {
                    "@skillPart": "",
                    "@source": "",
                    "@stat": "Herald of Thunder",
                    "@value": "",
                },
                {
                    "@skillPart": "",
                    "@source": "",
                    "@stat": "Full Culling DPS",
                    "@value": "",
                },
                {"@skillPart": "", "@source": "", "@stat": "Storm Brand", "@value": ""},
                {
                    "@skillPart": "",
                    "@source": "",
                    "@stat": "Orb of Storms",
                    "@value": "",
                },
            ],
        },
        "Import": {
            "@lastAccountHash": "",
            "@lastRealm": "PC",
            "@lastCharacterHash": "",
        },
        "Calcs": {
            "Input": [
                {"@name": "misc_buffMode", "@string": "EFFECTIVE"},
                {"@name": "skill_number", "@number": "1"},
            ],
            "Section": [
                {"@collapsed": "false", "@id": "SkillSelect"},
                {"@collapsed": "false", "@id": "HitDamage"},
                {"@collapsed": "false", "@id": "Warcries"},
                {"@collapsed": "false", "@id": "Dot"},
                {"@collapsed": "false", "@id": "Speed"},
                {"@collapsed": "false", "@id": "Crit"},
                {"@collapsed": "false", "@id": "Impale"},
                {"@collapsed": "false", "@id": "SkillTypeStats"},
                {"@collapsed": "false", "@id": "HitChance"},
                {"@collapsed": "false", "@id": "Bleed"},
                {"@collapsed": "false", "@id": "Poison"},
                {"@collapsed": "false", "@id": "Ignite"},
                {"@collapsed": "false", "@id": "Decay"},
                {"@collapsed": "false", "@id": "LeechGain"},
                {"@collapsed": "false", "@id": "EleAilments"},
                {"@collapsed": "false", "@id": "MiscEffects"},
                {"@collapsed": "false", "@id": "Attributes"},
                {"@collapsed": "false", "@id": "Life"},
                {"@collapsed": "false", "@id": "Mana"},
                {"@collapsed": "false", "@id": "EnergyShield"},
                {"@collapsed": "false", "@id": "Ward"},
                {"@collapsed": "false", "@id": "Armour"},
                {"@collapsed": "false", "@id": "Evasion"},
                {"@collapsed": "false", "@id": "Resist"},
                {"@collapsed": "false", "@id": "Block"},
                {"@collapsed": "false", "@id": "MiscDefences"},
                {"@collapsed": "false", "@id": "DamageTaken"},
            ],
        },
        "Skills": {
            "@sortGemsByDPSField": "CombinedDPS",
            "@matchGemLevelToCharacterLevel": "false",
            "@sortGemsByDPS": "true",
            "@defaultGemQuality": "0",
            "@defaultGemLevel": "20",
            "@showSupportGemTypes": "ALL",
            "@showAltQualityGems": "false",
        },
        "Tree": {
            "@activeSpec": "1",
            "Spec": {
                "@title": "Default",
                "@ascendClassId": 0,
                "@masteryEffects": None,
                "@nodes": None,
                "@treeVersion": re.sub("\.", "_", str(_VERSION)),
                "@classId": 0,
                "EditedNodes": None,
                "URL": "https://www.pathofexile.com/passive-skill-tree/AAAABgAAAAAA",
                "Sockets": None,
            },
        },
        "Notes": None,
        "NotesHTML": None,
        "TreeView": {
            "@searchStr": "",
            "@zoomY": "",
            "@showHeatMap": "false",
            "@zoomLevel": "1",
            "@showStatDifferences": "true",
            "@zoomX": "",
        },
        "Items": {
            "@activeItemSet": 1,
            "@useSecondWeaponSet": "false",
            "Slot": [
                {"@name": "Weapon 1", "@itemId": ""},
                {"@name": "Flask 3", "@itemId": ""},
                {"@name": "Gloves", "@itemId": ""},
                {"@name": "Belt", "@itemId": ""},
                {"@name": "Flask 5", "@itemId": ""},
                {"@name": "Helmet", "@itemId": ""},
                {"@name": "Flask 1", "@itemId": ""},
                {"@name": "Belt Abyssal Socket 1", "@itemId": ""},
                {"@name": "Flask 4", "@itemId": ""},
                {"@name": "Flask 2", "@itemId": ""},
                {"@name": "Weapon 2 Swap", "@itemId": ""},
                {"@name": "Weapon 1 Swap", "@itemId": ""},
                {"@name": "Ring 2", "@itemId": ""},
                {"@name": "Body Armour", "@itemId": ""},
                {"@name": "Ring 1", "@itemId": ""},
                {"@name": "Boots", "@itemId": ""},
                {"@name": "Amulet", "@itemId": ""},
            ],
            "ItemSet": {"@useSecondWeaponSet": "false", "@id": 1},
        },
        "Config": None,
    }
}

bandits = {
    "None": "2 Passives Points",
    "Oak": "Oak (Life Regen, Phys.Dmg. Reduction, Phys.Dmg)",
    "Kraityn": "Kraityn (Attack/Cast Speed, Avoid Elemental Ailments, Move Speed)",
    "Alira": "Alira (Mana Regen, Crit Multiplier, Resists)",
}

pantheon_major_gods = {
    "None": "Godless",
    "TheBrineKing": "Soul of the Brine King",
    "Lunaris": "Soul of Lunaris",
    "Solaris": "Soul of Solaris",
    "Arakaali": "Soul of Arakaali",
}

pantheon_minor_gods = {
    "None": "Godless",
    "Gruthkul": "Soul of Gruthkul",
    "Yugul": "Soul of Yugul",
    "Abberath": "Soul of Abberath",
    "Tukohama": "Soul of Tukohama",
    "Garukhan": "Soul of Garukhan",
    "Ralakesh": "Soul of Ralakesh",
    "Ryslatha": "Soul of Ryslatha",
    "Shakari": "Soul of Shakari",
}


class Layers(IntEnum):
    backgrounds = -3
    group = -2
    connectors = -1
    inactive = 0
    active = 1
    small_overlays = 2
    key_overlays = 3


class ColourCodes(Enum):
    NORMAL = 0x000000
    MAGIC = 0x8888FF
    RARE = 0xFFFF77
    UNIQUE = 0xAF6025
    RELIC = 0x60C060
    GEM = 0x1AA29B
    PROPHECY = 0xB54BFF
    CURRENCY = 0xAA9E82
    CRAFTED = 0xB8DAF1
    CUSTOM = 0x5CF0BB
    SOURCE = 0x88FFFF
    UNSUPPORTED = 0xF05050
    WARNING = 0xFF9922
    TIP = 0x80A080
    FIRE = 0xB97123
    COLD = 0x3F6DB3
    LIGHTNING = 0xADAA47
    CHAOS = 0xD02090
    POSITIVE = 0x33FF77
    NEGATIVE = 0xDD0022
    OFFENCE = 0xE07030
    DEFENCE = 0x8080E0
    SCION = 0xFFF0F0
    MARAUDER = 0xE05030
    RANGER = 0x70FF70
    WITCH = 0x7070FF
    DUELIST = 0xE0E070
    TEMPLAR = 0xC040FF
    SHADOW = 0x30C0D0
    MAINHAND = 0x50FF50
    MAINHANDBG = 0x071907
    OFFHAND = 0xB7B7FF
    OFFHANDBG = 0x070719
    SHAPER = 0x55BBFF
    ELDER = 0xAA77CC
    FRACTURED = 0xA29160
    ADJUDICATOR = 0xE9F831
    BASILISK = 0x00CB3A
    CRUSADER = 0x2946FC
    EYRIE = 0xAAB7B8
    CLEANSING = 0xF24141
    TANGLE = 0x038C8C
    CHILLBG = 0x151E26
    FREEZEBG = 0x0C262B
    SHOCKBG = 0x191732
    SCORCHBG = 0x270B00
    BRITTLEBG = 0x00122B
    SAPBG = 0x261500
    SCOURGE = 0xFF6E25
    STRENGTH = MARAUDER
    DEXTERITY = RANGER
    INTELLIGENCE = WITCH
    LIFE = MARAUDER
    MANA = WITCH
    ES = SOURCE
    WARD = RARE
    EVASION = POSITIVE
    RAGE = WARNING
    PHYS = NORMAL


class PlayerClasses(Enum):
    SCION = 0
    MARAUDER = 1
    RANGER = 2
    WITCH = 3
    DUELIST = 4
    TEMPLAR = 5
    SHADOW = 6


# Background artwork behind the tree
class_backgrounds = {
    PlayerClasses.SCION: {"n": "", "x": 0, "y": 0},
    PlayerClasses.MARAUDER: {
        "n": "BackgroundStr",
        "x": -3500 / global_scale_factor,
        "y": 350 / global_scale_factor,
    },
    PlayerClasses.RANGER: {
        "n": "BackgroundDex",
        "x": 1850 / global_scale_factor,
        "y": 250 / global_scale_factor,
    },
    PlayerClasses.WITCH: {
        "n": "BackgroundInt",
        "x": -1200 / global_scale_factor,
        "y": -3050 / global_scale_factor,
    },
    PlayerClasses.DUELIST: {
        "n": "BackgroundStrDex",
        "x": -1400 / global_scale_factor,
        "y": 1350 / global_scale_factor,
    },
    PlayerClasses.TEMPLAR: {
        "n": "BackgroundStrInt",
        "x": -2950 / global_scale_factor,
        "y": -2600 / global_scale_factor,
    },
    PlayerClasses.SHADOW: {
        "n": "BackgroundDexInt",
        "x": 1350 / global_scale_factor,
        "y": -3050 / global_scale_factor,
    },
}


# The start point for each class
# ToDo: The start points need to be fixed
class_centres = {
    PlayerClasses.SCION: {
        "n": "centerScion",
        "x": -150 / global_scale_factor,
        "y": -150 / global_scale_factor,
    },
    PlayerClasses.MARAUDER: {
        "n": "centerMarauder",
        "x": -2970 / global_scale_factor,
        "y": 1490 / global_scale_factor,
    },
    PlayerClasses.RANGER: {
        "n": "centerRanger",
        "x": 2690 / global_scale_factor,
        "y": 1490 / global_scale_factor,
    },
    PlayerClasses.WITCH: {
        "n": "centerWitch",
        "x": -150 / global_scale_factor,
        "y": -3340 / global_scale_factor,
    },
    PlayerClasses.DUELIST: {
        "n": "centerDuelist",
        "x": -150 / global_scale_factor,
        "y": 3040 / global_scale_factor,
    },
    PlayerClasses.TEMPLAR: {
        "n": "centerTemplar",
        "x": -2990 / global_scale_factor,
        "y": -1780 / global_scale_factor,
    },
    PlayerClasses.SHADOW: {
        "n": "centerShadow",
        "x": 2690 / global_scale_factor,
        "y": -1780 / global_scale_factor,
    },
}


""" Ascendancy circles around the outside of the tree """
ascendancy_positions = {
    "Ascendant": {"x": -7800.0 / global_scale_factor, "y": 7200 / global_scale_factor},
    "Berserker": {"x": -10400 / global_scale_factor, "y": 3700 / global_scale_factor},
    "Chieftain": {
        "x": -10400 / global_scale_factor,
        "y": 2200 / global_scale_factor,
    },  # data Error
    "Juggernaut": {"x": -10400 / global_scale_factor, "y": 5200 / global_scale_factor},
    "Deadeye": {"x": 10200 / global_scale_factor, "y": 2200 / global_scale_factor},
    "Pathfinder": {"x": 10200 / global_scale_factor, "y": 3700 / global_scale_factor},
    "Raider": {"x": 10200 / global_scale_factor, "y": 5200 / global_scale_factor},
    "Elementalist": {"x": 0 / global_scale_factor, "y": -9850 / global_scale_factor},
    "Occultist": {"x": -1500 / global_scale_factor, "y": -9850 / global_scale_factor},
    "Necromancer": {"x": 1500 / global_scale_factor, "y": -9850 / global_scale_factor},
    "Champion": {"x": 0 / global_scale_factor, "y": 9800 / global_scale_factor},
    "Gladiator": {"x": -1500 / global_scale_factor, "y": 9800 / global_scale_factor},
    "Slayer": {"x": 1500 / global_scale_factor, "y": 9800 / global_scale_factor},
    "Guardian": {"x": -10400 / global_scale_factor, "y": -5200 / global_scale_factor},
    "Hierophant": {"x": -10400 / global_scale_factor, "y": -3700 / global_scale_factor},
    "Inquisitor": {
        "x": -10400 / global_scale_factor,
        "y": -2200 / global_scale_factor,
    },  # data Error
    "Assassin": {"x": 10200 / global_scale_factor, "y": -5200 / global_scale_factor},
    "Saboteur": {"x": 10200 / global_scale_factor, "y": -2200 / global_scale_factor},
    "Trickster": {"x": 10200 / global_scale_factor, "y": -3700 / global_scale_factor},
}


nodeOverlay = {
    "Normal": {
        "artWidth": "40",
        "alloc": "PSSkillFrameActive",
        "path": "PSSkillFrameHighlighted",
        "unalloc": "PSSkillFrame",
        "allocAscend": "AscendancyFrameSmallAllocated",
        "pathAscend": "AscendancyFrameSmallCanAllocate",
        "unallocAscend": "AscendancyFrameSmallNormal",
    },
    "Notable": {
        "artWidth": "58",
        "alloc": "NotableFrameAllocated",
        "path": "NotableFrameCanAllocate",
        "unalloc": "NotableFrameUnallocated",
        "allocAscend": "AscendancyFrameLargeAllocated",
        "pathAscend": "AscendancyFrameLargeCanAllocate",
        "unallocAscend": "AscendancyFrameLargeNormal",
        "allocBlighted": "BlightedNotableFrameAllocated",
        "pathBlighted": "BlightedNotableFrameCanAllocate",
        "unallocBlighted": "BlightedNotableFrameUnallocated",
    },
    "Keystone": {
        "artWidth": "84",
        "alloc": "KeystoneFrameAllocated",
        "path": "KeystoneFrameCanAllocate",
        "unalloc": "KeystoneFrameUnallocated",
    },
    "Socket": {
        "artWidth": "58",
        "alloc": "JewelFrameAllocated",
        "path": "JewelFrameCanAllocate",
        "unalloc": "JewelFrameUnallocated",
        "allocAlt": "JewelSocketAltActive",
        "pathAlt": "JewelSocketAltCanAllocate",
        "unallocAlt": "JewelSocketAltNormal",
    },
    "Mastery": {
        "artWidth": "65",
        "alloc": "AscendancyFrameLargeAllocated",
        "path": "AscendancyFrameLargeCanAllocate",
        "unalloc": "AscendancyFrameLargeNormal",
    },
}
for _type in nodeOverlay:
    """
    From PassiveTree.lua file. Setting as the same scope as the 'constant'
    """
    data = nodeOverlay[_type]
    size = int(data["artWidth"]) * 1.33
    data["size"] = size
    data["rsq"] = size * size


class PlayerAscendancies(Enum):
    NONE = None


def str_to_bool(in_str):
    """
    Return a boolean from a string. As the settings could be manipulated by a human, we can't trust eval()
      EG: eval('os.system(`rm -rf /`)')
    :returns: True if it looks like it could be true, otherwise false
    """
    return in_str.lower() in ("yes", "true", "t", "1", "on")


class Config:
    def __init__(self, _win, _app) -> None:
        # To reduce circular references, have the app and main window references here
        self.win = _win
        self.app = _app
        self.config = (
            None  # this is the dictionary representing the xml, not a pointer to itself
        )
        self.screen_rect = self.app.primaryScreen().size()

        self.exeDir = Path.cwd()
        self.settingsFile = Path(self.exeDir, "settings.xml")
        self.buildPath = Path(self.exeDir, "builds")
        if not self.buildPath.exists():
            self.buildPath.mkdir()
        self.tree_data_path = Path(self.exeDir, "TreeData")
        if not self.tree_data_path.exists():
            self.tree_data_path.mkdir()
        self.misc = {}
        self.read()

    def read(self):
        """Set self.config with the contents of the settings file"""
        if self.settingsFile.exists():
            # try:
            self.config = OrderedDict(pob_file.read_xml(self.settingsFile))
            self.misc = self.config["PathOfBuilding"]["Misc"]
        if self.config is None:
            self.config = default_config

    def write(self):
        """Write the settings file"""
        pob_file.write_xml(self.settingsFile, self.config)

    @property
    def theme(self):
        _theme = self.misc.get("theme", "Dark")
        if _theme not in ("Dark", "Light"):
            _theme = "Dark"
        return _theme

    @theme.setter
    def theme(self, new_theme):
        self.misc["theme"] = new_theme and "Dark" or "Light"

    @property
    def slotOnlyTooltips(self):
        return str_to_bool(self.misc.get("slotOnlyTooltips", True))

    @slotOnlyTooltips.setter
    def slotOnlyTooltips(self, new_bool):
        self.misc["slotOnlyTooltips"] = str(new_bool)

    @property
    def showTitlebarName(self):
        return str_to_bool(self.misc.get("showTitlebarName", True))

    @showTitlebarName.setter
    def showTitlebarName(self, new_bool):
        self.misc["showTitlebarName"] = str(new_bool)

    @property
    def showWarnings(self):
        return str_to_bool(self.misc.get("showWarnings", True))

    @showWarnings.setter
    def showWarnings(self, new_bool):
        self.misc["showWarnings"] = str(new_bool)

    @property
    # fmt: off
    def defaultCharLevel(self):
        _defaultCharLevel = self.misc.get("defaultCharLevel", 1)
        if _defaultCharLevel < 1:
            _defaultCharLevel = 1
            self.misc["defaultCharLevel"] = f"{_defaultCharLevel}"
        if _defaultCharLevel > 100:
            _defaultCharLevel = 100
            self.misc["defaultCharLevel"] = f"{_defaultCharLevel}"
        return _defaultCharLevel
    # fmt: on

    @defaultCharLevel.setter
    def defaultCharLevel(self, new_int):
        self.misc["defaultCharLevel"] = f"{new_int}"

    @property
    def nodePowerTheme(self):
        return self.misc.get("nodePowerTheme", "RED/BLUE")

    @nodePowerTheme.setter
    def nodePowerTheme(self, new_theme):
        self.misc["nodePowerTheme"] = new_theme

    @property
    def connectionProtocol(self):
        return self.misc.get("connectionProtocol", "nil")

    @connectionProtocol.setter
    def connectionProtocol(self, new_conn):
        # what is this for
        self.misc["connectionProtocol"] = new_conn

    @property
    def decimalSeparator(self):
        return self.misc.get("decimalSeparator", ".")

    @decimalSeparator.setter
    def decimalSeparator(self, new_sep):
        self.misc["decimalSeparator"] = new_sep

    @property
    def thousandsSeparator(self):
        return self.misc.get("thousandsSeparator", ",")

    @thousandsSeparator.setter
    def thousandsSeparator(self, new_sep):
        self.misc["thousandsSeparator"] = new_sep

    @property
    def showThousandsSeparators(self):
        return str_to_bool(self.misc.get("showThousandsSeparators", True))

    @showThousandsSeparators.setter
    def showThousandsSeparators(self, new_bool):
        self.misc["showThousandsSeparators"] = str(new_bool)

    @property
    # fmt: off
    def defaultGemQuality(self):
        _defaultGemQuality = self.misc.get("defaultGemQuality", 1)
        if _defaultGemQuality < 0:
            _defaultGemQuality = 0
            self.misc["defaultGemQuality"] = f"{_defaultGemQuality}"
        if _defaultGemQuality > 20:
            _defaultGemQuality = 0
            self.misc["defaultGemQuality"] = f"{_defaultGemQuality}"
        return _defaultGemQuality
    # fmt: on

    @defaultGemQuality.setter
    def defaultGemQuality(self, new_int):
        self.misc["defaultGemQuality"] = f"{new_int}"

    @property
    def buildSortMode(self):
        return self.misc.get("buildSortMode", "NAME")

    @buildSortMode.setter
    def buildSortMode(self, new_mode):
        self.misc["buildSortMode"] = new_mode

    @property
    def betaMode(self):
        return str_to_bool(self.misc.get("betaMode", False))

    @betaMode.setter
    def betaMode(self, new_bool):
        self.misc["betaMode"] = str(new_bool)

    @property
    def size(self):
        """
        Return the window size as they were last written to settings. This ensures the user has the same experience.
        800 x 600 was chosen as the default as it has been learnt, with the lua version,
          that some users in the world have small screen laptops.
        Attempt to protect against silliness by limiting size to the screen size.
          This could happen if someone changes their desktop size or copy program from another machine.
        :returns: a QSize(width, height)
        """
        try:
            width = int(self.config["PathOfBuilding"]["size"]["width"])
            if width < 800:
                width = 800
            height = int(self.config["PathOfBuilding"]["size"]["height"])
            if height < 600:
                height = 600
        except KeyError:
            width = 800
            height = 600
        if width > self.screen_rect.width():
            print(f"Width: {width} is bigger than {self.screen_rect}. Correcting ...")
            _size = self.screen_rect
        if height > self.screen_rect.height():
            print(f"Height: {height} is bigger than {self.screen_rect}. Correcting ...")
            _size = self.screen_rect
        return QSize(width, height)

    @size.setter
    def size(self, new_size: QSize):
        self.config["PathOfBuilding"]["size"] = {
            "width": new_size.width(),
            "height": new_size.height(),
        }

    def recent_builds(self):
        """
        Recent builds are a list of xml's that have been opened, to a maximum of 10 entries
        :returns: an Ordered dictionary list of recent builds
        """
        try:
            output = self.config["PathOfBuilding"]["recentBuilds"]
        except KeyError:
            print("recentBuilds exception")
            output = {
                "r0": "",
                "r1": "",
                "r2": "",
                "r3": "",
                "r4": "",
            }
        self.config["PathOfBuilding"]["recentBuilds"] = output
        return OrderedDict(output)

    def add_recent_build(self, filename):
        """
        Adds one build to the list of recent builds
        :param filename: str(): name of build xml
        :returns: n/a
        """
        if filename not in self.config["PathOfBuilding"]["recentBuilds"].values():
            for idx in [3, 2, 1, 0]:
                # fmt: off
                self.config["PathOfBuilding"]["recentBuilds"][f"r{idx + 1}"]\
                    = self.config["PathOfBuilding"]["recentBuilds"][f"r{idx}"]
                # fmt: on
            self.config["PathOfBuilding"]["recentBuilds"]["r0"] = filename
