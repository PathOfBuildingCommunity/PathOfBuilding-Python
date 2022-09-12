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

from PoB_Main_Window import Ui_MainWindow
from pob_config import Config, _debug, index_exists, str_to_bool, bool_to_str
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

    def load(self, _items):
        """
        Load internal structures from the build object.

        :param _items: Reference to the xml <Items> tag set
        :return: N/A
        """
        self.xml_items = _items
        self.clear_controls()
        # add the items to the list box
        for _item in self.xml_items.findall("Item"):
            new_item = self.add_item()
            new_item.curr_variant = _item.get("variant", "")
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
        self.influences = {}
        self.two_hand = False
        self.corrupted = False
        self.sockets = ""
        self.properties = {}
        self.limits = 0
        self.implicitMods = []
        self.explicitMods = []
        self.full_explicitMods_list = []

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
        plicits_idx, line_idx = (0, 0)
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
                        plicits_idx = line_idx
                        break
                self.properties[m.group(1)] = m.group(2)
            else:
                # skip this line
                line_idx += 1
        # every thing that is left, from plicits_idx, is explicits
        for idx in range(plicits_idx, len(lines)):
            line = lines.pop(plicits_idx)
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
                self.influences[line] = True
            else:
                m = re.search(r"Requires (.*)", line)
                if m:
                    self.requires[m.group(1)] = True
                else:
                    # do something else
                    match line:
                        case _:
                            print(f"Item().load_from_xml: Skipped: {line}")

    def load_from_json(self, json: dict):
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

        self.title = json["name"]
        self.base_name = json["typeLine"]
        self.name = f"{self.title}, {self.base_name}"
        self.unique_id = json["id"]
        self.slot = slot_map[json["inventoryId"]]
        self.rarity = rarity_map[int(json.get("frameType", 0))]
        self.full_explicitMods_list = json["explicitMods"]
        self.implicitMods = json.get("implicitMods", [])
        self.properties = json["properties"]
        self.ilevel = json["ilvl"]
        if str_to_bool(json.get("shaper", "False")):
            self.influences["Shaper Item"] = True
        if str_to_bool(json.get("elder", "False")):
            self.influences["Elder Item"] = True
        self.quality = get_property(json["properties"], "Quality", "0")
        self.level_req = get_property(json["requirements"], "Level", "0")
        # Process sockets and their grouping
        if json.get("sockets", None) is not None:
            current_socket_group_number = -1
            socket_line = ""
            for socket in json["sockets"]:
                this_group = socket["group"]
                if this_group == current_socket_group_number:
                    socket_line += f"-{socket['sColour']}"
                else:
                    socket_line += f" {socket['sColour']}"
                    current_socket_group_number = this_group
            # there will always be a leading space from the routine above
            self.sockets = socket_line.strip()

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
            f'<tr><th>'
        )
        name = self.title == "" and self.base_name or self.name
        tip += f'<span style="color:{rarity_colour};">{name}</span>'
        for influence in self.influences.keys():
            tip += f'<br/><span style="color:{influence_colours[influence]};">{influence}</span>'
        tip += '</th></tr>'
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
                tip += mod.tooltip
            # mod tooltip's always end in <br/>, remove the last one
            tip = tip[:-4]
            tip += f"</td></tr>"

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
        return "Shaper" in self.influences.keys()

    @property
    def elder(self):
        return "Elder" in self.influences.keys()

    @property
    def warlord(self):
        return "Warlord" in self.influences.keys()

    @property
    def hunter(self):
        return "Hunter" in self.influences.keys()

    @property
    def crusader(self):
        return "Crusader" in self.influences.keys()

    @property
    def redeemer(self):
        return "Redeemer" in self.influences.keys()

    @property
    def exarch(self):
        return "Exarch" in self.influences.keys()

    @property
    def eater(self):
        return "Eater" in self.influences.keys()


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
        """ Return the text formatted for the xml output """
        return f'{self.variant_text and self.variant_text or ""}{self.crafted and "{crafted}" or ""}' \
               f'{self.range and f"{{range:{self.range}}}" or ""}{self.line}'

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, new_range):
        """ Set a new range and update value and tooltip """
        self._range = new_range
        self.value = self.min + (self.max - self.min) * self.range
        # get the value without the trailing .0, so we don't end up with 40.0% or such.
        value = f"{self.value:.1f}".replace(".0", "")
        # put the crafted colour on the value only
        tooltip = f'<span style="color:{ColourCodes.CRAFTED.value};">{value}' \
                  f'</span>{self.line_without_range}'
        # colour the whole tip
        self.tooltip = f'<span style="color:{self.tooltip_colour};">{tooltip}</span><br/>'
