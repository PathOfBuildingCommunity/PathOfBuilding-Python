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
from constants import slot_map, ColourCodes, slot_names
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
        self.current_itemset = None
        self.xml_itemsets = None
        self.triggers_connected = False

        self.base_items = read_json(Path(self.pob_config.exe_dir, "Data/base_items.json"))

        # Allow us to print in colour
        delegate = HTMLDelegate()
        delegate._list = self.win.list_Items
        self.win.list_Items.setItemDelegate(delegate)

        """Create the ui elements for displaying on the left side of the tab"""
        # list of abyssal ui's for ease of hiding them during itemset changes
        self.abyssal_item_slot_ui_list = []
        # dict of all slots
        self.item_slot_ui_list = {}
        for item_label in slot_names.values():
            self.create_equipped_item_slot_ui(item_label)
        for name in ("Weapon 1", "Weapon 2", "Weapon 1 Swap", "Weapon 2 Swap", "Body Armour"):
            self.create_equipped_abyssal_socket_slots(name, 6)
        for name in ("Helmet", "Gloves", "Boots"):
            self.create_equipped_abyssal_socket_slots(name, 4)
        self.create_equipped_abyssal_socket_slots("Belt", 2)
        self.hide_equipped_items_slot_ui("Weapon 1 Swap", hidden=True)
        self.hide_equipped_items_slot_ui("Weapon 2 Swap", hidden=True)
        self.win.groupbox_SocketedJewels.setVisible(False)

        """Reformat the xml from the lua. Temporary"""
        # self.rewrite_uniques_xml()

    def connect_item_triggers(self):
        """re-connect triggers"""
        # print("connect_item_triggers", self.triggers_connected)
        # print_call_stack(idx=-4)
        if self.triggers_connected:
            # Don't re-connect
            return
        self.triggers_connected = True
        self.win.list_Items.currentItemChanged.connect(self.on_row_changed)
        self.win.btn_WeaponSwap.clicked.connect(self.weapon_swap)
        self.win.list_Items.itemDoubleClicked.connect(self.double_clicked)
        self.win.combo_ItemSet.currentIndexChanged.connect(self.change_itemset)

    def disconnect_item_triggers(self):
        """disconnect item orientated triggers when updating widgets"""
        # print("disconnect_item_triggers", self.triggers_connected)
        # print_call_stack(idx=-4)
        if not self.triggers_connected:
            # Don't disconnect if not connected
            return
        self.triggers_connected = False
        self.win.list_Items.currentItemChanged.disconnect(self.on_row_changed)
        self.win.btn_WeaponSwap.clicked.disconnect(self.weapon_swap)
        self.win.list_Items.itemDoubleClicked.disconnect(self.double_clicked)
        self.win.combo_ItemSet.currentIndexChanged.disconnect(self.change_itemset)

    def create_equipped_abyssal_socket_slots(self, item_name, number_of_sockets):
        for idx in range(number_of_sockets, 0, -1):
            ui = self.create_equipped_item_slot_ui(f"{item_name} Abyssal Socket {idx}", True, item_name)
            self.abyssal_item_slot_ui_list.append(ui)
        # for idx in range(number_of_sockets):
        #     # work out what the preceeding
        #     after = idx == 0 and item_name or f"{item_name} Abyssal Socket {idx}"
        #     ui = self.create_equipped_item_slot_ui(f"{item_name} Abyssal Socket {idx+1}", True, after)
        #     self.abyssal_item_slot_ui_list.append(ui)

    def create_equipped_item_slot_ui(self, slot_name, hidden=False, insert_after=""):
        """
        Create an item_slot_ui with the label being slot_name

        :param slot_name: str: The labels contents
        :param hidden: bool: Alt weapons are hidden by default
        :param insert_after: str: The slot_name of the item_slot_ui to insert this item_slot_ui after
        :return: item_slot_ui:
        """
        # Abyssal sockets have the item name in front, so split it out. EG: 'Belt Abyssal Socket 1'
        if "Abyssal" in slot_name:
            socket_number = slot_name.split("Socket ")
            slot_ui = ItemSlotUI(f"Abyssal #{socket_number[1]}", True)
        else:
            slot_ui = ItemSlotUI(slot_name, insert_after != "")
        # Find which list we are adding these to, Items or Sockets
        vlayout = "Socket #" in slot_name and self.win.vlayout_SocketedJewels or self.win.vlayout_EquippedItems
        if insert_after != "":
            index = vlayout.indexOf(self.item_slot_ui_list[insert_after]) + 1
            vlayout.insertWidget(index, slot_ui)
        else:
            vlayout.addWidget(slot_ui)
        self.item_slot_ui_list[slot_name] = slot_ui
        slot_ui.setHidden(hidden)
        self.win.groupbox_SocketedJewels.setVisible(self.win.vlayout_SocketedJewels.count() > 1)
        height = (
            self.win.vlayout_EquippedItems.totalSizeHint().height()
            + self.win.vlayout_SocketedJewels.totalSizeHint().height()
        )
        # +40 = to make up for other widgets on the tab
        self.win.scrollAreaWidgetContents_Items.setFixedHeight(height + 40)
        return slot_ui

    def remove_equipped_items_slot_ui(self, slot_name):
        slot_ui = self.item_slot_ui_list.get(slot_name, None)
        if slot_ui is not None:
            vlayout = "Socket #" in slot_name and self.win.vlayout_SocketedJewels or self.win.vlayout_EquippedItems
            # vlayout.removeWidget(slot_ui)
            vlayout.takeAt(vlayout.indexOf(slot_ui))
            del self.item_slot_ui_list[slot_name]
        self.win.groupbox_SocketedJewels.setVisible(self.win.vlayout_SocketedJewels.count() > 1)
        height = (
            self.win.vlayout_EquippedItems.totalSizeHint().height()
            + self.win.vlayout_SocketedJewels.totalSizeHint().height()
        )
        # +40 = to make up for other widgets on the tab
        self.win.scrollAreaWidgetContents_Items.setFixedHeight(height + 40)

    def hide_equipped_items_slot_ui(self, slot_name, hidden):
        """
        (un)Hide an slot item.

        :param slot_name: str: Index to item_ui_list
        :param hidden: bool: Whether to hide or not
        :return:
        """
        # widget_item = self.item_slot_ui_list[slot_name].my_list_item
        # self.win.list_Slots.setRowHidden(self.win.list_Slots.row(widget_item), hidden)
        slot_ui = self.item_slot_ui_list.get(slot_name, None)
        if slot_ui is not None:
            slot_ui.setHidden(hidden)

    def fill_item_slot_uis(self):
        """fill the left hand item combos with items"""
        for _id in self.itemlist_by_id:
            item = self.itemlist_by_id[_id]
            for name in self.item_slot_ui_list:
                slot = self.item_slot_ui_list[name]
                if slot.type == item.type or (item.type == "Shield" and "Weapon 2" in slot.title):
                    slot.add_item(item)

    def rewrite_uniques_xml(self):
        """Reformat the xml from the lua. Temporary"""

        uniques = {}
        u_xml = read_xml(Path(self.pob_config.exe_dir, "Data/uniques_flat.xml"))
        for child in list(u_xml.getroot()):
            # print(child.tag)
            uniques[child.tag] = []
            for _item in child.findall("Item"):
                new_item = Item(self.base_items)
                # print(_item.text)
                new_item.load_from_xml(_item)
                uniques[child.tag].append(new_item)
        new_xml = ET.ElementTree(ET.fromstring("<?xml version='1.0' encoding='utf-8'?><Uniques></Uniques>"))
        new_root = new_xml.getroot()
        new_root.insert(
            1,
            ET.Comment(
                " === At this point in time (Nov2022), variants on item types is not supported. "
                "Items are duplicated instead === "
            ),
        )
        for child_tag in uniques:
            # print(child_tag)
            child_xml = ET.fromstring(f"<{child_tag} />")
            item_type = uniques[child_tag]
            for item in item_type:
                child_xml.append(item.save_v2())
            new_root.append(child_xml)

        write_xml("Data/uniques.xml", new_xml)

        # u = read_xml(Path(self.pob_config.exe_dir, "Data/uniques.xml"))
        # for child in list(u.getroot()):
        #     for _item in child.findall("Item"):
        #         # if "Implicits:" not in _item.text:
        #         #     lines = [y for y in (x.strip() for x in _item.text.splitlines()) if y]
        #         #     print(lines[0])
        #         lines = [y for y in (x.strip() for x in _item.text.splitlines()) if y]
        #         count = 0
        #         for line in lines:
        #             if "Implicits:" in line:
        #                 count += 1
        #                 print(count, lines[0])
        #         print()
        # write_xml("c:/git/PathOfBuilding-Python/src/Data/uniques2.xml", u)

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

    def load_from_xml(self, _items):
        """
        Load internal structures from the build object.

        :param _items: Reference to the xml <Items> tag set
        :return: N/A
        """
        # print("items_ui.load_from_xml")
        self.disconnect_item_triggers()
        self.xml_items = _items
        self.clear_controls(True)
        self.win.combo_ItemSet.clear()
        # Remove <Slot /> entries under <Items /> only
        for _item in self.xml_items.findall("Slot"):
            self.xml_items.remove(_item)
        # add the items to the list box
        for _item in self.xml_items.findall("Item"):
            new_item = Item(self.base_items)
            # new_item.curr_variant = _item.get("variant", "")
            new_item.load_from_xml(_item)
            new_item.id = int(_item.get("id", 0))
            self.add_item_to_itemlist_widget(new_item)
        self.xml_itemsets = self.xml_items.findall("ItemSet")
        for _item_set in self.xml_itemsets:
            self.win.combo_ItemSet.addItem(_item_set.get("title", "Default"), _item_set)
        self.fill_item_slot_uis()
        self.win.combo_ItemSet.setCurrentIndex(0)
        self.show_itemset(0, True)
        self.connect_item_triggers()

    def load_from_json(self, _items, itemset_name, delete_it_all):
        """
        Load internal structures from the build object.

        :param _items: Reference to the downloaded json <Items> tag set
        :param itemset_name: str: A potential new name for this itemset
        :param delete_it_all: bool: delete all current items and itemsets
        :return: N/A
        """
        # print("items_ui.load_from_json")
        self.disconnect_item_triggers()
        if delete_it_all:
            self.delete_all_items()
            self.delete_all_itemsets()
        self.new_itemset(itemset_name)
        id_base = len(self.itemlist_by_id) == 0 and 1 or max(self.itemlist_by_id.keys())
        # add the items to the list box
        for idx, text_item in enumerate(_items["items"]):
            new_item = Item(self.base_items)
            new_item.load_from_json(text_item)
            new_item.id = id_base + idx
            self.add_item_to_itemlist_widget(new_item)
        self.fill_item_slot_uis()
        self.win.combo_ItemSet.setCurrentIndex(0)
        self.show_itemset(0, True)
        self.connect_item_triggers()

    def save(self):
        """
        Save internal structures back to a xml object

        :return: ET.ElementTree:
        """
        items = []
        # build a list of items from the list control
        for row in range(self.win.list_Items.count()):
            items.append(self.win.list_Items.item(row).whatsThis())

        if len(items) > 0:
            # leave this here for a bit to pick out one item
            # self.itemlist[items[0]].save(0, true)
            # delete any items present in the xml and readd them with the current data
            for child in list(self.xml_items.findall("Item")):
                self.xml_items.remove(child)
            for idx, u_id in enumerate(items, 1):
                self.xml_items.append(self.itemlist_by_uid[u_id].save_v2(idx, True))

            # Remove legacy <Slot /> entries
            for child in list(self.current_itemset.findall("Slot")):
                self.current_itemset.remove(child)
            # Add slot information
            for slot_ui_name in self.item_slot_ui_list:
                slot_ui = self.item_slot_ui_list[slot_ui_name]
                item_id = slot_ui.current_item_id
                if item_id != 0:
                    item_xml = ET.fromstring(f'<Slot name="{slot_ui_name}" itemId="{item_id}"/>')
                    if "Flask" in slot_ui_name:
                        item_xml.set("active", bool_to_str(slot_ui.active))
                    self.current_itemset.append(item_xml)

    def clear_controls(self, loading=False):
        """
        Clear certain controls on the Skills tab in preparation for reloading.

        :return: N/A
        """
        _debug("clear_controls")
        if loading:
            self.win.list_Items.clear()
            self.itemlist_by_id.clear()
            self.itemlist_by_uid.clear()
        for name in self.item_slot_ui_list:
            slot: ItemSlotUI = self.item_slot_ui_list[name]
            slot.clear()
        for slot in self.abyssal_item_slot_ui_list:
            slot.setHidden(True)
        self.win.groupbox_SocketedJewels.setHidden(True)

    def delete_all_items(self):
        """Delete all items"""
        # print("delete_all_items")
        for child in list(self.xml_items.findall("Item")):
            self.xml_items.remove(child)
        self.clear_controls(True)

    def show_itemset(self, _itemset, initial=False):
        """
        Show the nominated Item Set

        :param _itemset: int:
        :param initial: bool: Only set during loading
        :return:
        """
        _debug("show_itemset", _itemset)
        if 0 <= _itemset < len(self.xml_itemsets):
            if not initial:
                self.save()
                # self.clear_controls()
            self.current_itemset = self.xml_itemsets[_itemset]

            for slot_ui in self.abyssal_item_slot_ui_list:
                slot_ui.setHidden(True)
            # Process the Slot entries and set default items
            slots = self.current_itemset.findall("Slot")
            if len(slots) > 0:
                for slot_xml in slots:
                    # The regex is for a data error: 1Swap -> 1 Swap
                    name = re.sub(r"([12])Swap", "\\1 Swap", slot_xml.get("name", ""))
                    item_id = int(slot_xml.get("itemId", 0))
                    if name != "" and item_id != 0:
                        item = self.itemlist_by_id[item_id]
                        item_ui: ItemSlotUI = self.item_slot_ui_list[name]
                        item_ui.set_active_item_text(item.name)
                        if item.type == "Flask":
                            item_ui.active = str_to_bool(slot_xml.get("active", "False"))
                        if "Abyssal" in name:
                            item_ui.setHidden(False)
            else:
                for slot_name in self.item_slot_ui_list:
                    self.item_slot_ui_list[slot_name].set_default_item()

    def new_itemset(self, itemset_name="Default"):
        """

        :param itemset_name: str: A potential new name for this itemset
        :return: N/A
        """
        # print("new_itemset", itemset_name, len(self.xml_itemsets))
        new_itemset = ET.fromstring(f'<ItemSet useSecondWeaponSet="false" id="{len(self.xml_itemsets)+1}"/>')
        new_itemset.set("title", itemset_name)
        self.xml_itemsets.append(new_itemset)
        self.win.combo_ItemSet.addItem(itemset_name, new_itemset)
        self.change_itemset(len(self.xml_itemsets) - 1)

    def change_itemset(self, _index):
        """React to the the itemset combo being changed"""
        # _debug("change_itemset", _index)
        if 0 <= _index < len(self.xml_itemsets):
            self.show_itemset(_index)

    def delete_all_itemsets(self):
        """Delete ALL itemsets"""
        # print("delete_all_itemsets")
        for itemset in self.xml_itemsets:
            self.xml_items.remove(itemset)
        self.current_itemset = None
        self.xml_itemsets.clear()
        self.win.combo_ItemSet.clear()
