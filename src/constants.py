"""Enumeration Data for Path of Exile constants."""

import enum

program_title = "Path of Building"

"""global_scale_factor
this is used to divide all x and y data coming in from the tree.json, but not Height and Width.
without this, items are too far apart and items are far too small on screen.
All values should only be scaled on point of entry, ie: when they are first processed out of the json
"""
global_scale_factor = 2.5
pob_debug = True

_VERSION_str = "3_21"
tree_versions = {
    "3_18": "3.18",
    "3_19": "3.19",
    "3_20": "3.20",
    "3_21": "3.21",
    "3_22": "3.22",
}
_VERSION = tree_versions[_VERSION_str]

http_headers = {"User-Agent": "Path of Building Community - Python", "Accept": ""}

# Default config incase the settings file doesn't exist
default_config = '<PathOfBuilding>\
    <Misc theme="Dark" slotOnlyTooltips="true" showTitlebarName="true" showWarnings="true" defaultCharLevel="1"\
        nodePowerTheme="0" connectionProtocol="0" thousandsSeparator="" decimalSeparator=""\
        showThousandsSeparators="true" betaTest="false" defaultGemQuality="0" buildSortMode="NAME"\
        proxyURL="" buildPath="" />\
    <recentBuilds/>\
    <size width="800" height="600"/>\
    </PathOfBuilding>'

default_spec = f'\
    <Spec title="Default" classId="0" ascendClassId="0" masteryEffects="" nodes="58833" treeVersion="{_VERSION_str}">\
    </Spec>'

# default_view_mode = "ITEMS"
default_view_mode = "TREE"
empty_build = f'<PathOfBuilding>\
    <Build level="1" targetVersion="3_0" bandit="None" className="Scion" ascendClassName="None"\
     mainSocketGroup="1" viewMode="{default_view_mode}" pantheonMajorGod="None" pantheonMinorGod="None"></Build>\
    <Import/>\
    <Calcs/>\
    <Skills sortGemsByDPSField="CombinedDPS" matchGemLevelToCharacterLevel="false" activeSkillSet="1"\
               sortGemsByDPS="true" defaultGemQuality="0" defaultGemLevel="normalMaximum" showSupportGemTypes="ALL"\
               showAltQualityGems="false">\
        <SkillSet id="0" title="Default">\
            <Skill mainActiveSkillCalcs="1" includeInFullDPS="false" label="" \
            enabled="true" slot="" mainActiveSkill="1">\
            </Skill>\
        </SkillSet>\
    </Skills>\
    <Items activeItemSet="1">\
        <ItemSet useSecondWeaponSet="false" id="1"/>\
    </Items>\
    <Tree activeSpec="1">\
        {default_spec}\
    </Tree>\
    <Notes/>\
    <NotesHTML/>\
    <TreeView searchStr="" zoomY="0" showHeatMap="nil" zoomLevel="3" showStatDifferences="true" zoomX="0"/>\
    <Config>\
        <Input name="resistancePenalty" number="0"/>\
        <Input name="pantheonMinorGod" string="None"/>\
        <Input name="enemyIsBoss" string="None"/>\
        <Input name="pantheonMajorGod" string="None"/>\
        <Input name="bandit" string="None"/>\
    </Config>\
</PathOfBuilding>'

empty_socket_group = '<Skill mainActiveSkillCalcs="1" includeInFullDPS="false" label="" \
    enabled="true" slot="" mainActiveSkill="1"/>'

empty_gem = '<Gem enableGlobal2="false" level="1" enableGlobal1="true" skillId="" qualityId="Default"\
    gemId="" enabled="true" quality="0" count="1" nameSpec=""/>'

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
        "tooltip": "50% less Duration of Poisons on you\n"
        "You cannot be Poisoned while there are at least 3 Poisons on you",
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
    active_connectors = 4
    active = 5


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
    OFFHAND = "#B7B7FF"
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
    LIGHTGRAY = "#808B96"
    DARKGRAY = "#696969"
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
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    YELLOW = "#FFFF00"
    PURPLE = "#FF00FF"
    AQUA = "#00FFFF"
    WHITE = "#FFFFFF"
    R = STRENGTH
    B = INTELLIGENCE
    G = DEXTERITY
    A = "#FFD700"  # Gold
    W = WHITE
    STR = STRENGTH
    INT = INTELLIGENCE
    DEX = DEXTERITY


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
        "tooltip": "Regenerate 1% of Life per second\n"
        "2% additional Physical Damage Reduction\n"
        "20% increased Physical Damage",
    },
    "Kraityn": {
        "name": "Kraityn (Attack/Cast Speed, Avoid Elemental Ailments, Move Speed)",
        "tooltip": "6% increased Attack and Cast Speed\n"
        "10% chance to avoid Elemental Ailments\n"
        "6% increased Movement Speed",
    },
    "Alira": {
        "name": "Alira (Mana Regen, Crit Multiplier, Resists)",
        "tooltip": "Regenerate 5 Mana per second\n"
        "+20% to Critical Strike Multiplier\n"
        "+15% to all Elemental Resistances",
    },
}


@enum.unique
class PlayerAscendancy(enum.Enum):
    NONE = None


stats_list = [
    {
        "stat": "ActiveMinionLimit",
        "label": "Active Minion Limit",
        "fmt": "{:d}",
    },
    {"stat": "AverageHit", "label": "Average Damage", "fmt": "{0:.2f}"},
    {
        "stat": "AverageDamage",
        "label": "Average Damage",
        "fmt": "{:.1f}",
        "flag": "attack",
    },
    {
        "stat": "ServerTriggerRate",
        "label": "Trigger Rate",
        "fmt": "{:.2f}",
    },
    {
        "stat": "Speed",
        "label": "Attack Rate",
        "fmt": "{0:.2f}",
        "flag": "attack",
    },
    {"stat": "Speed", "label": "Cast Rate", "fmt": "{0:.2f}", "flag": "spell"},
    {"stat": "Speed", "label": "Effective Trigger Rate", "fmt": "{:.2f}"},
    {
        "stat": "WarcryCastTime",
        "label": "Cast Time",
        "fmt": "{:.2f}s",
        "flag": "warcry",
    },
    {"stat": "HitSpeed", "label": "Hit Rate", "fmt": "{:.2f}"},
    {
        "stat": "TrapThrowingTime",
        "label": "Trap Throwing Time",
        "fmt": "{:.2f}s",
    },
    {
        "stat": "TrapCooldown",
        "label": "Trap Cooldown",
        "fmt": "{:.2f}s",
    },
    {
        "stat": "MineLayingTime",
        "label": "Mine Throwing Time",
        "fmt": "{:.2f}s",
    },
    {
        "stat": "TotemPlacementTime",
        "label": "Totem Placement Time",
        "fmt": "{:.2f}s",
    },
    {
        "stat": "PreEffectiveCritChance",
        "label": "Crit Chance",
        "fmt": "{0:.2g}%",
    },
    {
        "stat": "CritChance",
        "label": "Effective Crit Chance",
        "fmt": "{0:.2g}%",
    },
    {
        "stat": "CritMultiplier",
        "label": "Crit Multiplier",
        "fmt": "{0:.2f}",
    },
    {
        "stat": "HitChance",
        "label": "Hit Chance",
        "fmt": "{:.0f}%",
        "flag": "attack",
    },
    {
        "stat": "TotalDPS",
        "label": "Total DPS",
        "fmt": "{:.1f}",
        "flag": "notAverage",
    },
    {
        "stat": "TotalDPS",
        "label": "Total DPS",
        "fmt": "{:.1f}",
        "flag": "showAverage",
    },
    {
        "stat": "TotalDot",
        "label": "DoT DPS",
        "fmt": "{:.1f}",
    },
    {
        "stat": "WithDotDPS",
        "label": "Total DPS inc. DoT",
        "fmt": "{:.1f}",
        "flag": "notAverage",
    },
    {
        "stat": "BleedDPS",
        "label": "Bleed DPS",
        "fmt": "{:.1f}",
    },
    {
        "stat": "BleedDamage",
        "label": "Total Damage per Bleed",
        "fmt": "{:.1f}",
        "flag": "showAverage",
    },
    {
        "stat": "WithBleedDPS",
        "label": "Total DPS inc. Bleed",
        "fmt": "{0:.2f}",
    },
    {
        "stat": "IgniteDPS",
        "label": "Ignite DPS",
        "fmt": "{:.1f}",
    },
    {
        "stat": "IgniteDamage",
        "label": "Total Damage per Ignite",
        "fmt": "{:.1f}",
        "flag": "showAverage",
    },
    {
        "stat": "WithIgniteDPS",
        "label": "Total DPS inc. Ignite",
        "fmt": "{0:.2f}",
    },
    {
        "stat": "WithIgniteAverageDamage",
        "label": "Average Dmg. inc. Ignite",
        "fmt": "{:.1f}",
    },
    {
        "stat": "PoisonDPS",
        "label": "Poison DPS",
        "fmt": "{:.1f}",
    },
    {
        "stat": "PoisonDamage",
        "label": "Total Damage per Poison",
        "fmt": "{:.1f}",
    },
    {
        "stat": "WithPoisonDPS",
        "label": "Total DPS inc. Poison",
        "fmt": "{0:.2f}",
    },
    {
        "stat": "DecayDPS",
        "label": "Decay DPS",
        "fmt": "{:.1f}",
    },
    {
        "stat": "TotalDotDPS",
        "label": "Total DPS inc. DoT",
        "fmt": "{0:.2f}",
    },
    {
        "stat": "ImpaleDPS",
        "label": "Impale Damage",
        "fmt": "{:.1f}",
        "flag": ["impale", "showAverage"],
    },
    {
        "stat": "WithImpaleDPS",
        "label": "Damage inc. Impale",
        "fmt": "{:.1f}",
        "flag": ["impale", "showAverage"],
    },
    {
        "stat": "ImpaleDPS",
        "label": "Impale DPS",
        "fmt": "{:.1f}",
        "flag": ["impale", "notAverage"],
    },
    {
        "stat": "WithImpaleDPS",
        "label": "Total DPS inc. Impale",
        "fmt": "{:.1f}",
        "flag": ["impale", "notAverage"],
    },
    {"stat": "MirageDPS", "label": "Total Mirage DPS", "fmt": "{:.1f}"},
    {"stat": "CullingDPS", "label": "Culling DPS", "fmt": "{0:.2f}"},
    {"stat": "CombinedDPS", "label": "Combined DPS", "fmt": "{0:.2f}"},
    {
        "stat": "CombinedAvg",
        "label": "Combined Total Damage",
        "fmt": "{:.1f}",
        "flag": "showAverage",
    },
    {
        "stat": "Cooldown",
        "label": "Skill Cooldown",
        "fmt": "{:.2f}s",
    },
    {
        "stat": "SealCooldown",
        "label": "Seal Gain Frequency",
        "fmt": "{:.2f}s",
    },
    {"stat": "SealMax", "label": "Max Number of Seals", "fmt": "{:d}"},
    {
        "stat": "TimeMaxSeals",
        "label": "Time to Gain Max Seals",
        "fmt": "{:.2f}s",
    },
    {
        "stat": "AreaOfEffectRadius",
        "label": "AoE Radius",
        "fmt": "{0:.2f}",
    },
    {
        "stat": "BrandAttachmentRange",
        "label": "Attachment Range",
        "fmt": "{:d}",
        "flag": "brand",
    },
    {
        "stat": "BrandTicks",
        "label": "Activations per Brand",
        "fmt": "{:d}",
        "flag": "brand",
    },
    {
        "stat": "ManaCost",
        "label": "Mana Cost",
        "colour": ColourCodes.MANA,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "LifeCost",
        "label": "Life Cost",
        "colour": ColourCodes.LIFE,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "ESCost",
        "label": "Energy Shield Cost",
        "colour": ColourCodes.ES,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "RageCost",
        "label": "Rage Cost",
        "colour": ColourCodes.RAGE,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "ManaPercentCost",
        "label": "Mana Cost",
        "colour": ColourCodes.MANA,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "LifePercentCost",
        "label": "Life Cost",
        "colour": ColourCodes.LIFE,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "ManaPerSecondCost",
        "label": "Mana Cost",
        "colour": ColourCodes.MANA,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "LifePerSecondCost",
        "label": "Life Cost",
        "colour": ColourCodes.LIFE,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "ManaPercentPerSecondCost",
        "label": "Mana Cost",
        "colour": ColourCodes.MANA,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "LifePercentPerSecondCost",
        "label": "Life Cost",
        "colour": ColourCodes.LIFE,
        "fmt": "{0:.2f}",
    },
    {
        "stat": "ESPerSecondCost",
        "label": "Energy Shield Cost",
        "fmt": "{:.2f}/s",
        "colour": ColourCodes.ES,
    },
    {
        "stat": "ESPercentPerSecondCost",
        "label": "Energy Shield Cost",
        "fmt": "{:.2f}%/s",
        "colour": ColourCodes.ES,
    },
    {"stat": "blank"},
    {
        "stat": "Str",
        "label": "Strength",
        "colour": ColourCodes.STRENGTH,
        "fmt": "{:d}",
    },
    {
        "stat": "ReqStr",
        "label": "Strength Required",
        "colour": ColourCodes.STRENGTH,
        "fmt": "{:d}",
    },
    {
        "stat": "Dex",
        "label": "Dexterity",
        "colour": ColourCodes.DEXTERITY,
        "fmt": "{:d}",
    },
    {
        "stat": "ReqDex",
        "label": "Dexterity Required",
        "colour": ColourCodes.DEXTERITY,
        "fmt": "{:d}",
    },
    {
        "stat": "Int",
        "label": "Intelligence",
        "colour": ColourCodes.INTELLIGENCE,
        "fmt": "{:d}",
    },
    {
        "stat": "ReqInt",
        "label": "Intelligence Required",
        "colour": ColourCodes.INTELLIGENCE,
        "fmt": "{:d}",
    },
    {
        "stat": "Omni",
        "label": "Omniscience",
        "colour": ColourCodes.RARE,
        "fmt": "{:d}",
    },
    {
        "stat": "ReqOmni",
        "label": "Omniscience Required",
        "colour": ColourCodes.RARE,
        "fmt": "{:d}",
    },
    {"stat": "blank"},
    {
        "stat": "Devotion",
        "label": "Devotion",
        "colour": ColourCodes.RARE,
        "fmt": "{:d}",
    },
    {"stat": "blank"},
    {
        "stat": "TotalEHP",
        "label": "Effective Hit Pool",
        "fmt": "{:.0f}",
    },
    {
        "stat": "SecondMinimalMaximumHitTaken",
        "label": "Eff. Maximum Hit Taken",
        "fmt": "{:.0f}",
    },
    {"stat": "blank"},
    {
        "stat": "Life",
        "label": "Total Life",
        "fmt": "{:d}",
        "colour": ColourCodes.LIFE,
    },
    {
        "stat": "Spec:LifeInc",
        "label": "%Inc Life from Tree",
        "fmt": "{:d}%",
        "colour": ColourCodes.LIFE,
    },
    {
        "stat": "LifeUnreserved",
        "label": "Unreserved Life",
        "fmt": "{:d}",
        "colour": ColourCodes.LIFE,
    },
    {
        "stat": "LifeUnreservedPercent",
        "label": "Unreserved Life",
        "fmt": "{:d}%",
        "colour": ColourCodes.LIFE,
    },
    {"label": "Life Regen", "fmt": "{:.1f}", "colour": ColourCodes.LIFE},
    {
        "stat": "LifeLeechGainRate",
        "label": "Life Leech/On Hit Rate",
        "fmt": "{:.1f}",
        "colour": ColourCodes.LIFE,
    },
    {
        "stat": "LifeLeechGainPerHit",
        "label": "Life Leech/Gain per Hit",
        "fmt": "{:.1f}",
        "colour": ColourCodes.LIFE,
    },
    {"stat": "blank"},
    {
        "stat": "TotalDegen",
        "label": "Total Degen",
        "fmt": "{:.1f}",
    },
    {
        "stat": "TotalNetRegen",
        "label": "Total Net Regen",
        "fmt": "+{:.1f}",
    },
    {
        "stat": "NetLifeRegen",
        "label": "Net Life Regen",
        "fmt": "+{:.1f}",
        "colour": ColourCodes.LIFE,
    },
    {
        "stat": "NetManaRegen",
        "label": "Net Mana Regen",
        "fmt": "+{:.1f}",
        "colour": ColourCodes.MANA,
    },
    {
        "stat": "NetEnergyShieldRegen",
        "label": "Net Energy Shield Regen",
        "fmt": "+{:.1f}",
        "colour": ColourCodes.ES,
    },
    {"stat": "blank"},
    {
        "stat": "Ward",
        "label": "Ward",
        "fmt": "{:d}",
        "colour": ColourCodes.WARD,
    },
    {
        "stat": "EnergyShield",
        "label": "Energy Shield",
        "fmt": "{:d}",
        "colour": ColourCodes.ES,
    },
    {
        "stat": "EnergyShieldRecoveryCap",
        "label": "Recoverable ES",
        "colour": ColourCodes.ES,
        "fmt": "{:d}",
    },
    {
        "stat": "Spec:EnergyShieldInc",
        "label": "%Inc ES from Tree",
        "colour": ColourCodes.ES,
        "fmt": "{:d}%",
    },
    {
        "stat": "EnergyShieldRegen",
        "label": "Energy Shield Regen",
        "colour": ColourCodes.ES,
        "fmt": "{:.1f}",
    },
    {
        "stat": "EnergyShieldLeechGainRate",
        "label": "ES Leech/On Hit Rate",
        "colour": ColourCodes.ES,
        "fmt": "{:.1f}",
    },
    {
        "stat": "EnergyShieldLeechGainPerHit",
        "label": "ES Leech/Gain per Hit",
        "colour": ColourCodes.ES,
        "fmt": "{:.1f}",
    },
    {"stat": "blank"},
    {
        "stat": "stat",
        "label": "Evasion rating",
        "fmt": "{:d}",
        "colour": ColourCodes.EVASION,
    },
    {
        "stat": "stat",
        "label": "%Inc Evasion from Tree",
        "colour": ColourCodes.EVASION,
        "fmt": "{:d}%",
    },
    {
        "stat": "EvadeChance",
        "label": "Evade Chance",
        "fmt": "{:d}%",
        "colour": ColourCodes.EVASION,
    },
    {
        "stat": "MeleeEvadeChance",
        "label": "Melee Evade Chance",
        "fmt": "{:d}%",
        "colour": ColourCodes.EVASION,
    },
    {
        "stat": "ProjectileEvadeChance",
        "label": "Projectile Evade Chance",
        "fmt": "{:d}%",
        "colour": ColourCodes.EVASION,
    },
    {"stat": "blank"},
    {
        "stat": "Armour",
        "label": "Armour",
        "fmt": "{:d}",
    },
    {
        "stat": "Spec:ArmourInc",
        "label": "%Inc Armour from Tree",
        "fmt": "{:d}%",
    },
    {
        "stat": "PhysicalDamageReduction",
        "label": "Phys. Damage Reduction",
        "fmt": "{:d}%",
    },
    {"stat": "blank"},
    {
        "stat": "EffectiveMovementSpeedMod",
        "label": "Movement Speed Modifier",
        "fmt": "{:.1f}%",
    },
    {
        "stat": "BlockChance",
        "label": "Block Chance",
        "fmt": "{:d}%",
    },
    {
        "stat": "SpellBlockChance",
        "label": "Spell Block Chance",
        "fmt": "{:d}%",
    },
    {
        "stat": "AttackDodgeChance",
        "label": "Attack Dodge Chance",
        "fmt": "{:d}%",
    },
    {
        "stat": "SpellDodgeChance",
        "label": "Spell Dodge Chance",
        "fmt": "{:d}%",
    },
    {
        "stat": "SpellSuppressionChance",
        "label": "Spell Suppression Chance",
        "fmt": "{:d}%",
    },
    {"stat": "blank"},
    {
        "stat": "FireResist",
        "label": "Fire Resistance",
        "fmt": "{:d}%",
        "colour": ColourCodes.FIRE,
    },
    {
        "stat": "FireResistOverCap",
        "label": "Fire Res. Over Max",
        "fmt": "{:d}%",
        "hideStat": "true",
    },
    {
        "stat": "ColdResist",
        "label": "Cold Resistance",
        "fmt": "{:d}%",
        "colour": ColourCodes.COLD,
    },
    {
        "stat": "ColdResistOverCap",
        "label": "Cold Res. Over Max",
        "fmt": "{:d}%",
        "hideStat": "true",
    },
    {
        "stat": "LightningResist",
        "label": "Lightning Resistance",
        "fmt": "{:d}%",
        "colour": ColourCodes.LIGHTNING,
    },
    {
        "stat": "LightningResistOverCap",
        "label": "Lightning Res. Over Max",
        "fmt": "{:d}%",
        "hideStat": "true",
    },
    {
        "stat": "ChaosResist",
        "label": "Chaos Resistance",
        "fmt": "{:d}%",
        "colour": ColourCodes.CHAOS,
    },
    {
        "stat": "ChaosResistOverCap",
        "label": "Chaos Res. Over Max",
        "fmt": "{:d}%",
        "hideStat": "true",
    },
]

valid_websites = [
    "pastebin.com",
    "pastebinp.com",
    "pobb.in",
    "rentry.co",
    "poe.ninja/pob",
]
website_list = {
    "pastebin.com": {
        "id": "Pastebin",
        "downloadURL": "https://pastebin.com/raw/CODE",
        "codeOut": "",
        "postUrl": "https://pastebin.com/api/api_post.php",
        "postFields": "api_dev_key=c4757f22e50e65e21c53892fd8e0a9ff&api_paste_private=1&api_option=paste&api_paste_code=",
    },
    "pastebinp.com": {
        "id": "PastebinProxy",
        "downloadURL": "https://pastebinp.com/raw/CODE",
    },
    "pobb.in": {
        "id": "POBBin",
        "downloadURL": "https://pobb.in/pob/CODE",
        "codeOut": "https://pobb.in/",
        "postUrl": "https://pobb.in/pob/",
        "postFields": "",
    },
    "rentry.co": {
        "id": "Rentry",
        "downloadURL": "https://rentry.co/paste/CODE/raw",
    },
    "poe.ninja": {
        "id": "PoeNinja",
        "downloadURL": "https://poe.ninja/pob/raw/CODE",
        "codeOut": "",
        "postUrl": "https://poe.ninja/pob/api/api_post.php",
        "postFields": "api_paste_code=",
    },
    "Error": {"note": "If you get here, it's broken"},
}

# names for importing from json converting to xml entry names
slot_map = {
    "Weapon": "Weapon 1",
    "Weapon2": "Weapon 2",
    "Offhand": "Weapon 1 Swap",
    "Offhand2": "Weapon 2 Swap",
    "Helm": "Helmet",
    "BodyArmour": "Body Armour",
    "Gloves": "Gloves",
    "Boots": "Boots",
    "Amulet": "Amulet",
    "Ring": "Ring 1",
    "Ring2": "Ring 2",
    "Belt": "Belt",
    "Flask": "Flask",
    "PassiveJewels": "PassiveJewels",
    "Weapon1": "Weapon 1",
    "Offhand1": "Weapon 1 Swap",
    "Ring1": "Ring 1",
    "Flask1": "Flask 1",
    "Flask2": "Flask 2",
    "Flask3": "Flask 3",
    "Flask4": "Flask 4",
    "Flask5": "Flask 5",
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
