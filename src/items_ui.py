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
            new_item.load_from_xml(_item.text)
            self.add_item_to_item_list(new_item)
            new_item.variant = int(_item.get("variant", -1))
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
        self.variant = -1
        self.unique_id = ""
        self.spec_item = {}
        self.requires = {}
        self.shaper = False
        self.elder = False
        self.two_hand = False
        self.sockets = ""
        self.properties = {}
        self.limits = 0
        self.implicitMods = []
        self.explicitMods = []

    def load_from_xml(self, desc):
        """
        Load internal structures from the build object's xml
        """
        # split lines into a list, removing any blank lines, leading & trailing spaces.
        # stolen from https://stackoverflow.com/questions/7630273/convert-multiline-into-list
        lines = [y for y in (x.strip() for x in desc.splitlines()) if y]
        # Entries like 'Shaper Item' are idiotically in the middle of the : separated variables
        # lets get all the : separated variables first and remove them from the lines list
        implicits, plicits_idx, line_idx = (0, 0, 0)
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
                            self.implicitMods.append(lines.pop(line_idx))
                        plicits_idx = line_idx
                    case _:
                        self.properties[m.group(1)] = m.group(2)
            else:
                # skip this line
                line_idx += 1
        # every thing that is left, from plicits_idx, is explicits
        for idx in range(plicits_idx, len(lines)):
            self.explicitMods.append(lines.pop(plicits_idx))
        # _debug("b", len(lines), lines)
        # 'normal' and Magic ? objects and flasks only have one line (either no title or no base name)
        if len(lines) == 1:
            self.name = lines.pop(0)
            match self.rarity:
                case "MAGIC":
                    self.title = self.name
                case "NORMAL":
                    self.base_name = self.name
        else:
            self.title = lines.pop(0)
            self.base_name = lines.pop(0)
            self.name = f"{self.title}, {self.base_name}"
        # _debug("c", len(lines), lines)

        # Anything left must be something like 'Shaper Item'
        for idx, line in enumerate(lines):
            m = re.search(r"(.*) Item", line)
            if m:
                self.spec_item[m.group(1)] = True
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
            Get a property from a list of property tags. Not all properties appear mandatory.

            :param _json_item: the gem reference from the json download
            :param _name: the name of the property
            :param _default: a default value to be used if the property is not listed
            :return:
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
        self.explicitMods = json["explicitMods"]
        self.implicitMods = json.get("implicitMods", [])
        self.properties = json["properties"]
        self.ilevel = json["ilvl"]
        self.shaper = str_to_bool(json.get("shaper", "False"))
        self.quality = get_property(json["properties"], "Quality", "0")
        self.level_req = get_property(json["requirements"], "Level", "0")
        # flasks, at least, don't have sockets (yet)
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
            # there will always be a leading space
            self.sockets = socket_line.strip()

    def save(self):
        """
        Save internal structures back to a xml object

        :return: ET.ElementTree:
        """
        pass

    def tooltip(self):
        """
        Create a tooltip

        :return: str: the tooltip
        """
        rarity_colour = f"{ColourCodes[self.rarity].value};"
        crafted_colour = f"{ColourCodes.CRAFTED.value};"
        tip = (
            f"<style>"
            f"table, th, td {{border: 1px solid {rarity_colour}; border-collapse: collapse;}}"
            f"td {{text-align: center;}}"
            f"</style>"
            f'<table width="425">'
            f'<tr><th><span style="color:{rarity_colour};">{self.name}</span></th></tr>'
        )
        if self.level_req > 0:
            tip += f"<tr><td>Requires Level <b>{self.level_req}</b></td></tr>"
        if self.limits > 0:
            tip += f"<tr><td>Limited to: <b>{self.limits}</b></td></tr>"
        if len(self.implicitMods) > 0:
            tip += f"<tr><td>"
            for idx, line in enumerate(self.implicitMods):
                colour = "crafted" in line and ColourCodes.CRAFTED.value or ColourCodes.MAGIC.value
                tip += f'<span style="color:{colour};">{line.replace("{crafted}","")}</span><br/>'
            # remove the last BR
            tip = tip[:-4]
            tip += f"</td></tr>"
        if len(self.explicitMods) > 0:
            tip += f"<tr><td>"
            for idx, line in enumerate(self.explicitMods):
                tip += f"{line}<br/>"
            # remove the last BR
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
