"""
This Class manages all the elements and owns some elements of the "ITEMS" tab
"""

from qdarktheme.qtpy.QtCore import (
    QCoreApplication,
    QDir,
    QRect,
    QRectF,
    QSize,
    Qt,
    Signal,
    Slot,
)
from qdarktheme.qtpy.QtGui import (
    QAction,
    QActionGroup,
    QFont,
    QIcon,
    QPixmap,
    QBrush,
    QColor,
    QPainter,
    QStandardItemModel,
    QStandardItem,
)
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from typing import Union
import xml.etree.ElementTree as ET
import re
import ast

from PoB_Main_Window import Ui_MainWindow
from pob_config import Config, _debug, index_exists, str_to_bool, bool_to_str, print_call_stack
from constants import _VERSION, slot_map, ColourCodes

influence_colours = {
    "Shaper Item": ColourCodes.SHAPER.value,
    "Elder Item": ColourCodes.ELDER.value,
    "Warlord Item": ColourCodes.ADJUDICATOR.value,
    "Hunter Item": ColourCodes.BASILISK.value,
    "Crusader Item": ColourCodes.CRUSADER.value,
    "Redeemer Item": ColourCodes.EYRIE.value,
    "Searing Exarch": ColourCodes.CLEANSING.value,
    "Eater of Worlds": ColourCodes.TANGLE.value,
}

test = """			Rarity: UNIQUE
Bottled Faith
Sulphur Flask
League: Synthesis
Variant: Pre 3.15.0
Variant: Pre 3.16.0
Variant: Current
Selected Variant: 3
Sulphur Flask
Quality: 20
LevelReq: 35
Implicits: 3
{crafted}{range:1}(60-70)% increased effect
{crafted}Gains no Charges during Flask Effect
{variant:1}{range:0.5}(30-50)% increased Duration
Creates Consecrated Ground on Use
{variant:1}{range:0.5}(30-50)% increased Duration
{variant:2}{range:0.5}(20-40)% increased Duration
{variant:3}{range:0.22}(15-30)% reduced Duration
Consecrated Ground created by this Flask has Tripled Radius
{variant:1}{range:0.5}+(1.0-2.0)% to Critical Strike Chance against Enemies on Consecrated Ground during Effect
{variant:2,3}{range:0.878}(100-150)% increased Critical Strike Chance against Enemies on Consecrated Ground during Effect
{range:1}Consecrated Ground created during Effect applies (7-10)% increased Damage taken to Enemies
"""

fract = """           {"baseType": "Two-Stone Ring",
            "craftedMods": ["Non-Channelling Skills have -7 to Total Mana Cost",
             "+1 to Level of Socketed AoE Gems","9% increased Area of Effect"],
            "explicitMods": ["+32% to Fire Resistance",
                             "+32% to Cold Resistance",
                             "+28% to Chaos Resistance"],
            "fractured": "True",
            "fracturedMods": ["+53 to maximum Life"],
            "frameType": 2,
            "h": 1,
            "icon": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvUmluZ3MvVG9wYXpSdWJ5IiwidyI6MSwiaCI6MSwic2NhbGUiOjEsImZyYWN0dXJlZCI6dHJ1ZX1d/132743fd5f/TopazRuby.png",
            "id": "a56586f68e0ca5ea5126023ae0f87349e63a1d8d60b3ebb703d60bb0dc767916",
            "identified": "True",
            "ilvl": 69,
            "implicitMods": ["+16% to Fire and Lightning Resistances"],
            "influences": [
                "elder=true"
            ],
            "inventoryId": "Ring2",
            "league": "Standard",
            "name": "Glyph Finger",
            "requirements": [{"displayMode": 0,
                              "name": "Level",
                              "type": 62,
                              "values": [["64", 0]]}],
            "typeLine": "Two-Stone Ring",
            "verified": "False",
            "w": 1,
            "x": 0,
            "y": 0}"""

gloves = """{'verified': False, 'w': 2, 'h': 2, 'icon': 'GlovesStr4.png', 'league': 'Standard', 
 'id': '836a8d7a90033ae9b7f7363d438315b36dd57abf94875318aa746c93bdaa3cbf', 
 'sockets': [{'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, 
 {'group': 0, 'attr': 'S', 'sColour': 'R'},{'group': 0, 'attr': 'S', 'sColour': 'R'}],
 'name': 'Beast Fist', 'typeLine': 'Steel Gauntlets', 'baseType': 'Steel Gauntlets', 'identified': True, 'ilvl': 35,
 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Gloves',
 'enchantMods': ['Trigger Word of the Grave when your Skills or Minions Kill'], 
 'explicitMods': ['9% increased Armour', '11% increased Rarity of Items found', '+18% to Fire Resistance', 
 'Gain 2 Life per Enemy Hit with Attacks', '7% increased Stun and Block Recovery'],
 'properties': [{'name': 'Quality', 'values': [['+20%', 1]], 'displayMode': 0, 'type': 6},
 {'name': 'Armour', 'values': [['150', 1]], 'displayMode': 0, 'type': 16}],
 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'},
 {'name': 'Str', 'values': [['125', 0]], 'displayMode': 1, 'type': 63, 'suffix': '(gem)'},
 {'name': 'Int', 'values': [['38', 0]], 'displayMode': 1, 'type': 65, 'suffix': '(gem)'}],
 }
"""

items1 = {'items': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvUmluZ3MvVG9wYXpSdWJ5IiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/8878077651/TopazRuby.png', 'league': 'Standard', 'id': 'fa69af1ec517d3b0554cd5cfa2ba2fd360ec5b0fa703a209107d7978a7f711ca', 'name': 'Dire Grasp', 'typeLine': 'Two-Stone Ring', 'baseType': 'Two-Stone Ring', 'identified': True, 'ilvl': 82, 'requirements': [{'name': 'Level', 'values': [['57', 0]], 'displayMode': 0, 'type': 62}], 'implicitMods': ['+16% to Fire and Lightning Resistances'], 'explicitMods': ['+32 to Intelligence', '+124 to Evasion Rating', '+21 to maximum Mana', '0.4% of Chaos Damage Leeched as Life'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Ring2'}, {'verified': False, 'w': 2, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQXJtb3Vycy9HbG92ZXMvR2xvdmVzU3RyNCIsInciOjIsImgiOjIsInNjYWxlIjoxfV0/468f466568/GlovesStr4.png', 'league': 'Standard', 'id': '836a8d7a90033ae9b7f7363d438315b36dd57abf94875318aa746c93bdaa3cbf', 'sockets': [{'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}], 'name': 'Beast Fist', 'typeLine': 'Steel Gauntlets', 'baseType': 'Steel Gauntlets', 'identified': True, 'ilvl': 35, 'properties': [{'name': 'Quality', 'values': [['+20%', 1]], 'displayMode': 0, 'type': 6}, {'name': 'Armour', 'values': [['150', 1]], 'displayMode': 0, 'type': 16}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Str', 'values': [['125', 0]], 'displayMode': 1, 'type': 63, 'suffix': '(gem)'}, {'name': 'Int', 'values': [['38', 0]], 'displayMode': 1, 'type': 65, 'suffix': '(gem)'}], 'enchantMods': ['Trigger Word of the Grave when your Skills or Minions Kill'], 'explicitMods': ['9% increased Armour', '11% increased Rarity of Items found', '+18% to Fire Resistance', 'Gain 2 Life per Enemy Hit with Attacks', '7% increased Stun and Block Recovery'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Gloves', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0Nhc3RPbkRtZ1Rha2VuIiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/2f075f5964/CastOnDmgTaken.png', 'support': True, 'id': '46c7699ff09dc8bc298e8bac25570c32a8d7b7e6a27d96c25298b2e0c57de3ef', 'name': '', 'typeLine': 'Cast when Damage Taken Support', 'baseType': 'Cast when Damage Taken Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support, Spell, Trigger', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['9', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['250%', 0]], 'displayMode': 0}, {'name': 'Cooldown Time', 'values': [['0.25 sec', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['54', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['55', 0]], 'displayMode': 1, 'type': 63}, {'name': 'Int', 'values': [['38', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['384795/1956648', 0]], 'displayMode': 2, 'progress': 0.2, 'type': 20}], 'secDescrText': 'Each supported spell skill will track damage you take, and be triggered when the total damage taken reaches a threshold. Cannot support skills used by totems, traps, or mines. Vaal skills, channelling skills, and skills with a reservation cannot be triggered.', 'explicitMods': ['This Gem can only Support Skill Gems requiring Level 54 or lower', 'Supported Skills deal 49% less Damage', 'You cannot Cast Supported Triggerable Spells directly', 'Trigger Supported Spells when you take a total of 1221 Damage'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 0, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9Nb2x0ZW5TaGVsbCIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/9d2618a44a/MoltenShell.png', 'support': False, 'id': 'eeb0d354b620dbef839cc5e0f9e34616ad969d1e733a91f1b7fa6d796fd4f304', 'name': '', 'typeLine': 'Molten Shell', 'baseType': 'Molten Shell', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Spell, AoE, Duration, Fire, Physical, Guard', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['15', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost', 'values': [['11 Mana', 0]], 'displayMode': 0}, {'name': 'Cooldown Time', 'values': [['4.00 sec', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['Instant', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['55', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['123', 0]], 'displayMode': 1, 'type': 63}], 'additionalProperties': [{'name': 'Experience', 'values': [['3570338/7611351', 0]], 'displayMode': 2, 'progress': 0.47, 'type': 20}], 'secDescrText': 'Applies a buff that adds to your armour, and can take some of the damage from hits for you before being depleted. When the buff expires or is depleted, the skill deals reflected damage to enemies around you based on the total damage that was taken from the buff. Shares a cooldown with other Guard skills.', 'explicitMods': ['Base duration is 3.00 seconds', "This Skill's Cooldown does not recover during its effect", '75% of Damage from Hits is taken from the Buff before your Life or Energy Shield\nBuff can take Damage equal to 20% of your Armour, up to a maximum of 10000', 'Reflects 1820% of Damage taken from Buff as Fire Damage when Buff expires or is depleted', 'Buff grants +545 to Armour'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 1, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9EZXRlcm1pbmF0aW9uIiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/64c8ca9798/Determination.png', 'support': False, 'id': '5e9df624e79cd152b177cd4d9ae0269aafb92f9772634e2a3c4118e582746fd7', 'name': '', 'typeLine': 'Determination', 'baseType': 'Determination', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Aura, Spell, AoE, Physical', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['13', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Reservation', 'values': [['50% Mana', 0]], 'displayMode': 0}, {'name': 'Cooldown Time', 'values': [['1.20 sec', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['Instant', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['125', 0]], 'displayMode': 1, 'type': 63}], 'additionalProperties': [{'name': 'Experience', 'values': [['2927794/3655184', 0]], 'displayMode': 2, 'progress': 0.8, 'type': 20}], 'secDescrText': 'Casts an aura that grants armour to you and your allies.', 'explicitMods': ['+12 to radius', 'You and nearby allies gain 1019 additional Armour', 'You and nearby allies gain 46% more Armour'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 2, 'colour': 'S'}]}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvUmluZ3MvUmluZzUiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/6f90cd3c4b/Ring5.png', 'league': 'Standard', 'id': 'fdcc7f9d79206b7162bfb765cda2270949384dda3fad8f1fe767a572d423cea4', 'name': 'Phoenix Whorl', 'typeLine': 'Topaz Ring', 'baseType': 'Topaz Ring', 'identified': True, 'ilvl': 74, 'requirements': [{'name': 'Level', 'values': [['48', 0]], 'displayMode': 0, 'type': 62}], 'implicitMods': ['+20% to Lightning Resistance'], 'explicitMods': ['+31 to Evasion Rating', '+24 to maximum Energy Shield', 'Regenerate 47.5 Life per second', '0.4% of Chaos Damage Leeched as Life'], 'craftedMods': ['+27% to Cold Resistance'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Ring'}, {'verified': False, 'w': 1, 'h': 3, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvV2VhcG9ucy9PbmVIYW5kV2VhcG9ucy9PbmVIYW5kU3dvcmRzL09uZUhhbmRTd29yZDEiLCJ3IjoxLCJoIjozLCJzY2FsZSI6MX1d/ae6e9dda13/OneHandSword1.png', 'league': 'Standard', 'id': 'ab93454e680f67c960211da543db8612ef73f82fd75bccd3f33d8bdad98f8853', 'sockets': [{'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'D', 'sColour': 'G'}, {'group': 1, 'attr': 'D', 'sColour': 'G'}], 'name': '', 'typeLine': 'Rusted Sword', 'baseType': 'Rusted Sword', 'identified': True, 'ilvl': 3, 'properties': [{'name': 'One Handed Sword', 'values': [], 'displayMode': 0}, {'name': 'Physical Damage', 'values': [['4-9', 0]], 'displayMode': 0, 'type': 9}, {'name': 'Critical Strike Chance', 'values': [['5.00%', 0]], 'displayMode': 0, 'type': 12}, {'name': 'Attacks per Second', 'values': [['1.55', 0]], 'displayMode': 0, 'type': 13}, {'name': 'Weapon Range', 'values': [['11', 0]], 'displayMode': 0, 'type': 14}], 'requirements': [{'name': 'Level', 'values': [['50', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Dex', 'values': [['81', 0]], 'displayMode': 1, 'type': 64, 'suffix': '(gem)'}], 'implicitMods': ['40% increased Global Accuracy Rating'], 'frameType': 0, 'x': 0, 'y': 0, 'inventoryId': 'Offhand2', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0N1bGxpbmdTdHJpa2UiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/328a156075/CullingStrike.png', 'support': True, 'id': '323372e29db0d60a84a8b746adb1331b1bbdb4d0f039288c380b19c5e7112872', 'name': '', 'typeLine': 'Culling Strike Support', 'baseType': 'Culling Strike Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['11', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['110%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['50', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Dex', 'values': [['81', 0]], 'displayMode': 1, 'type': 64}], 'additionalProperties': [{'name': 'Experience', 'values': [['2151030/2151030', 0]], 'displayMode': 2, 'progress': 1, 'type': 20}], 'nextLevelRequirements': [{'name': 'Level', 'values': [['53', 0]], 'displayMode': 0}, {'name': 'Dex', 'values': [['85', 0]], 'displayMode': 1}], 'secDescrText': 'Supports any skill that hits enemies. If enemies are left below 10% of maximum life after being hit by these skills, they will be killed.', 'explicitMods': ['Kill Enemies that have 10% Life or lower when Hit by Supported Skills', 'Supported Skills deal 20% increased Damage'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 1, 'colour': 'D'}]}, {'verified': False, 'w': 1, 'h': 3, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvV2VhcG9ucy9PbmVIYW5kV2VhcG9ucy9PbmVIYW5kU3dvcmRzL09uZUhhbmRTd29yZDEiLCJ3IjoxLCJoIjozLCJzY2FsZSI6MX1d/ae6e9dda13/OneHandSword1.png', 'league': 'Standard', 'id': '26b7d3936176e81d3aacd8f53ca9cbf1982ca8ea22bf6b7076b243e1260b9bb3', 'sockets': [{'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 1, 'attr': 'D', 'sColour': 'G'}, {'group': 2, 'attr': 'I', 'sColour': 'B'}], 'name': '', 'typeLine': 'Rusted Sword', 'baseType': 'Rusted Sword', 'identified': True, 'ilvl': 1, 'properties': [{'name': 'One Handed Sword', 'values': [], 'displayMode': 0}, {'name': 'Physical Damage', 'values': [['4-9', 0]], 'displayMode': 0, 'type': 9}, {'name': 'Critical Strike Chance', 'values': [['5.00%', 0]], 'displayMode': 0, 'type': 12}, {'name': 'Attacks per Second', 'values': [['1.55', 0]], 'displayMode': 0, 'type': 13}, {'name': 'Weapon Range', 'values': [['11', 0]], 'displayMode': 0, 'type': 14}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Str', 'values': [['57', 0]], 'displayMode': 1, 'type': 63, 'suffix': '(gem)'}, {'name': 'Int', 'values': [['39', 0]], 'displayMode': 1, 'type': 65, 'suffix': '(gem)'}], 'implicitMods': ['40% increased Global Accuracy Rating'], 'frameType': 0, 'x': 0, 'y': 0, 'inventoryId': 'Weapon2', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0ZyYWdpbGl0eSIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/85392d054c/Fragility.png', 'support': True, 'id': 'c3062ae399d5ab17302e9b82a0d0975894fc3da48f0dfa5cf5d53db95bd53318', 'name': '', 'typeLine': 'Cruelty Support', 'baseType': 'Cruelty Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support, Duration', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['13', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['140%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['57', 0]], 'displayMode': 1, 'type': 63}, {'name': 'Int', 'values': [['39', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['3134556/3655184', 0]], 'displayMode': 2, 'progress': 0.86, 'type': 20}], 'secDescrText': 'Supports any skill that hits enemies. Minions cannot gain Cruelty.', 'explicitMods': ['Supported Skills deal 21% more Damage with Hits', 'Cruelty has a Base Duration of 4 seconds', 'Hits from Supported Skills grant Cruelty', '12% increased Effect of Cruelty granted by Supported Skills'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 0, 'colour': 'S'}]}, {'verified': False, 'w': 1, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzksMTQseyJmIjoiMkRJdGVtcy9GbGFza3MvbGlmZWZsYXNrOSIsInciOjEsImgiOjIsInNjYWxlIjoxLCJsZXZlbCI6MX1d/67262f06f5/lifeflask9.png', 'league': 'Standard', 'id': '4223ceafbafb8db611c39c11e27d6bcef94e5b59f227c798fe09f5d066078f2d', 'name': '', 'typeLine': 'Seething Hallowed Life Flask of Grounding', 'baseType': 'Hallowed Life Flask', 'identified': True, 'ilvl': 44, 'properties': [{'name': 'Recovers {0} Life over {1} Seconds', 'values': [['677', 1], ['4', 0]], 'displayMode': 3}, {'name': 'Consumes {0} of {1} Charges on use', 'values': [['10', 0], ['30', 0]], 'displayMode': 3}, {'name': 'Currently has {0} Charges', 'values': [['30', 0]], 'displayMode': 3}], 'requirements': [{'name': 'Level', 'values': [['42', 0]], 'displayMode': 0, 'type': 62}], 'explicitMods': ['66% reduced Amount Recovered', 'Instant Recovery', 'Grants Immunity to Shock for 11 seconds if used while Shocked'], 'descrText': 'Right click to drink. Can only hold charges while in belt. Refills as you kill monsters.', 'frameType': 1, 'x': 0, 'y': 0, 'inventoryId': 'Flask'}, {'verified': False, 'w': 1, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzksMTQseyJmIjoiMkRJdGVtcy9GbGFza3MvbGlmZWZsYXNrOSIsInciOjEsImgiOjIsInNjYWxlIjoxLCJsZXZlbCI6MX1d/67262f06f5/lifeflask9.png', 'league': 'Standard', 'id': 'ac9f5771f438cc42d02ddb0e8430076c941375cf86ec99adddda8164ac4b68d6', 'name': '', 'typeLine': 'Thickened Hallowed Life Flask of Damping', 'baseType': 'Hallowed Life Flask', 'identified': True, 'ilvl': 44, 'properties': [{'name': 'Recovers {0} Life over {1} Seconds', 'values': [['1990', 0], ['2.70', 1]], 'displayMode': 3}, {'name': 'Consumes {0} of {1} Charges on use', 'values': [['10', 0], ['30', 0]], 'displayMode': 3}, {'name': 'Currently has {0} Charges', 'values': [['30', 0]], 'displayMode': 3}], 'requirements': [{'name': 'Level', 'values': [['42', 0]], 'displayMode': 0, 'type': 62}], 'explicitMods': ['50% increased Recovery rate', 'Grants Immunity to Ignite for 7 seconds if used while Ignited\nRemoves all Burning when used'], 'descrText': 'Right click to drink. Can only hold charges while in belt. Refills as you kill monsters.', 'frameType': 1, 'x': 3, 'y': 0, 'inventoryId': 'Flask'}, {'verified': False, 'w': 2, 'h': 3, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQXJtb3Vycy9Cb2R5QXJtb3Vycy9Cb2R5U3RyMUMiLCJ3IjoyLCJoIjozLCJzY2FsZSI6MX1d/94a3d5d98e/BodyStr1C.png', 'league': 'Standard', 'id': 'b1b395a06cce6c28089c9175f6f5c6d14b0891b56073c76de3c593fcc2f1dc11', 'sockets': [{'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'I', 'sColour': 'B'}], 'name': 'Hypnotic Hide', 'typeLine': 'Sun Plate', 'baseType': 'Sun Plate', 'identified': True, 'ilvl': 49, 'properties': [{'name': 'Armour', 'values': [['807', 1]], 'displayMode': 0, 'type': 16}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Str', 'values': [['124', 0]], 'displayMode': 1, 'type': 63}, {'name': 'Int', 'values': [['109', 0]], 'displayMode': 1, 'type': 65, 'suffix': '(gem)'}], 'explicitMods': ['+53 to Armour', '50% increased Armour', '+8% to Fire Resistance', '+24% to Lightning Resistance', '+13% to Chaos Resistance', 'Reflects 3 Physical Damage to Melee Attackers'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'BodyArmour', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0xpZmVUYXAiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/9cef38ae47/LifeTap.png', 'support': True, 'id': '34a5222b7544a3d5b948408149535ed30abe6bbcc0d2cf4973a6ba2f1da8b56e', 'name': '', 'typeLine': 'Lifetap Support', 'baseType': 'Lifetap Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support, Duration', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['15', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['300%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['55', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['88', 0]], 'displayMode': 1, 'type': 63}], 'additionalProperties': [{'name': 'Experience', 'values': [['3134556/7610839', 0]], 'displayMode': 2, 'progress': 0.41, 'type': 20}], 'secDescrText': 'Supports any non-blessing skill. Minions cannot gain the Lifetap buff.', 'explicitMods': ['Supported Skills Cost Life instead of Mana', 'Gain Lifetap after Spending a total of 156 Life on Upfront\nCosts and Effects of a Supported Skill', 'Supported Skills deal 17% more Damage while you have Lifetap', 'Lifetap lasts 4 seconds'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 0, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L011bHRpcGxlVG90ZW1zIiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/dc8f032f0b/MultipleTotems.png', 'support': True, 'id': '90e10a77400be32872f1a641f501162413dbd37ddf4b9024cbda28b950aefcf1', 'name': '', 'typeLine': 'Multiple Totems Support', 'baseType': 'Multiple Totems Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Totem, Support', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['10', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['140%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['57', 0]], 'displayMode': 1, 'type': 63}, {'name': 'Int', 'values': [['39', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['1569305/3655184', 0]], 'displayMode': 2, 'progress': 0.43, 'type': 20}], 'secDescrText': 'Supports skills which summon totems.', 'explicitMods': ['Supported Skills have +2 to maximum number of Summoned Totems', 'Supported Skills Summon two Totems instead of one', 'Supported Skills deal 31% less Damage'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 1, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L1RvdGVtIiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/e168c87ee6/Totem.png', 'support': True, 'id': '93da2085c8b3f1bb10dd5dd2f1927656271c07d534613e0b2938f393b9317fad', 'name': '', 'typeLine': 'Spell Totem Support', 'baseType': 'Spell Totem Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support, Spell, Totem', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['13', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['200%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['49', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['50', 0]], 'displayMode': 1, 'type': 63}, {'name': 'Int', 'values': [['35', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['1053854/1964019', 0]], 'displayMode': 2, 'progress': 0.54, 'type': 20}], 'secDescrText': 'Supports spell skills that are not triggered. Instead of casting that spell, you will summon a totem that casts the spell for you.', 'explicitMods': ['Supported Skills deal 43% less Damage', 'Supported Skills will summon a Totem which uses that Skill', 'Totem lasts 8 seconds', 'Supported Skills have 40% less Cast Speed'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 2, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9XaXRoZXJHZW0iLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/f4a77cf6bc/WitherGem.png', 'support': False, 'id': 'e6cdf3249b005c5f4af23fd8fe703ef6aed0bb2d0fad06885fb6ff75bcc80864', 'name': '', 'typeLine': 'Wither', 'baseType': 'Wither', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Spell, AoE, Duration, Chaos, Channelling', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['12', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost', 'values': [['7 Mana', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['0.28 sec', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['48', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Int', 'values': [['109', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['1781907/1791769', 0]], 'displayMode': 2, 'progress': 0.99, 'type': 20}], 'secDescrText': 'Casts a debilitating debuff on enemies in an area, hindering their movement and also inflicts the Withered debuff, which increases the Chaos Damage they take and can stack up to 15 times.', 'explicitMods': ['Withered lasts 2 seconds', 'Base duration is 0.50 seconds', '11% increased Area of Effect', '33% reduced Movement Speed', '6% increased Chaos Damage taken'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 3, 'colour': 'I'}]}, {'verified': False, 'w': 1, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzksMTQseyJmIjoiMkRJdGVtcy9GbGFza3MvcGhhc2VmbGFzazAxIiwidyI6MSwiaCI6Miwic2NhbGUiOjEsImxldmVsIjoxfV0/6266d738e1/phaseflask01.png', 'league': 'Standard', 'id': '9e0e4d9f060d45085d5929f9be424570b5ff696d513a5af4a23137deeffa33f2', 'name': '', 'typeLine': "Transgressor's Quartz Flask of the Skink", 'baseType': 'Quartz Flask', 'identified': True, 'ilvl': 54, 'properties': [{'name': 'Lasts {0} Seconds', 'values': [['3.50', 1]], 'displayMode': 3}, {'name': 'Consumes {0} of {1} Charges on use', 'values': [['30', 0], ['60', 0]], 'displayMode': 3}, {'name': 'Currently has {0} Charges', 'values': [['60', 0]], 'displayMode': 3}], 'requirements': [{'name': 'Level', 'values': [['33', 0]], 'displayMode': 0, 'type': 62}], 'utilityMods': ['+10% chance to Suppress Spell Damage', 'Phasing'], 'explicitMods': ['Gain 4 Charges when you are Hit by an Enemy', '42% less Duration', 'Immunity to Bleeding and Corrupted Blood during Flask Effect'], 'descrText': 'Right click to drink. Can only hold charges while in belt. Refills as you kill monsters.', 'frameType': 1, 'x': 1, 'y': 0, 'inventoryId': 'Flask'}, {'verified': False, 'w': 2, 'h': 4, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvV2VhcG9ucy9Ud29IYW5kV2VhcG9ucy9TdGF2ZXMvU3RhZmY0IiwidyI6MiwiaCI6NCwic2NhbGUiOjF9XQ/85c22bd16b/Staff4.png', 'league': 'Standard', 'id': '11de806fae1917aaaa86d8487ea068768716dd80a8011487e2d63db49ae4889b', 'sockets': [{'group': 0, 'attr': 'D', 'sColour': 'G'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'I', 'sColour': 'B'}, {'group': 0, 'attr': 'I', 'sColour': 'B'}], 'name': 'Golem Cry', 'typeLine': 'Military Staff', 'baseType': 'Military Staff', 'identified': True, 'ilvl': 47, 'properties': [{'name': 'Warstaff', 'values': [], 'displayMode': 0}, {'name': 'Physical Damage', 'values': [['38-114', 0]], 'displayMode': 0, 'type': 9}, {'name': 'Critical Strike Chance', 'values': [['6.60%', 0]], 'displayMode': 0, 'type': 12}, {'name': 'Attacks per Second', 'values': [['1.25', 0]], 'displayMode': 0, 'type': 13}, {'name': 'Weapon Range', 'values': [['13', 0]], 'displayMode': 0, 'type': 14}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Str', 'values': [['88', 0]], 'displayMode': 1, 'type': 63, 'suffix': '(gem)'}, {'name': 'Dex', 'values': [['56', 0]], 'displayMode': 1, 'type': 64, 'suffix': '(gem)'}, {'name': 'Int', 'values': [['125', 0]], 'displayMode': 1, 'type': 65, 'suffix': '(gem)'}], 'implicitMods': ['+18% Chance to Block Attack Damage while wielding a Staff'], 'explicitMods': ['+1 to Level of Socketed Chaos Gems', '+10% to Global Critical Strike Multiplier', 'Gain 7 Life per Enemy Killed', '+197 to Accuracy Rating'], 'craftedMods': ['59% increased Spell Damage'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Weapon', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L1ZvaWRNYW5pcHVsYXRpb24iLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/d43a79f597/VoidManipulation.png', 'support': True, 'id': 'efdd646d6c84d24642901efa5924ee4e2583f342ce7bb7a2e2eec5a072121c1a', 'name': '', 'typeLine': 'Void Manipulation Support', 'baseType': 'Void Manipulation Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Chaos, Support', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['15', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['130%', 0]], 'displayMode': 0}, {'name': 'Quality', 'values': [['+10%', 1]], 'displayMode': 0, 'type': 6}], 'requirements': [{'name': 'Level', 'values': [['55', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Dex', 'values': [['56', 0]], 'displayMode': 1, 'type': 64}, {'name': 'Int', 'values': [['39', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['4043560/7610839', 0]], 'displayMode': 2, 'progress': 0.53, 'type': 20}], 'secDescrText': 'Supports any skill that deals damage.', 'explicitMods': ['Supported Skills deal 30% more Chaos Damage', 'Supported Skills deal 5% increased Chaos Damage', 'Supported Skills deal no Elemental Damage'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 0, 'colour': 'D'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0xpZmVUYXAiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/9cef38ae47/LifeTap.png', 'support': True, 'id': '2241d914e2ebb8f0605779c257613467e85b499b96bbb6a566d95d8d735cc914', 'name': '', 'typeLine': 'Lifetap Support', 'baseType': 'Lifetap Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support, Duration', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['15', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['300%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['55', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['88', 0]], 'displayMode': 1, 'type': 63}], 'additionalProperties': [{'name': 'Experience', 'values': [['4043560/7610839', 0]], 'displayMode': 2, 'progress': 0.53, 'type': 20}], 'secDescrText': 'Supports any non-blessing skill. Minions cannot gain the Lifetap buff.', 'explicitMods': ['Supported Skills Cost Life instead of Mana', 'Gain Lifetap after Spending a total of 156 Life on Upfront\nCosts and Effects of a Supported Skill', 'Supported Skills deal 17% more Damage while you have Lifetap', 'Lifetap lasts 4 seconds'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 1, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0NvbnRyb2xsZWREZXN0cnVjdGlvbkdlbSIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/0fca4292bb/ControlledDestructionGem.png', 'support': True, 'id': '0f63b6813ba24eb334d3edf1334bf0be90f39bdd766a68c61ccd2827b7065010', 'name': '', 'typeLine': 'Controlled Destruction Support', 'baseType': 'Controlled Destruction Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Spell, Critical, Support', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['13', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['140%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Int', 'values': [['90', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['1371154/3655184', 0]], 'displayMode': 2, 'progress': 0.38, 'type': 20}], 'secDescrText': 'Supports attack skills, or spell skills that deal damage.', 'explicitMods': ['Supported Skills have 80% less Critical Strike Chance', 'Supported Skills deal 34% more Spell Damage'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 2, 'colour': 'I'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9Ta2VsZXRhbENoYWlucyIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/5976d42537/SkeletalChains.png', 'support': False, 'id': '9be3997cc4fc07ec9b600b487ed011979f4b17f8693f32ff4970001e36c57bc2', 'name': '', 'typeLine': 'Dark Pact', 'baseType': 'Dark Pact', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Minion, Spell, AoE, Chaining, Chaos, Nova', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['13', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost', 'values': [['11 Mana', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['0.50 sec', 0]], 'displayMode': 0}, {'name': 'Critical Strike Chance', 'values': [['5.00%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Int', 'values': [['125', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['1569305/3655184', 0]], 'displayMode': 2, 'progress': 0.43, 'type': 20}], 'secDescrText': 'This spell removes some life from one of your Skeleton minions near you or the targeted location to deal chaos damage in an area around it. This effect will chain to your other nearby skeletons. If you have no skeletons near you or the targeted location, it will sacrifice your own life to deal damage instead.', 'explicitMods': ['Deals 118 to 177 Chaos Damage', 'Chains +2 Times', "Sacrifices 8% of Skeleton's Life to deal that much Chaos Damage", 'Uses your Life if no Skeletons in range', '106% more Damage with Hits and Ailments if using your Life'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 3, 'colour': 'I'}]}, {'verified': False, 'w': 1, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzksMTQseyJmIjoiMkRJdGVtcy9GbGFza3MvbGlmZWZsYXNrOSIsInciOjEsImgiOjIsInNjYWxlIjoxLCJsZXZlbCI6MX1d/67262f06f5/lifeflask9.png', 'league': 'Standard', 'id': '883cf71980bbcebecf81bfc2095dc2d880d1e77f8ab0a146f916c1c396677022', 'name': '', 'typeLine': 'Plentiful Hallowed Life Flask of Warding', 'baseType': 'Hallowed Life Flask', 'identified': True, 'ilvl': 30, 'properties': [{'name': 'Recovers {0} Life over {1} Seconds', 'values': [['1990', 0], ['4', 0]], 'displayMode': 3}, {'name': 'Consumes {0} of {1} Charges on use', 'values': [['10', 0], ['52', 1]], 'displayMode': 3}, {'name': 'Currently has {0} Charges', 'values': [['52', 0]], 'displayMode': 3}], 'requirements': [{'name': 'Level', 'values': [['42', 0]], 'displayMode': 0, 'type': 62}], 'explicitMods': ['+22 to Maximum Charges', 'Removes Curses on use'], 'descrText': 'Right click to drink. Can only hold charges while in belt. Refills as you kill monsters.', 'frameType': 1, 'x': 2, 'y': 0, 'inventoryId': 'Flask'}, {'verified': False, 'w': 2, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQXJtb3Vycy9Cb290cy9XYW5kZXJsdXN0IiwidyI6MiwiaCI6Miwic2NhbGUiOjF9XQ/c83c1c3bdc/Wanderlust.png', 'league': 'Standard', 'id': '5761881543e0738780107fe4e9425c4d31fda86687eeebac4ec72411ed46c49d', 'sockets': [{'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'D', 'sColour': 'G'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 1, 'attr': 'I', 'sColour': 'B'}], 'name': 'Wanderlust', 'typeLine': 'Wool Shoes', 'baseType': 'Wool Shoes', 'identified': True, 'ilvl': 79, 'properties': [{'name': 'Energy Shield', 'values': [['25', 1]], 'displayMode': 0, 'type': 18}], 'requirements': [{'name': 'Level', 'values': [['57', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Str', 'values': [['127', 0]], 'displayMode': 1, 'type': 63, 'suffix': '(gem)'}, {'name': 'Dex', 'values': [['53', 0]], 'displayMode': 1, 'type': 64, 'suffix': '(gem)'}, {'name': 'Int', 'values': [['76', 0]], 'displayMode': 1, 'type': 65, 'suffix': '(gem)'}], 'explicitMods': ['+5 to Dexterity', '+18 to maximum Energy Shield', '36% increased Mana Regeneration Rate', '20% increased Movement Speed', 'Cannot be Frozen'], 'flavourText': ['All the world is my home.'], 'frameType': 3, 'x': 0, 'y': 0, 'inventoryId': 'Boots', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9MZWFwU2xhbSIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/f65891de7a/LeapSlam.png', 'support': False, 'id': '5fb6544a620f78278304250f6ead261ff6b81f6f13b847af38b25ab3a3ec6376', 'name': '', 'typeLine': 'Leap Slam', 'baseType': 'Leap Slam', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Attack, AoE, Movement, Travel, Slam, Melee', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['15', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost', 'values': [['10 Mana', 0]], 'displayMode': 0}, {'name': 'Attack Damage', 'values': [['136.8% of base', 0]], 'displayMode': 0}, {'name': 'Effectiveness of Added Damage', 'values': [['137%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['57', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['127', 0]], 'displayMode': 1, 'type': 63}], 'additionalProperties': [{'name': 'Experience', 'values': [['1854424/9095466', 0]], 'displayMode': 2, 'progress': 0.2, 'type': 20}], 'secDescrText': 'Jump into the air, damaging and knocking back enemies with your weapon where you land. Enemies you would land on are pushed out of the way. Requires an Axe, Mace, Sceptre, Sword or Staff. Cannot be supported by Multistrike.', 'explicitMods': ['34% increased Stun Duration against Enemies that are on Full Life', '+0.55 seconds to Attack Time', 'Damaging Hits always Stun Enemies that are on Full Life'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 0, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9TdXBwb3J0L0xpZmVUYXAiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/9cef38ae47/LifeTap.png', 'support': True, 'id': '7ca9a983963232e4b75a74af7ffa901168fc3c3af2fdb66352f61350e36a175a', 'name': '', 'typeLine': 'Lifetap Support', 'baseType': 'Lifetap Support', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Support, Duration', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['15', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost & Reservation Multiplier', 'values': [['300%', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['55', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Str', 'values': [['88', 0]], 'displayMode': 1, 'type': 63}], 'additionalProperties': [{'name': 'Experience', 'values': [['3134556/7610839', 0]], 'displayMode': 2, 'progress': 0.41, 'type': 20}], 'secDescrText': 'Supports any non-blessing skill. Minions cannot gain the Lifetap buff.', 'explicitMods': ['Supported Skills Cost Life instead of Mana', 'Gain Lifetap after Spending a total of 156 Life on Upfront\nCosts and Effects of a Supported Skill', 'Supported Skills deal 17% more Damage while you have Lifetap', 'Lifetap lasts 4 seconds'], 'descrText': 'This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.', 'frameType': 4, 'socket': 2, 'colour': 'S'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9EZXNwYWlyIiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/b4dbf071cd/Despair.png', 'support': False, 'id': 'd921d067f7d495d2caf89b102a400434836f0495c54348ed96d9b6216c63c44c', 'name': '', 'typeLine': 'Despair', 'baseType': 'Despair', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Spell, AoE, Duration, Chaos, Curse, Hex', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['12', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Cost', 'values': [['27 Mana', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['0.50 sec', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['54', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Dex', 'values': [['53', 0]], 'displayMode': 1, 'type': 64}, {'name': 'Int', 'values': [['76', 0]], 'displayMode': 1, 'type': 65}], 'additionalProperties': [{'name': 'Experience', 'values': [['395883/1956648', 0]], 'displayMode': 2, 'progress': 0.2, 'type': 20}], 'secDescrText': 'Curses all targets in an area, lowering their chaos resistance and increasing damage over time they take. All hits will deal added chaos damage to the cursed enemies.', 'explicitMods': ['Base duration is 10.10 seconds', 'Curse gains 10 Doom per second if you Cast this Spell yourself', '+6 to radius', 'Cursed enemies have -25% to Chaos Resistance', 'Cursed enemies take 21% increased Damage from Damage Over Time effects', 'Adds 28 to 36 Chaos Damage to Hits against Cursed Enemies'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 3, 'colour': 'I'}]}, {'verified': False, 'w': 2, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQXJtb3Vycy9IZWxtZXRzL0hlbG1ldERleFVuaXF1ZTIiLCJ3IjoyLCJoIjoyLCJzY2FsZSI6MX1d/7f4908ef2f/HelmetDexUnique2.png', 'league': 'Standard', 'id': '6d45b1edaa6fb7daafd8c88e375abcb393327ae3e56f14993862c841c8e7105f', 'sockets': [{'group': 0, 'attr': 'D', 'sColour': 'G'}, {'group': 0, 'attr': 'D', 'sColour': 'G'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}, {'group': 0, 'attr': 'S', 'sColour': 'R'}], 'name': 'Goldrim', 'typeLine': 'Leather Cap', 'baseType': 'Leather Cap', 'identified': True, 'ilvl': 71, 'properties': [{'name': 'Evasion Rating', 'values': [['59', 1]], 'displayMode': 0, 'type': 17}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62, 'suffix': '(gem)'}, {'name': 'Dex', 'values': [['125', 0]], 'displayMode': 1, 'type': 64, 'suffix': '(gem)'}], 'explicitMods': ['+37 to Evasion Rating', '10% increased Rarity of Items found', '+40% to all Elemental Resistances', 'Reflects 4 Physical Damage to Melee Attackers'], 'flavourText': ['No metal slips as easily through the fingers as gold.'], 'frameType': 3, 'x': 0, 'y': 0, 'inventoryId': 'Helm', 'socketedItems': [{'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9IZXJhbGRPZkFnb255R2VtIiwidyI6MSwiaCI6MSwic2NhbGUiOjF9XQ/0e95349c4d/HeraldOfAgonyGem.png', 'support': False, 'id': '006d3ea62586cc9ff0e63d2c79c7aa2a97cacbcdcf28e949ecbbcf4b1889484e', 'name': '', 'typeLine': 'Herald of Agony', 'baseType': 'Herald of Agony', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Spell, Herald, Minion, Chaos, Physical', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['11', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Reservation', 'values': [['25% Mana', 0]], 'displayMode': 0}, {'name': 'Cooldown Time', 'values': [['1.00 sec', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['Instant', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['49', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Dex', 'values': [['111', 0]], 'displayMode': 1, 'type': 64}], 'additionalProperties': [{'name': 'Experience', 'values': [['1964019/1964019', 0]], 'displayMode': 2, 'progress': 1, 'type': 20}], 'nextLevelRequirements': [{'name': 'Level', 'values': [['52', 0]], 'displayMode': 0}, {'name': 'Dex', 'values': [['117', 0]], 'displayMode': 1}], 'secDescrText': 'Grants a buff giving more poison damage and a chance to inflict poison. When you poison an enemy while you have this buff, you gain Virulence, and summon an Agony Crawler minion that uses projectile and area attacks. You will lose Virulence over time, at a rate which increases the more Virulence you have. The minion will die when you have no Virulence.', 'explicitMods': ['Maximum 1 Summoned Agony Crawler', 'Buff grants 20% chance to Poison on Hit', 'Grants Virulence when you Poison an Enemy', 'Buff grants 10% more Damage with Poison', 'Maximum 40 Virulence', 'Agony Crawler has 3% increased Attack Speed per Virulence you have', 'Agony Crawler deals 7% increased Physical Damage per Virulence you have', 'Agony Crawler has 13 to 25 Added Physical Damage per Virulence you have', 'Minions cannot Taunt Enemies'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 0, 'colour': 'D'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9HcmFjZSIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/e98082048a/Grace.png', 'support': False, 'id': '5357bc1e1d9ca5fbd4f1d30e3c27b761357c0761f4b11d24c397bd82b53cf2d9', 'name': '', 'typeLine': 'Grace', 'baseType': 'Grace', 'identified': True, 'ilvl': 0, 'properties': [{'name': 'Aura, Spell, AoE', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['13', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Reservation', 'values': [['50% Mana', 0]], 'displayMode': 0}, {'name': 'Cooldown Time', 'values': [['1.20 sec', 0]], 'displayMode': 0}, {'name': 'Cast Time', 'values': [['Instant', 0]], 'displayMode': 0}], 'requirements': [{'name': 'Level', 'values': [['56', 0]], 'displayMode': 0, 'type': 62}, {'name': 'Dex', 'values': [['125', 0]], 'displayMode': 1, 'type': 64}], 'additionalProperties': [{'name': 'Experience', 'values': [['1781907/3655184', 0]], 'displayMode': 2, 'progress': 0.49, 'type': 20}], 'secDescrText': 'Casts an aura that grants evasion to you and your allies.', 'explicitMods': ['+12 to radius', 'You and nearby allies gain 1283 additional Evasion Rating', 'You and nearby allies gain 26% more Evasion rating'], 'descrText': 'Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.', 'frameType': 4, 'socket': 1, 'colour': 'D'}]}, {'verified': False, 'w': 1, 'h': 2, 'icon': 'https://web.poecdn.com/gen/image/WzksMTQseyJmIjoiMkRJdGVtcy9GbGFza3Mvc3ByaW50IiwidyI6MSwiaCI6Miwic2NhbGUiOjEsImxldmVsIjoxfV0/aa66be180b/sprint.png', 'league': 'Standard', 'id': 'bbc065688ce6e3708373983d1f38c11d741f0942187f3862aca5de277a16a75c', 'name': '', 'typeLine': 'Wide Quicksilver Flask of the Deer', 'baseType': 'Quicksilver Flask', 'identified': True, 'ilvl': 4, 'properties': [{'name': 'Lasts {0} Seconds', 'values': [['3.20', 1]], 'displayMode': 3}, {'name': 'Consumes {0} of {1} Charges on use', 'values': [['30', 0], ['78', 1]], 'displayMode': 3}, {'name': 'Currently has {0} Charges', 'values': [['78', 0]], 'displayMode': 3}], 'requirements': [{'name': 'Level', 'values': [['4', 0]], 'displayMode': 0, 'type': 62}], 'utilityMods': ['40% increased Movement Speed'], 'explicitMods': ['+18 to Maximum Charges', '47% less Duration', 'Immunity to Freeze and Chill during Flask Effect'], 'descrText': 'Right click to drink. Can only hold charges while in belt. Refills as you kill monsters.', 'frameType': 1, 'x': 4, 'y': 0, 'inventoryId': 'Flask'}, {'verified': False, 'w': 1, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQW11bGV0cy9UdXJxdW9pc2VBbXVsZXQiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/605b4da0e1/TurquoiseAmulet.png', 'league': 'Standard', 'id': '835bd4efc885e501dd07cedab743c7e99c9cbf36d7c6a1922aae75bc18de3406', 'name': 'Chimeric Heart', 'typeLine': 'Turquoise Amulet', 'baseType': 'Turquoise Amulet', 'identified': True, 'ilvl': 66, 'requirements': [{'name': 'Level', 'values': [['44', 0]], 'displayMode': 0, 'type': 62}], 'implicitMods': ['+18 to Dexterity and Intelligence'], 'explicitMods': ['+23 to all Attributes', '+15% to Damage over Time Multiplier', '28% increased Armour', 'Regenerate 1.5 Life per second'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Amulet'}, {'verified': False, 'w': 2, 'h': 1, 'icon': 'https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQmVsdHMvQmVsdDMiLCJ3IjoyLCJoIjoxLCJzY2FsZSI6MX1d/93af17affd/Belt3.png', 'league': 'Standard', 'id': '9b9350afdc42a99c3f767636877e5f750878c67ecdf501aeee6040cf62d2c51a', 'name': 'Eagle Harness', 'typeLine': 'Leather Belt', 'baseType': 'Leather Belt', 'identified': True, 'ilvl': 66, 'requirements': [{'name': 'Level', 'values': [['35', 0]], 'displayMode': 0, 'type': 62}], 'implicitMods': ['+36 to maximum Life'], 'explicitMods': ['+32 to Armour', '+77 to maximum Life', '+12% to Fire Resistance', '+7% to Lightning Resistance', '12% increased Flask Mana Recovery rate'], 'craftedMods': ['+25% to Cold Resistance'], 'frameType': 2, 'x': 0, 'y': 0, 'inventoryId': 'Belt'}], 'character': {'name': 'ChoaticKillerKesKesCest', 'league': 'Standard', 'classId': 4, 'ascendancyClass': 1, 'class': 'Slayer', 'level': 59, 'experience': 143753011}}


class ItemsUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self.itemlist = []

        self.xml_items = None

        # self.model = Model(self.win.list_Items)
        # self.win.list_Items.setModel(self.model)
        # self.model.itemChanged.connect(self.on_item_changed)
        # self.win.list_Items.setAlternatingRowColors(True)

        # self.my_model = Model(self.win.list_Items)
        # self.win.list_Items.setModel(self.my_model)

        # self.my_model.rowDropped.connect(self.drag_dropped)
        self.win.list_Items.currentItemChanged.connect(self.on_row_changed)
        self.win.list_Items.indexesMoved.connect(self.onIndexesMoved)
        self.win.btn_weaponSwap.clicked.connect(self.weapon_swap)

        # setup Alt Weapon combo's
        self.combo_alt_weapon1 = QComboBox(self.win.groupbox_Items)
        self.combo_alt_weapon1.setVisible(False)
        self.combo_alt_weapon1.setGeometry(self.win.combo_Weapon1.geometry())
        self.combo_alt_weapon2 = QComboBox(self.win.groupbox_Items)
        self.combo_alt_weapon2.setVisible(False)
        self.combo_alt_weapon2.setGeometry(self.win.combo_Weapon2.geometry())

        self.combo_slot_map = {
            "Weapon 1": self.win.combo_Weapon1,
            "Weapon 2": self.win.combo_Weapon2,
            "Weapon 1 Swap": self.combo_alt_weapon1,
            "Weapon 2 Swap": self.combo_alt_weapon2,
            "Helmet": self.win.combo_Helmet,
            "Body Armour": self.win.combo_BodyArmour,
            "Gloves": self.win.combo_Gloves,
            "Boots": self.win.combo_Boots,
            "Amulet": self.win.combo_Amulet,
            "Ring 1": self.win.combo_Ring1,
            "Ring 2": self.win.combo_Ring2,
            "Belt": self.win.combo_Belt,
            "Flask 1": self.win.combo_Flask1,
            "Flask 2": self.win.combo_Flask2,
            "Flask 3": self.win.combo_Flask3,
            "Flask 4": self.win.combo_Flask4,
            "Flask 5": self.win.combo_Flask5,
        }

        # t = Item()
        # t.load_from_xml(test)
        # f = Item()
        # f.load_from_json(fract)
        # g = Item()
        # g.load_from_json(gloves)
        self.load_from_json(items1)

    def add_item(self):
        """
        Create an Item() class and add it to the internal list.
        :return: an Item() class object
        """
        item = Item()
        self.itemlist.append(item)
        return item

    def add_item_to_item_list(self, _item):
        """
        Add a new row to the Items list
        :param _item: Item(): The item to be added
        :return:
        """
        if _item is None:
            return
        # print(_item.name, _item.rarity)
        row = QListWidgetItem()
        self.win.list_Items.addItem(row)
        label = QLabel()
        label.setAcceptDrops(False)
        label.setFrameShape(QFrame.NoFrame)
        # label.setFrameShape(QFrame.StyledPanel)
        label.setFixedHeight(22)
        label.setText(f'<span style="color:{ColourCodes[_item.rarity].value};">{_item.name}</span>')
        label.setToolTip(_item.tooltip())
        self.win.list_Items.setItemWidget(row, label)

    @Slot()
    def weapon_swap(self, checked):
        """"""
        self.win.combo_Weapon1.setVisible(not checked)
        self.win.combo_Weapon2.setVisible(not checked)
        self.combo_alt_weapon1.setVisible(checked)
        self.combo_alt_weapon2.setVisible(checked)
        self.win.btn_weaponSwap.setText(checked and "Show Main" or "Show Alt")
        self.win.label_Weapon1.setText(f'{checked and "Alt" or ""} Weapon 1:')
        self.win.label_Weapon2.setText(f'{checked and "Alt" or ""} Weapon 2:')

    @Slot()
    def define_item_labels(self):
        """"""
        for idx, _item in enumerate(self.itemlist):
            label = self.win.list_Items.itemWidget(idx)
            label.setText(f'<span style="color:{ColourCodes[_item.rarity].value};">{_item.name}</span>')
            # Do more here based on itemsets, etc

    @Slot()
    def on_row_changed(self, item):
        # print(type(item), item.text())
        label: QLabel = self.win.list_Items.itemWidget(item)
        print(type(label), label.text())

    @Slot()
    def drag_dropped(self, current):
        print("Row %d selected", type(current), current)

    @Slot()
    def onIndexesMoved(self, indexes):
        print("indexes were moved", type(indexes), indexes)

    def clear_controls(self):
        """
        Clear certain controls on the Skills tab in preparation for reloading.

        :return: N/A
        """
        self.win.list_Items.clear()
        for combo in self.combo_slot_map:
            self.combo_slot_map[combo].clear()
        # temporary so we can see them changing
        self.combo_alt_weapon1.addItem("combo_alt_weapon1", None)
        self.combo_alt_weapon2.addItem("combo_alt_weapon2", None)

    def load_from_xml(self, _items):
        """
        Load internal structures from the build object.

        :param _items: Reference to the xml <Items> tag set
        :return: N/A
        """
        self.xml_items = _items
        # self.clear_controls()
        # add the items to the list box
        for _item in self.xml_items.findall("Item"):
            new_item = self.add_item()
            # new_item.curr_variant = _item.get("variant", "")
            new_item.load_from_xml(_item.text)
            self.add_item_to_item_list(new_item)
        for _item_set in self.xml_items.findall("ItemSet"):
            self.win.combo_ItemSet.addItem(_item_set.get("title", "Default"), _item_set)
            for _slot in _item_set.findall("Slot"):
                _name = _slot.get("name"), _slot.get("itemId")
                _id = int(_slot.get("itemId", 0))
                if _id != 0:
                    self.itemlist[_id - 1].slot = _name
        self.win.combo_ItemSet.setCurrentIndex(0)

    def load_from_json(self, _items):
        """
        Load internal structures from the build object.

        :param _items: Reference to the xml <Items> tag set
        :return: N/A
        """
        self.clear_controls()
        # print(_items)
        character = _items["character"]
        # add the items to the list box
        for _item in _items["items"]:
            # print(_item)
            new_item = self.add_item()
            new_item.load_from_json(_item)
            # print(vars(new_item))
            self.add_item_to_item_list(new_item)


class Model(QStandardItemModel):
    """An idea for a model to export a signel for the drop point, but it doesn't work with QListWidget"""

    rowDropped = Signal(int)

    def dropMimeData(self, *args):
        success = super(Model, self).dropMimeData(*args)
        if success:
            self.rowDropped.emit(args[2])
        return success


class Item:
    """
    A class to encapsulate one item
    """

    def __init__(self, _slot=None) -> None:
        """
        Initialise defaults
        :param _slot: where this item is worn/carried.
        """
        self._slot = _slot

        # this is not always available from the json character download
        self.level_req = 0

        self.rarity = "NORMAL"
        self.title = ""
        self.name = ""
        self.base_name = ""
        self.ilevel = 0
        self.quality = 0
        self.curr_variant = ""
        self.unique_id = ""
        self.requires = {}
        self.influences = []
        self.two_hand = False
        self.corrupted = False
        self.fractured = None
        self.fracturedMods = None
        self.abyss_jewel = None
        self.synthesised = None
        self.sockets = ""
        self.properties = {}
        self.limits = 0
        self.implicitMods = []
        self.explicitMods = []
        self.full_explicitMods_list = []
        self.craftedMods = []
        self.enchantMods = []

    def load_from_xml(self, desc):
        """
        Load internal structures from the build object's xml
        """
        # ToDo: Mod mod class to handle ranges, crafts ?
        # split lines into a list, removing any blank lines, leading & trailing spaces.
        # stolen from https://stackoverflow.com/questions/7630273/convert-multiline-into-list
        lines = [y for y in (x.strip() for x in desc.splitlines()) if y]
        # lets get all the : separated variables first and remove them from the lines list
        # stop when we get to implicits
        explicits_idx, line_idx = (0, 0)
        # Can't use enumerate as we are changing the list as we move through
        while index_exists(lines, line_idx):
            # _debug("a", len(lines), lines)
            m = re.search(r"(.*): (.*)", lines[line_idx])
            if m is not None:
                lines.pop(line_idx)
                match m.group(1):
                    case "Rarity":
                        self.rarity = m.group(2).upper()
                    case "Unique ID":
                        self.unique_id = m.group(2)
                    case "Item Level":
                        self.ilevel = m.group(2)
                    case "Selected Variant":
                        self.curr_variant = m.group(2)
                    case "Quality":
                        self.quality = m.group(2)
                    case "Sockets":
                        self.sockets = m.group(2)
                    case "LevelReq":
                        self.level_req = int(m.group(2))
                    case "Limited to":
                        self.limits = int(m.group(2))
                    case "Implicits":
                        # implicits, if any
                        for idx in range(int(m.group(2))):
                            line = lines.pop(line_idx)
                            self.implicitMods.append(Mod(line))
                        explicits_idx = line_idx
                        break
                self.properties[m.group(1)] = m.group(2)
            else:
                # skip this line
                line_idx += 1
        # every thing that is left, from explicits_idx, is explicits
        for idx in range(explicits_idx, len(lines)):
            line = lines.pop(explicits_idx)
            mod = Mod(line)
            self.full_explicitMods_list.append(mod)
            if "Corrupted" in line:
                self.corrupted = True
            # check for variants and if it's our variant, add it to the smaller explicit mod list
            if "variant" in line:
                m = re.search(r"{variant:([\d,]+)}(.*)", line)
                for var in m.group(1).split(","):
                    if var == self.curr_variant:
                        self.explicitMods.append(mod)
            else:
                self.explicitMods.append(mod)

        # _debug("b", len(lines), lines)
        # 'normal' and Magic ? objects and flasks only have one line (either no title or no base name)
        if len(lines) == 1:
            self.name = lines.pop(0)
            match self.rarity:
                case "MAGIC":
                    self.base_name = self.name
                case "NORMAL":
                    self.base_name = self.name
        else:
            self.title = lines.pop(0)
            self.base_name = lines.pop(0)
            self.name = f"{self.title}, {self.base_name}"
        # _debug("c", len(lines), lines)

        # Anything left must be something like 'Shaper Item'
        for line in lines:
            if line in influence_colours.keys():
                self.influences.append(line)
            else:
                m = re.search(r"Requires (.*)", line)
                if m:
                    self.requires[m.group(1)] = True
                else:
                    # do something else
                    match line:
                        case _:
                            print(f"Item().load_from_xml: Skipped: {line}")

    def load_from_json(self, _json):
        """
        Load internal structures from the downloaded json
        """
        rarity_map = {0: "NORMAL", 1: "MAGIC", 2: "RARE", 3: "UNIQUE", 9: "RELIC"}

        def get_property(_json_item, _name, _default):
            """
            Get a property from a list of property tags. Not all properties appear to be mandatory.

            :param _json_item: the gem reference from the json download
            :param _name: the name of the property
            :param _default: a default value to be used if the property is not listed/found
            :return: Either the string value if found or the _default value passed in.
            """
            for _prop in _json_item:
                if _prop.get("name") == _name and _prop.get("suffix") != "(gem)":
                    value = _prop.get("values")[0][0].replace("+", "").replace("%", "")
                    return value
            return _default

        if type(_json) == str:
            _json = ast.literal_eval(_json)
        self.base_name = _json.get("typeLine", "")
        # for magic and normal items, name is blank
        self.title = _json.get("name", "")
        self.name = f'{self.title and f"{self.title}, " or ""}{self.base_name}'
        self.unique_id = _json["id"]
        self._slot = slot_map[_json["inventoryId"]]
        self.rarity = rarity_map[int(_json.get("frameType", 0))]

        # Mods
        for mod in _json.get("explicitMods", []):
            self.full_explicitMods_list.append(Mod(mod))
        for mod in _json.get("craftedMods", []):
            self.full_explicitMods_list.append(Mod(f"{{crafted}}{mod}"))
        self.explicitMods = self.full_explicitMods_list

        for mod in _json.get("enchantMods", []):
            self.implicitMods.append(Mod(f"{{crafted}}{mod}"))
        for mod in _json.get("scourgeMods", []):
            self.implicitMods.append(Mod(f"{{crafted}}{mod}"))
        for mod in _json.get("implicitMods", []):
            self.implicitMods.append(Mod(mod))
        # for mod in _json.get("scourgeModLines", []):
        #     self.implicitMods.append(f"{{crafted}}{mod}")
        # for mod in _json.get("implicitModLines", []):
        #     self.implicitMods.append(f"{{crafted}}{mod}")

        self.properties = _json.get("properties", {})
        if self.properties:
            self.quality = get_property(_json["properties"], "Quality", "0")
        self.ilevel = _json.get("ilvl", 0)
        # self.corrupted = str_to_bool(_json.get("corrupted", "False"))
        # self.abyss_jewel = str_to_bool(_json.get("abyssJewel", "False"))
        # self.fractured = str_to_bool(_json.get("fractured", "False"))
        # self.synthesised = str_to_bool(_json.get("synthesised", "False"))
        self.corrupted = _json.get("corrupted", False)
        self.abyss_jewel = _json.get("abyssJewel", False)
        self.fractured = _json.get("fractured", False)
        self.synthesised = _json.get("synthesised", False)
        if self.fractured:
            self.fracturedMods = _json.get("fracturedMods", None)
        self.level_req = int(get_property(_json["requirements"], "Level", "0"))
        # Process sockets and their grouping
        if _json.get("sockets", None) is not None:
            current_socket_group_number = -1
            socket_line = ""
            for socket in _json["sockets"]:
                this_group = socket["group"]
                if this_group == current_socket_group_number:
                    socket_line += f"-{socket['sColour']}"
                else:
                    socket_line += f" {socket['sColour']}"
                    current_socket_group_number = this_group
            # there will always be a leading space from the routine above
            self.sockets = socket_line.strip()
        """
        delve 	?bool 	always true if present
        synthesised 	?bool 	always true if present
        """
        influences = _json.get("influences", None)
        if influences is not None:
            # each entry is like 'shaper=true'
            for influence in influences:
                key = f'{influence.split("=")[0].title()} Item'
                if key in influence_colours.keys():
                    self.influences.append(key)

    def save(self):
        """
        Save internal structures back to a xml object

        :return: ET.ElementTree:
        """
        pass

    def tooltip(self):
        """
        Create a tooltip. Hand crafted html anyone ?

        :return: str: the tooltip
        """
        rarity_colour = f"{ColourCodes[self.rarity].value};"
        tip = (
            f"<style>"
            f"table, th, td {{border: 1px solid {rarity_colour}; border-collapse: collapse;}}"
            f"td {{text-align: center;}}"
            f"</style>"
            f'<table width="425">'
            f"<tr><th>"
        )
        name = self.title == "" and self.base_name or self.name
        tip += f'<span style="color:{rarity_colour};">{name}</span>'
        for influence in self.influences:
            tip += f'<br/><span style="color:{influence_colours[influence]};">{influence}</span>'
        tip += "</th></tr>"
        if self.level_req > 0:
            tip += f"<tr><td>Requires Level <b>{self.level_req}</b></td></tr>"
        if self.limits > 0:
            tip += f"<tr><td>Limited to: <b>{self.limits}</b></td></tr>"
        if len(self.implicitMods) > 0:
            tip += f"<tr><td>"
            for mod in self.implicitMods:
                tip += mod.tooltip
            # mod tooltip's always end in <br/>, remove the last one
            tip = tip[:-4]
            tip += f"</td></tr>"
        if len(self.explicitMods) > 0:
            tip += f"<tr><td>"
            for mod in self.explicitMods:
                if not mod.corrupted:
                    tip += mod.tooltip
            # mod tooltip's always end in <br/>, remove the last one
            tip = tip[:-4]
            tip += f"</td></tr>"

        if self.corrupted:
            tip += f'<tr><td><span style="color:{ColourCodes.STRENGTH.value};">Corrupted</span></td></tr>'
        tip += f"</table>"
        return tip

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, new_slot):
        self._slot = new_slot

    @property
    def shaper(self):
        return "Shaper" in self.influences

    @property
    def elder(self):
        return "Elder" in self.influences

    @property
    def warlord(self):
        return "Warlord" in self.influences

    @property
    def hunter(self):
        return "Hunter" in self.influences

    @property
    def crusader(self):
        return "Crusader" in self.influences

    @property
    def redeemer(self):
        return "Redeemer" in self.influences

    @property
    def exarch(self):
        return "Exarch" in self.influences

    @property
    def eater(self):
        return "Eater" in self.influences


class Mod:
    """
    A class to encapsulate one mod
    """

    def __init__(self, _line) -> None:
        """
        Initialise defaults
        :param _line: the full line of the mod, including variant stanzas.
        """
        # this is the text without {variant}, {crafted}, and {range}. At this point {range} is still present
        self.line = re.sub(r"{variant:\d+}", "", _line.replace("{crafted}", ""))
        # this is the text with the (xx-yy), eg '% increased Duration'.
        # It is to avoid recalculating this value needlessly
        self.line_without_range = None
        # print(f"\n_line", _line)
        self.corrupted = self.line == "Corrupted"
        if self.corrupted:
            self.tooltip = f'<span style="color:{ColourCodes.STRENGTH.value};">{self.line}</span><br/>'
            return

        # value for managing the range of values
        self._range = None
        self.min = None
        self.max = None
        # the actual value of the mod, where valid
        self.value = None
        self.crafted = "{crafted}" in _line
        self.tooltip_colour = self.crafted and ColourCodes.CRAFTED.value or ColourCodes.MAGIC.value
        # preformed text for adding to the tooltip. Let's set a default in case there is no 'range'
        self.tooltip = f'<span style="color:{self.tooltip_colour};">{self.line}</span><br/>'

        # check for and keep variant information
        m = re.search(r"({variant:\d+})", _line)
        self.variant_text = m and m.group(1) or None

        # sort out the range, min, max,value and the tooltip, if applicable
        tooltip = self.line
        m1 = re.search(r"{range:([0-9.]+)}(.*)", tooltip)
        if m1:
            # this is now stripped of the (xx-yy)
            self.line = m1.group(2)
            m2 = re.search(r"([0-9.]+)-([0-9.]+)(.*)", self.line)
            if m2:
                self.min = float(m2.group(1))
                self.max = float(m2.group(2))
                self.line_without_range = m2.group(3)[1:]

            # trigger property to update value and tooltip
            self.range = float(m1.group(1))

        # print("self.text", self.text)

    @property
    def text(self):
        """Return the text formatted for the xml output"""
        return (
            f'{self.variant_text and self.variant_text or ""}{self.crafted and "{crafted}" or ""}'
            f'{self.range and f"{{range:{self.range}}}" or ""}{self.line}'
        )

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, new_range):
        """Set a new range and update value and tooltip"""
        self._range = new_range
        self.value = self.min + (self.max - self.min) * self.range
        # get the value without the trailing .0, so we don't end up with 40.0% or such.
        value = f"{self.value:.1f}".replace(".0", "")
        # put the crafted colour on the value only
        tooltip = f'<span style="color:{ColourCodes.CRAFTED.value};">{value}' f"</span>{self.line_without_range}"
        # colour the whole tip
        self.tooltip = f'<span style="color:{self.tooltip_colour};">{tooltip}</span><br/>'
