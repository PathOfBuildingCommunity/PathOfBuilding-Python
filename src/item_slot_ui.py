"""
A class to show and manage the item slots ui on the left hand side of the Items tab.
"""

import xml.etree.ElementTree as ET

from qdarktheme.qtpy.QtCore import Slot, QSize, Qt
from qdarktheme.qtpy.QtGui import QColor, QBrush, QIcon
from qdarktheme.qtpy.QtWidgets import QCheckBox, QComboBox, QLabel, QListWidgetItem, QSpinBox, QWidget

from pob_config import Config, _debug, str_to_bool, index_exists, bool_to_str, print_a_xml_element, print_call_stack
from constants import ColourCodes, slot_map
from ui_utils import set_combo_index_by_data, set_combo_index_by_text, HTMLDelegate, html_colour_text
from popup_dialogs import yes_no_dialog
from item import Item


class ItemSlotUI(QWidget):
    """
    A class to manage one item/jewel on the left hand side of the UI
    """

    def __init__(self, title, indent=False) -> None:
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

        self.label = QLabel(self)
        self.label.setText(f"{title}:")
        self.label.setGeometry(1, 5, indent and 105 or 95, 22)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.combo_item_list = QComboBox(self)
        self.combo_item_list.setGeometry(indent and 110 or 100, 3, indent and 320 or 330, 22)
        self.combo_item_list.setDuplicatesEnabled(True)
        self.combo_item_list.addItem("None", 0)
        self.combo_item_list.setCurrentIndex(0)
        if self.type == "Flask":
            self.cb_active = QCheckBox(self)
            # Flasks are never indented, so no need to mention it.
            self.cb_active.setGeometry(75, 5, 20, 20)
            self.label.setGeometry(1, 5, 73, 22)
        else:
            self.cb_active = None

    # @property
    # def title(self):
    #     """The label's text"""
    #     return self.label.text()

    @property
    def current_item_id(self):
        """Get the id number of the combo's current entry"""
        item = self.combo_item_list.currentData()
        if item == 0:  # "None"
            return 0
        else:
            return item.id

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
                self.combo_item_list.removeItem(i)
                return

    def clear(self):
        """clear the combo box"""
        # print("self.combo_item_list.clear")
        self.combo_item_list.clear()
        self.combo_item_list.addItem("None", 0)
        self.active = False

    def set_active_item_text(self, _text):
        """Set the combo's active item by text"""
        set_combo_index_by_text(self.combo_item_list, _text)

    def set_default_item(self):
        """
        Set a default item if there is no slot information to set it (for example json download)
        For slots with more than one entry (eg: Flasks), try to fill out slots with different items.

        :return: N/A
        """
        # print("set_default_item", self.title, self.combo_item_list.currentIndex(), self.combo_item_list.count())

        if self.combo_item_list.currentIndex() == 0 and self.combo_item_list.count() > 0:
            # Split out the number for those titles that have numbers
            title_parts = self.title.split(" ")
            match self.type:
                case "Flask" | "Weapon" | "Ring":
                    idx = int(title_parts[-1])
                    if self.combo_item_list.count() > idx:
                        self.combo_item_list.setCurrentIndex(idx)
                    else:
                        self.combo_item_list.setCurrentIndex(0)
                case "AbyssJewel":
                    title_parts = self.title[-1].split("#")
                    idx = int(title_parts[-1])
                    if self.combo_item_list.count() > idx:
                        self.combo_item_list.setCurrentIndex(idx)
                    else:
                        self.combo_item_list.setCurrentIndex(0)
                case _:
                    if self.combo_item_list.count() > 1:
                        self.combo_item_list.setCurrentIndex(1)
                    else:
                        self.combo_item_list.setCurrentIndex(0)
