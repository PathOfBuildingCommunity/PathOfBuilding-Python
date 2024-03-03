"""Enumeration Data for Path of Exile constants."""

import enum
import locale

locale.setlocale(locale.LC_ALL, "")

program_title = "Path of Building"
bad_text = "oh noes"  # used for dictionary get's
"""global_scale_factor
this is used to divide all x and y data coming in from the tree.json, but not Height and Width.
without this, items are too far apart and items are far too small on screen.
All values should only be scaled on point of entry, ie: when they are first processed out of the json
"""
global_scale_factor = 2.5
pob_debug = True  # Default setting for now. Will move to settings.xml

tree_versions = {
    "3_18": "3.18",
    "3_19": "3.19",
    "3_20": "3.20",
    "3_21": "3.21",
    "3_22": "3.22",
    "3_23": "3.23",
}
_VERSION_str = "3_23"
_VERSION = tree_versions[_VERSION_str]
default_view_mode = "TREE"
# default_view_mode = "ITEMS"
# default_view_mode = "SKILLS"

default_max_charges = 3

# Default config incase the settings file doesn't exist
def_theme = "dark"
default_settings = f"""<PathOfBuilding>
<Misc theme="{def_theme}" slotOnlyTooltips="true" showTitlebarName="true" showWarnings="true" defaultCharLevel="1" 
nodePowerTheme="0" connectionProtocol="0" thousandsSeparator="n" decimalSeparator="_" 
showThousandsSeparators="true" betaTest="false"  defaultGemQuality="0" buildSortMode="NAME" 
defaultItemAffixQuality="0.5" colour_positive="#33FF77" colour_negative="#FF0022" colour_highlight="#FF0000"
proxyURL="" buildPath="" open_build=""/>
   <recentBuilds/>
   <size width="800" height="600"/>
</PathOfBuilding>"""

default_spec = f"""<Spec title="Default" classId="0" ascendClassId="0" masteryEffects="" nodes="58833" 
treeVersion="{_VERSION_str}"></Spec>"""
default_skill_set = """<SkillSet id="1" title="Default">
  <Skill mainActiveSkillCalcs="1" includeInFullDPS="false" label="" enabled="true" slot="" mainActiveSkill="1"></Skill>
</SkillSet>"""

empty_build = f"""
<PathOfBuilding>
    <Build version="2" level="1" targetVersion="3_0" bandit="None" className="Scion" ascendClassName="None"
     mainSocketGroup="1" viewMode="{default_view_mode}" pantheonMajorGod="None" pantheonMinorGod="None">
            <PlayerStat stat="AverageHit" value="0"/>
     </Build>
    <Import/>
    <Calcs/>
    <Skills sortGemsByDPSField="CombinedDPS" matchGemLevelToCharacterLevel="false" activeSkillSet="1" 
        sortGemsByDPS="true" defaultGemQuality="0" defaultGemLevel="normalMaximum" showSupportGemTypes="ALL" 
        showAltQualityGems="false">
        {default_skill_set}
    </Skills>
    <Items activeItemSet="1">
        <ItemSet useSecondWeaponSet="false" id="1"/>
    </Items>
    <Tree activeSpec="1">
        {default_spec}
    </Tree>
    <Notes/>
    <NotesHTML/>
    <TreeView searchStr="" zoomY="0" showHeatMap="nil" zoomLevel="3" showStatDifferences="true" zoomX="0"/>
    <Config>
        <Input name="resistancePenalty" number="-60"/>
        <Input name="pantheonMinorGod" string="None"/>
        <Input name="enemyIsBoss" string="None"/>
        <Input name="pantheonMajorGod" string="None"/>
        <Input name="bandit" string="None"/>
    </Config>
</PathOfBuilding>"""

empty_socket_group = """<Skill mainActiveSkillCalcs="1" includeInFullDPS="false" label="" 
enabled="true" slot="" mainActiveSkill="1"/>"""

empty_gem = """<Gem enableGlobal2="false" level="1" enableGlobal1="true" skillId="" qualityId="Default" 
gemId="" enabled="true" quality="0" count="1" nameSpec=""/>"""

resistance_penalty = {
    0: "None",
    -30: "Act 5 (-30%)",
    -60: "Act 10 (-60%)",
}

pantheon_major_gods = {
    "None": {"name": "Godless", "tooltip": "You get nothing, heathen"},
    "TheBrineKing": {
        "name": "Soul of the Brine King",
        "tooltip": "You cannot be Stunned if you've been Stunned or Blocked a Stunning Hit in the past 2 seconds",
    },
    "Lunaris": {
        "name": "Soul of Lunaris",
        "tooltip": "1% additional Physical Damage Reduction for each nearby Enemy, up to 8%\n"
        "1% increased Movement Speed for each nearby Enemy, up to 8%",
    },
    "Solaris": {
        "name": "Soul of Solaris",
        "tooltip": "6% additional Physical Damage Reduction while there is only one nearby Enemy\n"
        "20% chance to take 50% less Area Damage from Hits",
    },
    "Arakaali": {
        "name": "Soul of Arakaali",
        "tooltip": "10% reduced Damage taken from Damage Over Time",
    },
}

pantheon_minor_gods = {
    "None": {"name": "Godless", "tooltip": "You get nothing, heathen"},
    "Gruthkul": {
        "name": "Soul of Gruthkul",
        "tooltip": "1% additional Physical Damage Reduction for each Hit you've taken Recently up to a maximum of 5%",
    },
    "Yugul": {
        "name": "Soul of Yugul",
        "tooltip": "You and your Minions take 50% reduced Reflected Damage\n50% chance to Reflect Hexes",
    },
    "Abberath": {
        "name": "Soul of Abberath",
        "tooltip": "60% less Duration of Ignite on You",
    },
    "Tukohama": {
        "name": "Soul of Tukohama",
        "tooltip": "While stationary, gain 3% additional Physical Damage Reduction every second, up to a maximum of 9%",
    },
    "Garukhan": {
        "name": "Soul of Garukhan",
        "tooltip": "60% reduced Effect of Shock on you",
    },
    "Ralakesh": {
        "name": "Soul of Ralakesh",
        "tooltip": "25% reduced Physical Damage over Time taken while moving\n"
        "Moving while Bleeding doesn't cause you to take extra Damage",
    },
    "Ryslatha": {
        "name": "Soul of Ryslatha",
        "tooltip": "Life Flasks gain 3 Charges every 3 seconds if you haven't used a Life Flask Recently",
    },
    "Shakari": {
        "name": "Soul of Shakari",
        "tooltip": "50% less Duration of Poisons on you\n" "You cannot be Poisoned while there are at least 3 Poisons on you",
    },
}


class Layers(enum.IntEnum):
    backgrounds = -4
    group = -3
    connectors = -2
    active_effect = -1
    inactive = 0
    small_overlays = 1
    key_overlays = 2
    socket_overlays = 2
    active_connectors = 4
    active = 5
    jewels = 6


class ColourCodes(enum.Enum):
    NORMAL = "#F0F0F0"
    ADJUDICATOR = "#E9F831"
    AQUA = "#00FFFF"
    BASILISK = "#00CB3A"
    BLACK = "#000000"
    BLUE = "#0000FF"
    BRITTLEBG = "#00122B"
    CHAOS = "#D02090"
    CHILLBG = "#151E26"
    CLEANSING = "#F24141"
    COLD = "#3F6DB3"
    CRAFTED = "#B8DAF1"
    CRUCIBLE = "#FFA500"
    CRUSADER = "#2946FC"
    CURRENCY = "#AA9E82"
    CUSTOM = "#5CF0BB"
    DARKGRAY = "#696969"
    DEFENCE = "#8080E0"
    DUELIST = "#E0E070"
    ELDER = "#AA77CC"
    EYRIE = "#AAB7B8"
    FIRE = "#B97123"
    FRACTURED = "#A29160"
    FREEZEBG = "#0C262B"
    GEM = "#1AA29B"
    GOLD = "#FFD700"
    GRAY = "#D3D3D3"
    GREEN = "#00FF00"
    LIGHTGRAY = "#808B96"
    LIGHTNING = "#ADAA47"
    MAGIC = "#8888FF"
    MAINHAND = "#50FF50"
    MARAUDER = "#E05030"
    NEGATIVE = "#FF0022"  # Better against black
    OFFENCE = "#E07030"
    OFFHAND = "#B7B7FF"
    POSITIVE = "#33FF77"
    PROPHECY = "#B54BFF"
    PURPLE = "#FF00FF"
    RANGER = "#70FF70"
    RARE = "#FFFF77"
    RED = "#FF0000"
    RELIC = "#60C060"
    SAPBG = "#261500"
    SCION = GEM
    SCORCHBG = "#270B00"
    SCOURGE = "#FF6E25"
    SHADOW = "#30C0D0"
    SHAPER = "#55BBFF"
    SHOCKBG = "#191732"
    SILVER = "#C0C0C0"
    SOURCE = "#88FFFF"
    TANGLE = "#038C8C"
    TEMPLAR = "#C040FF"
    TIP = "#80A080"
    UNIQUE = "#AF6025"
    UNSUPPORTED = "#F05050"
    WARNING = "#FF9922"
    WHITE = "#FFFFFF"
    WITCH = "#7070FF"
    YELLOW = "#FFFF00"
    A = GOLD
    B = WITCH
    DEX = RANGER
    DEXTERITY = RANGER
    ES = SOURCE
    EVASION = POSITIVE
    G = DEXTERITY
    INT = WITCH
    INTELLIGENCE = WITCH
    LIFE = MARAUDER
    MANA = WITCH
    NONE = NORMAL
    PHYS = NORMAL
    R = MARAUDER
    RAGE = WARNING
    STR = MARAUDER
    STRENGTH = MARAUDER
    W = WHITE
    WARD = RARE


@enum.unique
class PlayerClasses(enum.IntEnum):
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
        "x": -3700 / global_scale_factor,
        "y": 250 / global_scale_factor,
    },
    PlayerClasses.RANGER: {
        "n": "BackgroundDex",
        "x": 1550 / global_scale_factor,
        "y": 250 / global_scale_factor,
    },
    PlayerClasses.WITCH: {
        "n": "BackgroundInt",
        "x": -1200 / global_scale_factor,
        "y": -3550 / global_scale_factor,
    },
    PlayerClasses.DUELIST: {
        "n": "BackgroundStrDex",
        "x": -1900 / global_scale_factor,
        "y": 1350 / global_scale_factor,
    },
    PlayerClasses.TEMPLAR: {
        "n": "BackgroundStrInt",
        "x": -3250 / global_scale_factor,
        "y": -2800 / global_scale_factor,
    },
    PlayerClasses.SHADOW: {
        "n": "BackgroundDexInt",
        "x": 1250 / global_scale_factor,
        "y": -3450 / global_scale_factor,
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
    "Chieftain": {"x": -10400 / global_scale_factor, "y": 2200 / global_scale_factor},
    "Chieftain_g3": {
        "x": -10580 / global_scale_factor,
        "y": 2507 / global_scale_factor,
    },
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

bandits = {
    "None": {"name": "Kill All", "tooltip": "2 Passives Points"},
    "Oak": {
        "name": "Oak (Life Regen, Phys.Dmg. Reduction, Phys.Dmg)",
        "tooltip": "Regenerate 1% of Life per second\n" "2% additional Physical Damage Reduction\n" "20% increased Physical Damage",
    },
    "Kraityn": {
        "name": "Kraityn (Attack/Cast Speed, Avoid Elemental Ailments, Move Speed)",
        "tooltip": "6% increased Attack and Cast Speed\n" "10% chance to avoid Elemental Ailments\n" "6% increased Movement Speed",
    },
    "Alira": {
        "name": "Alira (Mana Regen, Crit Multiplier, Resists)",
        "tooltip": "Regenerate 5 Mana per second\n" "+20% to Critical Strike Multiplier\n" "+15% to all Elemental Resistances",
    },
}


@enum.unique
class PlayerAscendancy(enum.Enum):
    NONE = None


# ToDo: Need to use the flag attribute to separate stats like Speed. Should we have a list or dictionary as we have
# fmt: off
player_stats_list = {
    "ActiveMinionLimit": {"label": "Active Minion Limit", "fmt": "%d"},
    "AverageHit": {"label": "Average Hit", "fmt": "%0.1f"},
    "PvpAverageHit": {"label": "PvP Average Hit", "fmt": "%0.1f"},
    "AverageDamage": {
        "attack": {"label": "Average Damage", "fmt": "%0.1f", "flag": "attack"},
        "monsterExplode": {"label": "Average Damage", "fmt": "%0.1f", "flag": "monsterExplode"},
        },
    "AverageBurstDamage": {"label": "Average Burst Damage", "fmt": "%0.1f"},
    "PvpAverageDamage": {"label": "PvP Average Damage", "fmt": "%0.1f", "flag": "attackPvP"},
    "Speed": {
        "attack": {"label": "Attack Rate", "fmt": "%0.2f", "flag": "attack"},
        "spell": {"label": "Cast Rate", "fmt": "%0.2f", "flag": "spell"},
        "": {"label": "Effective Trigger Rate", "fmt": "%0.2f"},
        },
    "WarcryCastTime": {"label": "Cast Time", "fmt": "%0.2fs", "flag": "warcry"},
    "HitSpeed": {"label": "Hit Rate", "fmt": "%0.2f"},
    "HitTime": {"label": "Channel Time", "fmt": "%0.2fs", "flag": "channelRelease"},
    "ChannelTimeToTrigger": {"label": "Channel Time", "fmt": "%0.2fs"},
    "TrapThrowingTime": {"label": "Trap Throwing Time", "fmt": "%0.2fs"},
    "TrapCooldown": {"label": "Trap Cooldown", "fmt": "%0.3fs"},
    "MineLayingTime": {"label": "Mine Throwing Time", "fmt": "%0.2fs"},
    "TotemPlacementTime": {"label": "Totem Placement Time", "fmt": "%0.2fs"},
    "PreEffectiveCritChance": {"label": "Crit Chance", "fmt": "%0.2f%%"},
    "CritChance": {"label": "Effective Crit Chance", "fmt": "%0.2f%%"},
    "CritMultiplier": {"label": "Crit Multiplier", "fmt": "%d"},
    "HitChance": {
        "attack": {"label": "Hit Chance", "fmt": "%0.0f%%", "flag": "attack"},
        "enemyHasSpellBlock": {"label": "Hit Chance", "fmt": "%0.0f%%", "flag": "enemyHasSpellBlock"},
        },
    "TotalDPS": {
        "notAverage": {"label": "Total DPS", "fmt": "%0.1f", "flag": "notAverage"},
        "showAverage": {"stat": "TotalDPS", "label": "Total DPS", "fmt": "%0.1f", "flag": "showAverage"},
        },
    "PvpTotalDPS": {"label": "PvP Hit DPS", "fmt": "%0.1f", "flag": "notAveragePvP"},
    "TotalDot": {"label": "DoT DPS", "fmt": "%0.1f"},
    "WithDotDPS": {"label": "Total DPS inc. DoT", "fmt": "%0.1f", "flag": "notAverage"},
    "BleedDPS": {"label": "Bleed DPS", "fmt": "%0.1f"},
    "CorruptingBloodDPS": {"label": "Corrupting Blood DPS", "fmt": "%0.1f"},
    "BleedDamage": {"label": "Total Damage per Bleed", "fmt": "%0.1f", "flag": "showAverage"},
    "WithBleedDPS": {"label": "Total DPS inc. Bleed", "fmt": "%0.2f"},
    "IgniteDPS": {"label": "Ignite DPS", "fmt": "%0.1f"},
    "IgniteDamage": {"label": "Total Damage per Ignite", "fmt": "%0.1f", "flag": "showAverage"},
    "BurningGroundDPS": {"label": "Burning Ground DPS", "fmt": "%0.1f"},
    "WithIgniteDPS": {"label": "Total DPS inc. Ignite", "fmt": "%0.2f", "flag": "notAverage"},
    "WithIgniteAverageDamage": {"label": "Average Dmg. inc. Ignite", "fmt": "%0.1f"},
    "PoisonDPS": {"label": "Poison DPS", "fmt": "%0.1f"},
    "CausticGroundDPS": {"label": "Caustic Ground DPS", "fmt": "%0.1f"},
    "PoisonDamage": {"label": "Total Damage per Poison", "fmt": "%0.1f"},
    "WithPoisonDPS": {"label": "Total DPS inc. Poison", "fmt": "%.2f"},
    "DecayDPS": {"label": "Decay DPS", "fmt": "%0.1f"},
    "TotalDotDPS": {"label": "Total DoT DPS", "fmt": "%0.2f"},
    "ImpaleDPS": {
        "showAverage": {"label": "Impale Damage", "fmt": "%0.1f", "flag": ["impale", "showAverage"]},
        "notAverage": {"label": "Impale DPS", "fmt": "%0.1f", "flag": ["impale", "notAverage"],
        },
    },
    "WithImpaleDPS": {
        "showAverage": {"label": "Damage inc. Impale", "fmt": "%0.1f", "flag": ["impale", "showAverage"]},
        "notAverage": {"label": "Total DPS inc. Impale", "fmt": "%0.1f", "flag": ["impale", "notAverage"]},
    },
    "MirageDPS": {"label": "Total Mirage DPS", "fmt": "%0.1f"},
    "CullingDPS": {"label": "Culling DPS", "fmt": "%0.1f"},
    "ReservationDPS": {"label": "Reservation DPS", "fmt": "%0.1f"},
    "CombinedDPS": {"label": "Combined DPS", "fmt": "%0.1f"},
    "CombinedAvg": {"label": "Combined Total Damage", "fmt": "%0.1f", "flag": "showAverage"},
    "ExplodeChance": {"label": "Total Explode Chance", "fmt": "%0.0fs"},
    "CombinedAvgToMonsterLife": {"label": "Enemy Life Equivalent", "fmt": "%0.1fs"},
    "Cooldown": {"label": "Skill Cooldown", "fmt": "%0.3fs"},
    "SealCooldown": {"label": "Seal Gain Frequency", "fmt": "%0.2fs"},
    "SealMax": {"label": "Max Number of Seals", "fmt": "%d"},
    "TimeMaxSeals": {"label": "Time to Gain Max Seals", "fmt": "%0.2fs"},
    "AreaOfEffectRadiusMetres": {"label": "AoE Radius", "fmt": "%0.2fm"},
    "BrandAttachmentRange": {"label": "Attachment Range", "fmt": "%d", "flag": "brand"},
    "BrandTicks": {"label": "Activations per Brand", "fmt": "%d", "flag": "brand"},
    "ManaCost": {"label": "Mana Cost", "colour": ColourCodes.MANA.value, "fmt": "%d"},
    "ManaPercentCost": {"label": "Mana Cost", "colour": ColourCodes.MANA.value, "fmt": "d%%"},
    "ManaPerSecondCost": {"label": "Mana Cost", "colour": ColourCodes.MANA.value, "fmt": "%0.2f/s"},
    "ManaPercentPerSecondCost": {"label": "Mana Cost", "colour": ColourCodes.MANA.value, "fmt": "%0.2f%%/s"},
    "LifeCost": {"label": "Life Cost", "colour": ColourCodes.LIFE.value, "fmt": "%d"},
    "LifePercentCost": {"label": "Life Cost", "colour": ColourCodes.LIFE.value, "fmt": "%d%%"},
    "LifePerSecondCost": {"label": "Life Cost", "colour": ColourCodes.LIFE.value, "fmt": "%0.2f/s"},
    "LifePercentPerSecondCost": {"label": "Life Cost", "colour": ColourCodes.LIFE.value, "fmt": "%0.2f%%/s"},
    "ESCost": {"label": "Energy Shield Cost", "colour": ColourCodes.ES.value, "fmt": "%0.2f"},
    "ESPerSecondCost": {"label": "Energy Shield Cost", "fmt": "%0.2f/s", "colour": ColourCodes.ES.value},
    "ESPercentPerSecondCost": {"label": "Energy Shield Cost", "fmt": "%0.2f%%/s", "colour": ColourCodes.ES.value},
    "RageCost": {"label": "Rage Cost", "colour": ColourCodes.RAGE.value, "fmt": "%d"},
    "RagePerSecondCost": {"label": "Rage Cost per second", "colour": ColourCodes.RAGE.value, "fmt": "%0.2f/s"},
    "SoulCost": {"label": "Soul Cost", "colour": ColourCodes.RAGE.value, "fmt": "%d"},
    "blanka": {},
    "Str": {"label": "Strength", "colour": ColourCodes.STRENGTH.value, "fmt": "%d"},
    "ReqStr": {"label": "Strength Required", "colour": ColourCodes.STRENGTH.value, "fmt": "%d"},
    "Dex": {"label": "Dexterity", "colour": ColourCodes.DEXTERITY.value, "fmt": "%d"},
    "ReqDex": {"label": "Dexterity Required", "colour": ColourCodes.DEXTERITY.value, "fmt": "%d"},
    "Int": {"label": "Intelligence", "colour": ColourCodes.INTELLIGENCE.value, "fmt": "%d"},
    "ReqInt": {"label": "Intelligence Required", "colour": ColourCodes.INTELLIGENCE.value, "fmt": "%d"},
    "Omni": {"label": "Omniscience", "colour": ColourCodes.RARE.value, "fmt": "%d"},
    "ReqOmni": {"label": "Omniscience Required", "colour": ColourCodes.RARE.value, "fmt": "%d"},
    "blankb": {},
    "Devotion": {"label": "Devotion", "colour": ColourCodes.RARE.value, "fmt": "%d"},
    "blankc": {},
    "TotalEHP": {"label": "Effective Hit Pool", "fmt": "%0.0f"},
    "PvPTotalTakenHit": {"label": "PvP Hit Taken", "fmt": "%0.1f"},
    "PhysicalMaximumHitTaken": {"label": "Phys Max Hit", "fmt": "%0.0f"},
    "LightningMaximumHitTaken": {"label": "Elemental Max Hit", "fmt": "%0.0f"},
    "FireMaximumHitTaken": {"label": "Fire Max Hit", "fmt": "%0.0f"},
    "ColdMaximumHitTaken": {"label": "Cold Max Hit", "fmt": "%0.0f"},
    "LightningMaximumHitTaken": {"label": "Lightning Max Hit", "fmt": "%0.0f"},
    "ChaosMaximumHitTaken": {"label": "Chaos Max Hit", "fmt": "%0.0f"},
    "blankd": {},
    # "MainHand": {"label": "Total Life", "childStat": "Accuracy", "fmt": "%d", "colour": ColourCodes.LIFE.value},
    # "OffHand": {"label": "Total Life", "childStat": "Accuracy", "fmt": "%d", "colour": ColourCodes.LIFE.value},
    "Life": {"label": "Total Life", "fmt": "%d", "colour": ColourCodes.LIFE.value},
    "Spec:LifeInc": {"label": "%Inc Life from Tree", "fmt": "%d%%", "colour": ColourCodes.LIFE.value},
    "LifeUnreserved": {"label": "Unreserved Life", "fmt": "%d", "colour": ColourCodes.LIFE.value},
    "LifeRecoverable": {"label": "Life Recoverable", "fmt": "%d", "colour": ColourCodes.LIFE.value},
    "LifeUnreservedPercent": {"label": "Unreserved Life", "fmt": "%d%%", "colour": ColourCodes.LIFE.value},
    # This may need looking into. in lua, two stats separated by cond function.Mana and ES have these two
    "LifeRegenRecovery": {"label": "Life Regen", "alt_label": "Life Recovery", "fmt": "%0.1f", "colour": ColourCodes.LIFE.value},
    "LifeLeechGainRate": {"label": "Life Leech/On Hit Rate", "fmt": "%0.1f", "colour": ColourCodes.LIFE.value},
    "LifeLeechGainPerHit": {"label": "Life Leech/Gain per Hit", "fmt": "%0.1f", "colour": ColourCodes.LIFE.value},
    "blanke": {},
    "Mana": {"label": "Total Mana", "fmt": "%d", "colour": ColourCodes.MANA.value},
    "Spec:ManaInc": {"label": "%Inc Mana from Tree", "fmt": "%d%%", "colour": ColourCodes.MANA.value},
    "ManaUnreserved": {"label": "Unreserved Mana", "fmt": "%d", "colour": ColourCodes.MANA.value},
    "ManaUnreservedPercent": {"label": "Unreserved Mana", "fmt": "%d%%", "colour": ColourCodes.MANA.value},
    "ManaRegenRecovery": {"label": "Mana Regen", "alt_label": "Life Recovery", "fmt": "%0.1f", "colour": ColourCodes.MANA.value},
    "ManaLeechGainRate": {"label": "Mana Leech/On Hit Rate", "fmt": "%0.1f", "colour": ColourCodes.MANA.value},
    "ManaLeechGainPerHit": {"label": "Mana Leech/Gain per Hit", "fmt": "%0.1f", "colour": ColourCodes.MANA.value},
    "blankf": {},
    "EnergyShield": {"label": "Total Energy Shield", "fmt": "%d", "colour": ColourCodes.ES.value},
    "EnergyShieldRecoveryCap": {"label": "Recoverable ES", "fmt": "%d", "colour": ColourCodes.ES.value},
    "Spec:EnergyShieldInc": {"label": "%Inc ES from Tree", "fmt": "%d%%", "colour": ColourCodes.ES.value},
    "EnergyShieldRegenRecovery": {"label": "Energy Shield Regen", "alt_label": "Energy Shield Recovery", "fmt": "%0.1f",
                                  "colour": ColourCodes.MANA.value},
    "EnergyShieldRegen": {"label": "Energy Shield Regen", "fmt": "%0.1f", "colour": ColourCodes.ES.value},
    "EnergyShieldLeechGainRate": {"label": "ES Leech/On Hit Rate", "fmt": "%0.1f", "colour": ColourCodes.ES.value},
    "EnergyShieldLeechGainPerHit": {"label": "ES Leech/Gain per Hit", "fmt": "%0.1f", "colour": ColourCodes.ES.value},
    "blankg": {},
    "Ward": {"label": "Ward", "fmt": "%d", "colour": ColourCodes.WARD.value},
    "blankh": {},
    "Rage": {"label": "Rage", "fmt": "%d", "colour": ColourCodes.RAGE.value},
    "RageRegenRecovery": {"label": "Rage Regen", "fmt": "%d", "colour": ColourCodes.RAGE.value},
    "blanki": {},
    "TotalDegen": {"label": "Total Degen", "fmt": "%0.1f"},
    "TotalNetRegen": {"label": "Total Net Regen", "fmt": "+%0.1f"},
    "NetLifeRegen": {"label": "Net Life Regen", "fmt": "+%0.1f", "colour": ColourCodes.LIFE.value},
    "NetManaRegen": {"label": "Net Mana Regen", "fmt": "+%0.1f", "colour": ColourCodes.MANA.value},
    "NetEnergyShieldRegen": {"label": "Net Energy Shield Regen", "fmt": "+%0.1f", "colour": ColourCodes.ES.value},
    "blankj": {},
    "Evasion": {"label": "Evasion rating", "fmt": "%d", "colour": ColourCodes.EVASION.value},
    "Spec:EvasionInc": {"label": "%Inc Evasion from Tree", "fmt": "%d%%", "colour": ColourCodes.EVASION.value},
    "EvadeChance": {"label": "Evade Chance", "fmt": "%d%%", "colour": ColourCodes.EVASION.value},
    "MeleeEvadeChance": {"label": "Melee Evade Chance", "fmt": "%d%%", "colour": ColourCodes.EVASION.value},
    "ProjectileEvadeChance": {"label": "Projectile Evade Chance", "fmt": "%d%%", "colour": ColourCodes.EVASION.value},
    "blankk": {},
    "Armour": {"label": "Armour", "fmt": "%d"},
    "Spec:ArmourInc": {"label": "%Inc Armour from Tree", "fmt": "%d%%"},
    "PhysicalDamageReduction": {"label": "Phys. Damage Reduction", "fmt": "%d%%"},
    "blankl": {},
    "BlockChance": {"label": "Block Chance", "fmt": "%d%%"},
    "SpellBlockChance": {"label": "Spell Block Chance", "fmt": "%d%%"},
    "AttackDodgeChance": {"label": "Attack Dodge Chance", "fmt": "%d%%"},
    "SpellDodgeChance": {"label": "Spell Dodge Chance", "fmt": "%d%%"},
    "EffectiveSpellSuppressionChance": {"label": "Spell Suppression Chance", "fmt": "%d%%"},
    "blankm": {},
    "FireResist": {"label": "Fire Resistance", "fmt": "%d%%", "colour": ColourCodes.FIRE.value},
    "FireResistOverCap": {"label": "Fire Res. Over Max", "fmt": "%d%%", "hideStat": "true"},
    "ColdResist": {"label": "Cold Resistance", "fmt": "%d%%", "colour": ColourCodes.COLD.value},
    "ColdResistOverCap": {"label": "Cold Res. Over Max", "fmt": "%d%%", "hideStat": "true"},
    "LightningResist": {"label": "Lightning Resistance", "fmt": "%d%%", "colour": ColourCodes.LIGHTNING.value},
    "LightningResistOverCap": {"label": "Lightning Res. Over Max", "fmt": "%d%%", "hideStat": "true"},
    "ChaosResist": {"label": "Chaos Resistance", "fmt": "%d%%", "colour": ColourCodes.CHAOS.value},
    "ChaosResistOverCap": {"label": "Chaos Res. Over Max", "fmt": "%d%%", "hideStat": "true"},
    "blankn": {},
    "EffectiveMovementSpeedMod": {"label": "Movement Speed Modifier", "fmt": "+%d%%"},
    "blanko": {},
    "FullDPS": {"label": "Full DPS", "fmt": "%0.1f", "colour": ColourCodes.CURRENCY.value},
    "FullDotDPS": {"label": "Full Dot DPS", "fmt": "%0.1f", "colour": ColourCodes.CURRENCY.value},
    "blankp": {},
    "SkillDPS": {"label": "Skill DPS", "fmt": "%0.1f"},
}
# fmt: on
# Stats that are included in the build xml but not shown on the left hand side of the PoB window.
extraSaveStats = [
    "PowerCharges",
    "PowerChargesMax",
    "FrenzyCharges",
    "FrenzyChargesMax",
    "EnduranceCharges",
    "EnduranceChargesMax",
    "ActiveTotemLimit",
    "ActiveMinionLimit",
]


get_http_headers = {"User-Agent": "Path of Building Community - Python", "Accept": ""}
post_http_headers = {
    "User-Agent": "Path of Building Community - Python",
    "Accept": "",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "text/html; charset=utf-8",
}

valid_websites = [
    "pastebin.com",
    "pastebinp.com",
    "pobb.in",
    "rentry.co",
    "poe.ninja/pob",
]
website_list = {
    "pobb.in": {
        "id": "POBBin",
        "downloadURL": "https://pobb.in/pob/CODE",
        "codeOut": "https://pobb.in/",
        "postUrl": "https://pobb.in/pob/",
        "postFields": "",
    },
    "pastebin.com": {
        "id": "Pastebin",
        "downloadURL": "https://pastebin.com/raw/CODE",
        "codeOut": "",
        "postUrl": "https://pastebin.com/api/api_post.php",
        # "postFields": "api_dev_key=c4757f22e50e65e21c53892fd8e0a9ff&api_paste_private=1&api_option=paste&api_paste_code=CODE",
        "api_dev_key": "c4757f22e50e65e21c53892fd8e0a9ff",
    },
    "poe.ninja": {
        "id": "PoeNinja",
        "downloadURL": "https://poe.ninja/pob/raw/CODE",
        "codeOut": "",
        "postUrl": "https://poe.ninja/pob/api/api_post.php",
        # "postUrl": "https://httpbin.org/post",
        "postFields": "api_paste_code=CODE",
    },
    "pastebinp.com": {
        "id": "PastebinProxy",
        "downloadURL": "https://pastebinp.com/raw/CODE",
    },
    "rentry.co": {
        "id": "Rentry",
        "downloadURL": "https://rentry.co/paste/CODE/raw",
    },
    "Error": {"note": "If you get here, it's broken"},
}

# names for importing from json converting to xml entry names
slot_map = {
    "Weapon": "Weapon 1",
    "Weapon1": "Weapon 1",
    "Offhand": "Weapon 2",
    "Weapon2": "Weapon 1 Swap",
    "Offhand2": "Weapon 2 Swap",
    "Helm": "Helmet",
    "Helmet": "Helmet",
    "BodyArmour": "Body Armour",
    "Body": "Body Armour",
    "Gloves": "Gloves",
    "Boots": "Boots",
    "Amulet": "Amulet",
    "Ring": "Ring 1",
    "Ring1": "Ring 1",
    "Ring2": "Ring 2",
    "Belt": "Belt",
    "Flask": "Flask 1",
    "Flask1": "Flask 1",
    "Flask2": "Flask 2",
    "Flask3": "Flask 3",
    "Flask4": "Flask 4",
    "Flask5": "Flask 5",
    "PassiveJewels": "PassiveJewels",
    "Abyssal1": "Abyssal #1",
    "Abyssal2": "Abyssal #2",
    "Abyssal3": "Abyssal #3",
    "Abyssal4": "Abyssal #4",
    "Trinket": "Trinket",
}

slot_names = {
    "Weapon1": "Weapon 1",
    "Weapon2": "Weapon 2",
    "Offhand1": "Weapon 1 Swap",
    "Offhand2": "Weapon 2 Swap",
    "Helm": "Helmet",
    "BodyArmour": "Body Armour",
    "Gloves": "Gloves",
    "Boots": "Boots",
    "Amulet": "Amulet",
    "Ring1": "Ring 1",
    "Ring2": "Ring 2",
    "Belt": "Belt",
    "Flask1": "Flask 1",
    "Flask2": "Flask 2",
    "Flask3": "Flask 3",
    "Flask4": "Flask 4",
    "Flask5": "Flask 5",
}

qss_template = """
    * {{
//        padding: 0;
//        margin: 0;
        border: none;
        border-style: none;
        border-image: unset;
        outline: none;
        background: {window_colour};
        color: {text_colour};
    }}
    ListBox,
    QListView,
    QAbstractItemView {{
        alternate-background-color: {alt_colour};
    }}
    
    /* Put a box around control */
    ListBox:hover,
    QListWidget:hover,
    QCheckBox:hover,
    QRadioButton:hover,
    QComboBox:hover,
    QPushButton:hover,
    QAbstractSpinBox:hover,
    QLineEdit:hover,
    QTextEdit:hover,
    QPlainTextEdit:hover,
    QAbstractView:hover,
    QTabBar::tab:hover,
    QSpinBox::up-button:hover,
    QSpinBox::down-button:hover
    {{
        border: 1px solid {text_colour};
    }}
    /* Show disabled as dimmer */
    *:disabled
    {{
        color: grey;
    }}
    """
