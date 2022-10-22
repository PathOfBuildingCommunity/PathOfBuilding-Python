"""
This Class manages all the elements and owns some elements of the "ITEMS" tab
"""

from pathlib import Path

from qdarktheme.qtpy.QtCore import (
    QCoreApplication,
    QDir,
    QRect,
    QRectF,
    QSize,
    QStringListModel,
    Qt,
    Signal,
    Slot,
)
from qdarktheme.qtpy.QtGui import (
    QAbstractTextDocumentLayout,
    QAction,
    QActionGroup,
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
    QTextDocument,
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
    QLayout,
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
    QItemDelegate,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
import xml.etree.ElementTree as ET
import re

from PoB_Main_Window import Ui_MainWindow
from pob_config import Config, _debug, index_exists, str_to_bool, bool_to_str, print_call_stack, print_a_xml_element
from pob_file import read_xml, write_xml, read_json
from constants import slot_map, ColourCodes
from ui_utils import HTMLDelegate, html_colour_text
from item import Item
from item_slot_ui import ItemSlotUI


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


class ItemsUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        # dictionary of Items() indexed by id. This is the same order in the xml
        self.itemlist_by_id = {}
        # dictionary of Items() indexed by unique_id. May not be in the same order as items in the GUI
        self.itemlist_by_uid = {}
        self.xml_items = None

        self.base_items = read_json(Path(self.pob_config.exe_dir, "Data/base_items.json"))

        # Allow us to print in colour
        delegate = HTMLDelegate()
        delegate._list = self.win.list_Items
        self.win.list_Items.setItemDelegate(delegate)

        self.win.list_Items.currentItemChanged.connect(self.on_row_changed)
        self.win.btn_WeaponSwap.clicked.connect(self.weapon_swap)
        self.win.list_Items.itemDoubleClicked.connect(self.double_clicked)

        self.item_ui_list = {}
        self.create_equipped_items_slot_ui("Weapon 1")
        self.create_equipped_items_slot_ui("Weapon 2")
        self.create_equipped_items_slot_ui("Weapon 1 Swap", hidden=True)
        self.create_equipped_items_slot_ui("Weapon 2 Swap", hidden=True)
        self.create_equipped_items_slot_ui("Helmet")
        self.create_equipped_items_slot_ui("Body Armour")
        self.create_equipped_items_slot_ui("Gloves")
        self.create_equipped_items_slot_ui("Boots")
        self.create_equipped_items_slot_ui("Amulet")
        self.create_equipped_items_slot_ui("Ring 1")
        self.create_equipped_items_slot_ui("Ring 2")
        self.create_equipped_items_slot_ui("Belt")
        self.create_equipped_items_slot_ui("Flask 1")
        self.create_equipped_items_slot_ui("Flask 2")
        self.create_equipped_items_slot_ui("Flask 3")
        self.create_equipped_items_slot_ui("Flask 4")
        self.create_equipped_items_slot_ui("Flask 5")
        self.win.groupbox_SocketedJewels.setVisible(False)
        # for idx in range(10):
        #     self.create_equipped_items_slot_ui(f"Socket #{idx+1}")

        # self.rewrite_uniques_xml()
        # self.uniques = {}
        # u = read_xml(Path(self.pob_config.exe_dir, "Data/uniques.xml"))
        # for child in list(u.getroot()):
        #     self.uniques[child.tag] = []
        #     for _item in child.findall("Item"):
        #         new_item = Item()
        #         # print(_item.text)
        #         new_item.load_from_xml(f"Rarity: UNIQUE\n{_item.text}")
        #         self.uniques[child.tag].append(new_item)

    def create_equipped_items_slot_ui(self, slot_name, hidden=False, insert_after=""):
        slot_ui = ItemSlotUI(slot_name, insert_after != "")
        vlayout = "Socket #" in slot_name and self.win.vlayout_SocketedJewels or self.win.vlayout_EquippedItems
        if insert_after != "":
            index = vlayout.indexOf(self.item_ui_list[insert_after]) + 1
            vlayout.insertWidget(index, slot_ui)
        else:
            vlayout.addWidget(slot_ui)
        self.item_ui_list[slot_name] = slot_ui
        slot_ui.setHidden(hidden)
        self.win.groupbox_SocketedJewels.setVisible(self.win.vlayout_SocketedJewels.count() > 1)
        # # -2 for the two hidden alt weapon item_slot_ui's
        # item_count = self.win.groupbox_Items.layout().count() + self.win.groupbox_SocketedJewels.layout().count() - 2
        # # 30 = item_slot_ui.height() + layout Spacing
        # self.win.scrollAreaWidgetContents_Items.setFixedHeight(item_count * 30)
        height = (
            self.win.vlayout_EquippedItems.totalSizeHint().height()
            + self.win.vlayout_SocketedJewels.totalSizeHint().height()
        )
        # 40 = to make for other widgets on the tab
        self.win.scrollAreaWidgetContents_Items.setFixedHeight(height + 40)
        return slot_ui

    def remove_equipped_items_slot_ui(self, slot_name):
        slot_ui = self.item_ui_list.get(slot_name, None)
        if slot_ui is not None:
            vlayout = "Socket #" in slot_name and self.win.vlayout_SocketedJewels or self.win.vlayout_EquippedItems
            # vlayout.removeWidget(slot_ui)
            vlayout.takeAt(vlayout.indexOf(slot_ui))
            del self.item_ui_list[slot_name]
        self.win.groupbox_SocketedJewels.setVisible(self.win.vlayout_SocketedJewels.count() > 1)
        # # -2 for the two hidden alt weapon item_slot_ui's
        # item_count = self.win.groupbox_Items.layout().count() + self.win.groupbox_SocketedJewels.layout().count() - 2
        # # 30 = item_slot_ui.height() + layout Spacing
        # self.win.scrollAreaWidgetContents_Items.setFixedHeight(item_count * 30)
        height = (
            self.win.vlayout_EquippedItems.totalSizeHint().height()
            + self.win.vlayout_SocketedJewels.totalSizeHint().height()
        )
        # 40 = to make for other widgets on the tab
        self.win.scrollAreaWidgetContents_Items.setFixedHeight(height + 40)

    def hide_equipped_items_slot_ui(self, slot_name, hidden):
        """
        (un)Hide an slot item.

        :param slot_name: str: Index to item_ui_list
        :param hidden: bool: Whether to hide or not
        :return:
        """
        # widget_item = self.item_ui_list[slot_name].my_list_item
        # self.win.list_Slots.setRowHidden(self.win.list_Slots.row(widget_item), hidden)
        slot_ui = self.item_ui_list.get(slot_name, None)
        if slot_ui is not None:
            slot_ui.setHidden(hidden)

    def rewrite_uniques_xml(self):
        """Reformat the xml from the lua. Temporary"""

        u = read_xml(Path(self.pob_config.exe_dir, "Data/uniques.xml"))
        for child in list(u.getroot()):
            for _item in child.findall("Item"):
                # if "Implicits:" not in _item.text:
                #     lines = [y for y in (x.strip() for x in _item.text.splitlines()) if y]
                #     print(lines[0])
                lines = [y for y in (x.strip() for x in _item.text.splitlines()) if y]
                count = 0
                for line in lines:
                    if "Implicits:" in line:
                        count += 1
                        print(count, lines[0])
                print()
        write_xml("c:/git/PathOfBuilding-Python/src/Data/uniques2.xml", u)

    def add_item_to_itemlist_widget(self, _item):
        """
        Add an Item() class to the internal list.

        :param _item: Item(). The item to be added to the list
        :return: the passed in Item() class object
        """
        self.itemlist_by_uid[_item.unique_id] = _item
        self.itemlist_by_id[_item.id] = _item
        lwi = QListWidgetItem(html_colour_text(_item.rarity, _item.name))
        lwi.setToolTip(_item.tooltip())
        lwi.setWhatsThis(_item.unique_id)
        self.win.list_Items.addItem(lwi)
        return _item

    def fill_item_slot_uis(self):
        for id in self.itemlist_by_id:
            item = self.itemlist_by_id[id]
            for name in self.item_ui_list:
                slot = self.item_ui_list[name]
                if slot.type == item.type or (item.type == "Shield" and "Weapon 2" in slot.title):
                    slot.add_item(item)

    @Slot()
    def weapon_swap(self, checked):
        """
        Switch between active and alternate weapons.

        :param checked: bool: state of the btn_WeaponSwap button. Checked = True means Alt is to be shown.
        :return: N/A
        """
        self.win.btn_WeaponSwap.setText(checked and "Show Main Weapons" or "Show Alt Weapons")
        self.hide_equipped_items_slot_ui("Weapon 1", checked)
        self.hide_equipped_items_slot_ui("Weapon 2", checked)
        self.hide_equipped_items_slot_ui("Weapon 1 Swap", not checked)
        self.hide_equipped_items_slot_ui("Weapon 2 Swap", not checked)

    @Slot()
    def define_item_labels(self):
        """
        Set item labels based on what set they are in and what set is active
        :return:
        """
        return
        # for idx, _item in enumerate(self.itemlist):
        #     label = self.win.list_Items.itemWidget(idx)
        #     label.setText(html_colour_text(_item.rarity, _item.name))
        #     # Do more here based on itemsets, etc

    @Slot()
    def on_row_changed(self, item):
        """Are there actions we want to take when the use selects a new item"""
        print("on_row_changed", item.text())

    @Slot()
    def double_clicked(self, item: QListWidgetItem):
        """Actions for editing an item"""
        print(item.text(), item.whatsThis())

    def clear_controls(self):
        """
        Clear certain controls on the Skills tab in preparation for reloading.

        :return: N/A
        """
        _debug("clear_controls")
        self.win.list_Items.clear()
        for item_ui in self.item_ui_list:
            self.item_ui_list[item_ui].combo_item_list.clear()
        for name in self.item_ui_list:
            slot = self.item_ui_list[name]
            slot.clear()

    def load_from_xml(self, _items):
        """
        Load internal structures from the build object.

        :param _items: Reference to the xml <Items> tag set
        :return: N/A
        """
        # print("load_from_xml")
        self.xml_items = _items
        self.clear_controls()
        # add the items to the list box
        for _item in self.xml_items.findall("Item"):
            new_item = Item(self.base_items)
            # new_item.curr_variant = _item.get("variant", "")
            new_item.load_from_xml(_item.text)
            new_item.id = _item.get("id", 0)
            self.add_item_to_itemlist_widget(new_item)
        for _item_set in self.xml_items.findall("ItemSet"):
            self.win.combo_ItemSet.addItem(_item_set.get("title", "Default"), _item_set)
            for _slot in _item_set.findall("Slot"):
                _name = _slot.get("name"), _slot.get("itemId")
        self.win.combo_ItemSet.setCurrentIndex(0)
        self.fill_item_slot_uis()
        # Process the Slot entries and set default items
        for slot_xml in self.xml_items.findall("Slot"):
            name = slot_xml.get("name", None)
            item_id = slot_xml.get("itemId", None)
            if name is not None and item_id is not None:
                item = self.itemlist_by_id[item_id]
                item_ui = self.item_ui_list[name]
                item_ui.set_active_item(item.name)
                if item.type == "Flask":
                    item_ui.active.setChecked(str_to_bool(slot_xml.get("active", "False")))

    def load_from_json(self, _items):
        """
        Load internal structures from the build object.

        :param _items: Reference to the downloaded json <Items> tag set
        :return: N/A
        """
        # print("load_from_json")
        self.clear_controls()
        print(_items)
        character = _items["character"]
        print("load_from_json.character", character)
        # add the items to the list box
        for text_item in _items["items"]:
            # print(text_item)
            new_item = Item(self.base_items)
            new_item.load_from_json(text_item)
            # print(vars(new_item))
            self.add_item_to_itemlist_widget(new_item)

    def save(self):
        """
        Save internal structures back to a xml object

        :return: ET.ElementTree:
        """
        items = []
        for row in range(self.win.list_Items.count()):
            items.append(self.win.list_Items.item(row).whatsThis())

        if len(items) > 0:
            # leave this here for a bit to pick out one item
            # self.itemlist[items[0]].save(0, true)
            # delete any items present and readd them with the current data
            for child in list(self.xml_items):
                self.xml_items.remove(child)
            for idx, u_id in enumerate(items):
                self.xml_items.append(self.itemlist_by_uid[u_id].save(idx + 1, True))
