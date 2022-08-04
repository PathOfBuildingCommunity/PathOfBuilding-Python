"""Enumeration Data for Path of Exile constants."""

import re
import enum

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
                "@nodes": "0",
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


class Layers(enum.IntEnum):
    backgrounds = -3
    group = -2
    connectors = -1
    inactive = 0
    active = 1
    small_overlays = 2
    key_overlays = 3


class ColourCodes(enum.Enum):
    NORMAL = "#F0F0F0"
    BLACK = "#000000"
    MAGIC = "#8888FF"
    RARE = "#FFFF77"
    UNIQUE = "#AF6025"
    RELIC = "#60C060"
    GEM = "#1AA29B"
    PROPHECY = "#B54BFF"
    CURRENCY = "#AA9E82"
    CRAFTED = "#B8DAF1"
    CUSTOM = "#5CF0BB"
    SOURCE = "#88FFFF"
    UNSUPPORTED = "#F05050"
    WARNING = "#FF9922"
    TIP = "#80A080"
    FIRE = "#B97123"
    COLD = "#3F6DB3"
    LIGHTNING = "#ADAA47"
    CHAOS = "#D02090"
    POSITIVE = "#33FF77"
    NEGATIVE = "#DD0022"
    OFFENCE = "#E07030"
    DEFENCE = "#8080E0"
    SCION = "#FFF0F0"
    MARAUDER = "#E05030"
    RANGER = "#70FF70"
    WITCH = "#7070FF"
    DUELIST = "#E0E070"
    TEMPLAR = "#C040FF"
    SHADOW = "#30C0D0"
    MAINHAND = "#50FF50"
    MAINHANDBG = "#071907"
    OFFHAND = "#B7B7FF"
    OFFHANDBG = "#070719"
    SHAPER = "#55BBFF"
    ELDER = "#AA77CC"
    FRACTURED = "#A29160"
    ADJUDICATOR = "#E9F831"
    BASILISK = "#00CB3A"
    CRUSADER = "#2946FC"
    EYRIE = "#AAB7B8"
    CLEANSING = "#F24141"
    TANGLE = "#038C8C"
    CHILLBG = "#151E26"
    FREEZEBG = "#0C262B"
    SHOCKBG = "#191732"
    SCORCHBG = "#270B00"
    BRITTLEBG = "#00122B"
    SAPBG = "#261500"
    SCOURGE = "#FF6E25"
    GRAY = "#D3D3D3"
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


@enum.unique
class PlayerClasses(enum.IntEnum):
# class PlayerClasses(Enum):
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


@enum.unique
class PlayerAscendancy(enum.Enum):
    NONE = None


stats_list = {
    "ActiveMinionLimit": {"stat": "ActiveMinionLimit", "label": "Active Minion Limit", "fmt": "{:d}" },
    "AverageHit": {"label": "Average Damage", "fmt": "{0:.2f}"},
    "AverageDamage": {"stat": "AverageDamage", "label": "Average Damage", "fmt": "{:.1f}", "flag": "attack"},
    "ServerTriggerRate": {"stat": "ServerTriggerRate", "label": "Trigger Rate", "fmt": "{:.2f}"},
    "Speed": {"label": "Attack Rate", "fmt": "{0:.2f}", "flag": "attack"},
    "Speed": {"label": "Cast Rate", "fmt": "{0:.2f}", "flag": "spell"},
    "Speed": {"stat": "Speed", "label": "Effective Trigger Rate", "fmt": "{:.2f}"},
    "WarcryCastTime": {"stat": "WarcryCastTime", "label": "Cast Time", "fmt": ".2fs", "flag": "warcry" },
    "HitSpeed": {"label": "Hit Rate", "fmt": "{:.2f}"},
    "TrapThrowingTime": {"label": "Trap Throwing Time", "fmt": ".2fs", },
    "TrapCooldown": {"label": "Trap Cooldown", "fmt": ".3fs", },
    "MineLayingTime": {"label": "Mine Throwing Time", "fmt": ".2fs", },
    "TotemPlacementTime": {"label": "Totem Placement Time", "fmt": ".2fs", },
    "PreEffectiveCritChance": {"label": "Crit Chance", "fmt": "{0:.2g}%"},
    "CritChance": {"label": "Effective Crit Chance", "fmt": "{0:.2g}%"},
    "CritMultiplier": {"label": "Crit Multiplier", "fmt": "{0:.2f}"},
    "HitChance": {"label": "Hit Chance", "fmt": ".0f%", "flag": "attack"},
    "TotalDPS": {"label": "Total DPS", "fmt": "{:.1f}", "flag": "notAverage"},
    "TotalDPS": {"label": "Total DPS", "fmt": "{:.1f}", "flag": "showAverage"},
    "TotalDot": {"label": "DoT DPS", "fmt": "{:.1f}", },
    "WithDotDPS": {"label": "Total DPS inc. DoT", "fmt": "{:.1f}", "flag": "notAverage"},
    "BleedDPS": {"label": "Bleed DPS", "fmt": "{:.1f}", },
    "BleedDamage": {"label": "Total Damage per Bleed", "fmt": "{:.1f}", "flag": "showAverage"},
    "WithBleedDPS": {"label": "Total DPS inc. Bleed", "fmt": "{0:.2f}"},
    "IgniteDPS": {"label": "Ignite DPS", "fmt": "{:.1f}", },
    "IgniteDamage": {"label": "Total Damage per Ignite", "fmt": "{:.1f}", "flag": "showAverage"},
    "WithIgniteDPS": {"label": "Total DPS inc. Ignite", "fmt": "{0:.2f}"},
    "WithIgniteAverageDamage": {"label": "Average Dmg. inc. Ignite", "fmt": "{:.1f}", },
    "PoisonDPS": {"label": "Poison DPS", "fmt": "{:.1f}", },
    "PoisonDamage": {"label": "Total Damage per Poison", "fmt": "{:.1f}", },
    "WithPoisonDPS": {"label": "Total DPS inc. Poison", "fmt": "{0:.2f}"},
    "DecayDPS": {"label": "Decay DPS", "fmt": "{:.1f}", },
    "TotalDotDPS": {"label": "Total DPS inc. DoT", "fmt": "{0:.2f}"},
    "ImpaleDPS": {"label": "Impale Damage", "fmt": "{:.1f}", "flag": "impale", "flag": "showAverage"},
    "WithImpaleDPS": {"label": "Damage inc. Impale", "fmt": "{:.1f}", "flag": "impale", "flag": "showAverage"},
    "ImpaleDPS": {"label": "Impale DPS", "fmt": "{:.1f}", "flag": "impale", "flag": "notAverage"},
    "WithImpaleDPS": {"label": "Total DPS inc. Impale", "fmt": "{:.1f}", "flag": "impale", "flag": "notAverage"},
    "MirageDPS": {"label": "Total Mirage DPS", "fmt": "{:.1f}"},
    "CullingDPS": {"label": "Culling DPS", "fmt": "{0:.2f}"},
    "CombinedDPS": {"label": "Combined DPS", "fmt": "{0:.2f}"},
    "CombinedAvg": {"label": "Combined Total Damage", "fmt": "{:.1f}", "flag": "showAverage"},
    "Cooldown": {"label": "Skill Cooldown", "fmt": ".3fs", },
    "SealCooldown": {"label": "Seal Gain Frequency", "fmt": ".2fs", },
    "SealMax": {"label": "Max Number of Seals", "fmt": "{:d}"},
    "TimeMaxSeals": {"label": "Time to Gain Max Seals", "fmt": ".2fs", },
    "AreaOfEffectRadius": {"label": "AoE Radius", "fmt": "{0:.2f}"},
    "BrandAttachmentRange": {"label": "Attachment Range", "fmt": "{:d}", "flag": "brand"},
    "BrandTicks": {"label": "Activations per Brand", "fmt": "{:d}", "flag": "brand"},
    "ManaCost": {"label": "Mana Cost", "colour": ColourCodes.MANA, "fmt": "{0:.2f}"},
    "LifeCost": {"label": "Life Cost", "colour": ColourCodes.LIFE, "fmt": "{0:.2f}"},
    "ESCost": {"label": "Energy Shield Cost", "colour": ColourCodes.ES, "fmt": "{0:.2f}"},
    "RageCost": {"label": "Rage Cost", "colour": ColourCodes.RAGE, "fmt": "{0:.2f}"},
    "ManaPercentCost": {"label": "Mana Cost", "colour": ColourCodes.MANA, "fmt": "{0:.2f}"},
    "LifePercentCost": {"label": "Life Cost", "colour": ColourCodes.LIFE, "fmt": "{0:.2f}"},
    "ManaPerSecondCost": {"label": "Mana Cost", "colour": ColourCodes.MANA, "fmt": "{0:.2f}"},
    "LifePerSecondCost": {"label": "Life Cost", "colour": ColourCodes.LIFE, "fmt": "{0:.2f}"},
    "ManaPercentPerSecondCost": {"label": "Mana Cost", "colour": ColourCodes.MANA, "fmt": "{0:.2f}"},
    "LifePercentPerSecondCost": {"label": "Life Cost", "colour": ColourCodes.LIFE, "fmt": "{0:.2f}"},
    "ESPerSecondCost": {"label": "Energy Shield Cost", "fmt": ".2f/s", "colour": ColourCodes.ES, },
    "ESPercentPerSecondCost": {"label": "Energy Shield Cost", "fmt": ".2f%/s", "colour": ColourCodes.ES,},
    "blank1": {},
    "Str": {"label": "Strength", "colour": ColourCodes.STRENGTH, "fmt": "{:d}"},
    "ReqStr": {"label": "Strength Required", "colour": ColourCodes.STRENGTH, "fmt": "{:d}"},
    "Dex": {"label": "Dexterity", "colour": ColourCodes.DEXTERITY, "fmt": "{:d}"},
    "ReqDex": {"label": "Dexterity Required", "colour": ColourCodes.DEXTERITY, "fmt": "{:d}"},
    "Int": {"label": "Intelligence", "colour": ColourCodes.INTELLIGENCE, "fmt": "{:d}"},
    "ReqInt": {"label": "Intelligence Required", "colour": ColourCodes.INTELLIGENCE, "fmt": "{:d}"},
    "Omni": {"label": "Omniscience", "colour": ColourCodes.RARE, "fmt": "{:d}"},
    "ReqOmni": {"label": "Omniscience Required", "colour": ColourCodes.RARE, "fmt": "{:d}"},
    "blank2": {},
    "Devotion": {"label": "Devotion", "colour": ColourCodes.RARE, "fmt": "{:d}"},
    "blank3": {},
    "TotalEHP": {"label": "Effective Hit Pool", "fmt": "{:.0f}", },
    "SecondMinimalMaximumHitTaken": {"label": "Eff. Maximum Hit Taken", "fmt": "{:.0f}", },
    "blank4": {},
    "Life": {"label": "Total Life", "fmt": "{:d}", "colour": ColourCodes.LIFE, },
    "Spec:LifeInc": {"label": "%Inc Life from Tree", "fmt": "{:d}%", "colour": ColourCodes.LIFE},
    "LifeUnreserved": {"label": "Unreserved Life", "fmt": "{:d}", "colour": ColourCodes.LIFE},
    "LifeUnreservedPercent": {"label": "Unreserved Life", "fmt": "{:d}%", "colour": ColourCodes.LIFE},
    "LifeRegen": {"label": "Life Regen", "fmt": "{:.1f}", "colour": ColourCodes.LIFE},
    "LifeLeechGainRate": {"label": "Life Leech/On Hit Rate", "fmt": "{:.1f}", "colour": ColourCodes.LIFE, },
    "LifeLeechGainPerHit": {"label": "Life Leech/Gain per Hit", "fmt": "{:.1f}", "colour": ColourCodes.LIFE, },
    "blank5": {},
    "TotalDegen": {"label": "Total Degen", "fmt": "{:.1f}", },
    "TotalNetRegen": {"label": "Total Net Regen", "fmt": "+{:.1f}"},
    "NetLifeRegen": {"label": "Net Life Regen", "fmt": "+{:.1f}", "colour": ColourCodes.LIFE},
    "NetManaRegen": {"label": "Net Mana Regen", "fmt": "+{:.1f}", "colour": ColourCodes.MANA},
    "NetEnergyShieldRegen": {"label": "Net Energy Shield Regen", "fmt": "+{:.1f}", "colour": ColourCodes.ES},
    "blank6": {},
    "Ward": {"label": "Ward", "fmt": "{:d}", "colour": ColourCodes.WARD, },
    "EnergyShield": {"label": "Energy Shield", "fmt": "{:d}", "colour": ColourCodes.ES, },
    "EnergyShieldRecoveryCap": {"label": "Recoverable ES", "colour": ColourCodes.ES, "fmt": "{:d}"},
    "Spec:EnergyShieldInc": {"label": "%Inc ES from Tree", "colour": ColourCodes.ES, "fmt": "{:d}%"},
    "EnergyShieldRegen": {"label": "Energy Shield Regen", "colour": ColourCodes.ES, "fmt": "{:.1f}"},
    "EnergyShieldLeechGainRate": {"label": "ES Leech/On Hit Rate", "colour": ColourCodes.ES, "fmt": "{:.1f}", },
    "EnergyShieldLeechGainPerHit": {"label": "ES Leech/Gain per Hit", "colour": ColourCodes.ES, "fmt": "{:.1f}", },
    "blank7": {},
    "Evasion": {"label": "Evasion rating", "fmt": "{:d}", "colour": ColourCodes.EVASION, },
    "Spec:EvasionInc": {"label": "%Inc Evasion from Tree", "colour": ColourCodes.EVASION, "fmt": "{:d}%"},
    "MeleeEvadeChance": {"label": "Evade Chance", "fmt": "{:d}%", "colour": ColourCodes.EVASION},
    "MeleeEvadeChance": {"label": "Melee Evade Chance", "fmt": "{:d}%", "colour": ColourCodes.EVASION},
    "ProjectileEvadeChance": {"label": "Projectile Evade Chance", "fmt": "{:d}%", "colour": ColourCodes.EVASION},
    "blank8": {},
    "Armour": {"label": "Armour", "fmt": "{:d}", },
    "Spec:ArmourInc": {"label": "%Inc Armour from Tree", "fmt": "{:d}%"},
    "PhysicalDamageReduction": {"label": "Phys. Damage Reduction", "fmt": "{:d}%"},
    "blank9": {},
    "EffectiveMovementSpeedMod": {"label": "Movement Speed Modifier", "fmt": "{:.1f}%", },
    "BlockChance": {"label": "Block Chance", "fmt": "{:d}%", },
    "SpellBlockChance": {"label": "Spell Block Chance", "fmt": "{:d}%", },
    "AttackDodgeChance": {"label": "Attack Dodge Chance", "fmt": "{:d}%", },
    "SpellDodgeChance": {"label": "Spell Dodge Chance", "fmt": "{:d}%", },
    "SpellSuppressionChance": {"label": "Spell Suppression Chance", "fmt": "{:d}%", },
    "blank10": {},
    "FireResist": {"label": "Fire Resistance", "fmt": "{:d}%", "colour": ColourCodes.FIRE},
    "FireResistOverCap": {"label": "Fire Res. Over Max", "fmt": "{:d}%", "hideStat": "true"},
    "ColdResist": {"label": "Cold Resistance", "fmt": "{:d}%", "colour": ColourCodes.COLD},
    "ColdResistOverCap": {"label": "Cold Res. Over Max", "fmt": "{:d}%", "hideStat": "true"},
    "LightningResist": {"label": "Lightning Resistance", "fmt": "{:d}%", "colour": ColourCodes.LIGHTNING},
    "LightningResistOverCap": {"label": "Lightning Res. Over Max", "fmt": "{:d}%", "hideStat": "true"},
    "ChaosResist": {"label": "Chaos Resistance", "fmt": "{:d}%", "colour": ColourCodes.CHAOS},
    "ChaosResistOverCap": {"label": "Chaos Res. Over Max", "fmt": "{:d}%", "hideStat": "true"},
}
