"""
A class to show and manage the item slots ui on the left hand side of the Items tab.
"""

import xml.etree.ElementTree as ET

from qdarktheme.qtpy.QtCore import QRect, Slot, QSize, Qt
from qdarktheme.qtpy.QtGui import QColor, QBrush, QIcon
from qdarktheme.qtpy.QtWidgets import QComboBox, QLabel, QListWidgetItem, QSpinBox, QWidget

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

        :param title: string: the text for the label
        :param my_list_item:QListWidgetItem: the item in the list box that this instance is attached to
        :param parent_notify: function: function to call when a change has happened
        """
        super(ItemSlotUI, self).__init__()

        self.widget_height = 24
        # self.setGeometry(0, 0, 320, self.widget_height)
        self.setMinimumHeight(self.widget_height)

        self.label = QLabel(self)
        self.label.setText(f"{title}:")
        self.label.setGeometry(QRect(1, 5, indent and 95 or 85, 22))
        self.label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.combo_item_list = QComboBox(self)
        self.combo_item_list.setGeometry(QRect(indent and 100 or 90, 3, indent and 370 or 380, 22))
        self.combo_item_list.setDuplicatesEnabled(True)
        self.combo_item_list.addItem("None", 0)

    def sizeHint(self) -> QSize:
        """Return a known size. Without this the default row height is about 22"""
        return QSize(self.label.width() + self.combo_item_list.width() + 5, self.widget_height)

    def add_item(self, item: Item):
        """add an item to the drop down"""

    def del_item(self, item: Item):
        """delete an item from the drop down"""
