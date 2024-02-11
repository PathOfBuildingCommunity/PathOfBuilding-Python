"""
A class to show and manage the item slots ui on the left hand side of the Items tab.
"""

import xml.etree.ElementTree as ET

from PySide6.QtCore import Slot, QSize, Qt
from PySide6.QtGui import QColor, QBrush, QIcon
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QListWidgetItem, QSpinBox, QWidget

from PoB.item import Item
from widgets.ui_utils import _debug, print_a_xml_element, print_call_stack, set_combo_index_by_text


class ItemSlotUI(QWidget):
    """
    A class to manage one item/jewel on the left hand side of the UI
    """

    def __init__(self, title, parent_notify, indent=False) -> None:
        """
        init

        :param title: string: the text for the label.
        :param indent: bool: If the widgets is indented or not.
        :param parent_notify: function: function to call when a change has happened.
        """
        super(ItemSlotUI, self).__init__()
        self.widget_height = 26
        # self.setGeometry(0, 0, 320, self.widget_height)
        self.setMinimumHeight(self.widget_height)
        self.other_weapon_slot: ItemSlotUI = None
        self.parent_notify = parent_notify
        self.lastSelectedItem = None

        # preserve the original name, EG: "Weapon 1 Swap"
        self.slot_name = title
        if "Weapon" in title:
            self.type = "Weapon"
            match title:
                case "Weapon 1 Swap":
                    title = "Alt Weapon 1"
                case "Weapon 2 Swap":
                    title = "Alt Weapon 2"
        elif "Ring" in title:
            self.type = "Ring"
        elif "Flask" in title:
            self.type = "Flask"
        elif "Socket" in title:
            self.type = "Jewel"
        elif "Abyssal" in title:
            self.type = "AbyssJewel"
        else:
            self.type = title
        self.title = title
        self.itemPbURL = ""
        self.jewel_node_id = 0  # Only used by tree jewels

        self.label = QLabel(self)
        self.label.setMinimumSize(QSize(0, 24))
        self.label.setMaximumSize(QSize(16777215, 24))
        self.label.setText(f"{title}:")
        self.label.setGeometry(1, 5, indent and 105 or 95, 24)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.combo_item_list = QComboBox(self)
        self.combo_item_list.setMinimumSize(QSize(0, 24))
        self.combo_item_list.setMaximumSize(QSize(16777215, 24))
        self.combo_item_list.setGeometry(indent and 110 or 100, 3, indent and 320 or 330, 24)
        self.combo_item_list.setDuplicatesEnabled(True)
        self.combo_item_list.addItem("None", 0)
        self.combo_item_list.setCurrentIndex(0)
        self.combo_item_list.currentTextChanged.connect(self.combobox_change_text)
        self.combo_item_list.setInsertPolicy(QComboBox.InsertAlphabetically)

        if self.type == "Flask":
            self.cb_active = QCheckBox(self)
            # Flasks are never indented, so no need to mention it.
            self.cb_active.setGeometry(75, 5, 20, 20)
            self.label.setGeometry(1, 5, 73, 22)
        else:
            self.cb_active = None

    @property
    def current_item_id(self):
        """Get the id number of the combo's current entry"""
        item = self.combo_item_list.currentData()
        if item == 0:  # "None"
            return 0
        else:
            return item.id

    @property
    def current_item(self):
        """Get the id number of the combo's current entry"""
        item = self.combo_item_list.currentData()
        if item == 0:  # "None"
            return None
        else:
            return item

    @property
    def active(self) -> bool:
        """Return is a flask is active or not. Ignores non-flasks"""
        if self.cb_active is not None:
            return self.cb_active.isChecked()
        else:
            return False

    @active.setter
    def active(self, new_state):
        """Set flasks to active or not. Ignores non-flasks"""
        if self.cb_active is not None:
            self.cb_active.setChecked(new_state)

    def sizeHint(self) -> QSize:
        """Return a known size. Without this the default row height is about 22"""
        return QSize(self.label.width() + self.combo_item_list.width() + 5, self.widget_height)

    def add_item(self, _item: Item):
        """add an item to the drop down"""
        self.combo_item_list.addItem(_item.name, _item)
        self.combo_item_list.view().setMinimumWidth(self.combo_item_list.minimumSizeHint().width() + 50)

    def delete_item(self, _item: Item):
        """delete an item from the drop down"""
        for i in range(self.combo_item_list.count()):
            if self.combo_item_list.itemData(i) == _item:
                self.clear_item_slot(_item)
                self.combo_item_list.removeItem(i)
                return

    def clear(self):
        """clear the combo box"""
        # print("self.combo_item_list.clear")
        # for each item, self.clear_item_slot(_item)
        try:
            while self.combo_item_list.count() > 0:
                self.clear_item_slot()
                self.combo_item_list.removeItem(0)
            self.combo_item_list.addItem("None", 0)
        except RuntimeError:  # Timing error. During a clear, this is cleaned up before we complete.
            pass
        self.active = False

    @Slot()
    def combobox_change_text(self, _text):
        """Set the comboBox's tooltip"""
        # print(f"combobox_change_text, {self.slot_name=}, {_text=}")
        if self.combo_item_list.currentIndex() == 0:
            self.combo_item_list.setToolTip("")
            if self.lastSelectedItem:
                self.lastSelectedItem.active = False
            self.lastSelectedItem = None
        else:
            item = self.combo_item_list.currentData()
            if type(item) == Item:
                self.combo_item_list.setToolTip(item.tooltip())
                if self.lastSelectedItem:
                    self.lastSelectedItem.active = False
                item.active = True
                self.lastSelectedItem = item
                # Clear the other slot if this is a two-hander
                if item.two_hand:
                    self.other_weapon_slot.clear_default_item()
        self.parent_notify(self)

    def set_default_by_text(self, _text):
        """Set the combo's active item by text"""
        # print(f"set_default_by_text, slot_name: '{self.slot_name}', text: '{_text}'")
        self.combo_item_list.setCurrentText(_text)

    def set_default_item(self, item=None, _id=0):
        """
        Set a default item if there is no slot information to set it (for example json download)
        For slots with more than one entry (eg: Flasks), try to fill out slots with different items.

        :param item: The jewel's Item()
        :param _id: int: ID for matching jewel's default item
        :return: N/A
        """
        # name = ""
        # if item is not None:
        #     name = item.name
        # print(f"set_default_item, slot name: '{self.slot_name}', id: {id}, item.name: '{name}'")

        if self.combo_item_list.currentIndex() == 0 and self.combo_item_list.count() > 0:
            if item is not None:
                if self.slot_name in item.slots and item.slot is None:
                    self.clear_item_slot()
                    self.set_default_by_text(item.name)
                    item.slot = self.title
            else:
                # Split out the number for those titles that have numbers (don't use slot_name)
                title_parts = self.title[-1].split("#")
                if len(title_parts) == 0:
                    title_parts = self.title.split(" ")
                match self.type:
                    case "Flask" | "Weapon" | "Ring" | "AbyssJewel":
                        idx = int(title_parts[-1])
                        if self.combo_item_list.count() > idx:
                            self.combo_item_list.setCurrentIndex(idx)
                        else:
                            self.clear_default_item()
                    case "AbyssJewel":
                        title_parts = self.title[-1].split("#")
                        idx = int(title_parts[-1])
                        if self.combo_item_list.count() > idx:
                            self.combo_item_list.setCurrentIndex(idx)
                        else:
                            self.clear_default_item()
                    case "Jewel":
                        # Different rules for jewels
                        pass
                    case _:
                        if self.combo_item_list.count() > 1:
                            self.combo_item_list.setCurrentIndex(1)
                        else:
                            self.clear_default_item()

    def clear_item_slot(self, _item=None):
        """
        Remove the current item's slot value, or the passed in item's slot
        :param _item:
        :return:
        """
        item = _item is None and self.current_item or _item
        if item is not None:
            item.slot = ""

    def clear_default_item(self):
        """Remove the default item, so the control is blank. Useful for offhand when using a two handed Weapon"""
        self.clear_item_slot()
        self.combo_item_list.setCurrentIndex(0)
