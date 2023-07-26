"""
Craft Items dialog

Open a dialog for crafting items.
"""

import xml.etree.ElementTree as ET
import re

from qdarktheme.qtpy.QtWidgets import QDialog, QDialogButtonBox
from qdarktheme.qtpy.QtCore import Qt, Slot
from qdarktheme.qtpy.QtGui import QColor, QBrush, QIcon

from ui.dlgCraftItems import Ui_CraftItems
from pob_config import Config
from item import Item
from widgets.ui_utils import set_combo_index_by_text
from constants import ColourCodes


class CraftItemsDlg(Ui_CraftItems, QDialog):
    """Craft Items dialog"""

    def __init__(self, _config: Config, _base_items, _mods, import_item=False, parent=None):
        """

        :param _config:
        :param _base_items:
        :param import_item: bool: True if importing an item
        :param parent:
        """
        super().__init__(parent)
        self.config = _config
        self.base_items = _base_items
        self.mods = _mods

        # duplicate of the item as passed in
        self._item = Item(_base_items)
        # save a copy of the item as passed in for recovering if dlg cancelled or reset is used.
        self.original_item = None
        self.setupUi(self)
        self.triggers_connected = False

        self.btnBox.addButton("Discard", QDialogButtonBox.RejectRole)
        if import_item:
            self.btnBox.addButton("Add to Build", QDialogButtonBox.AcceptRole)
        else:
            self.btnBox.addButton("Save", QDialogButtonBox.AcceptRole)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)
        btn_reset = self.btnBox.button(QDialogButtonBox.Reset)
        btn_reset.clicked.connect(self.reset)

        self.max_num_sockets = 0
        self.socket_widgets = [
            self.combo_Socket1,
            self.combo_Socket2,
            self.combo_Socket3,
            self.combo_Socket4,
            self.combo_Socket5,
            self.combo_Socket6,
        ]
        self.socket_connectors = [
            self.check_Connector1,
            self.check_Connector2,
            self.check_Connector3,
            self.check_Connector4,
            self.check_Connector5,
        ]
        # fill the socket combos with coloured letters
        for combo in self.socket_widgets:
            combo.clear()
            for idx, letter in enumerate("RBGAW"):
                combo.addItem(letter)
                combo.setItemData(idx, QBrush(ColourCodes[letter].value), Qt.ForegroundRole)

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, newitem: Item):
        self.original_item = newitem
        # go via text so we get a unique python object
        self._item.load_from_xml_v2(newitem.save_v2())
        self.fill_widgets()

    def connect_triggers(self):
        if self.triggers_connected:
            return
        for idx in range(len(self.socket_widgets)):
            self.socket_widgets[idx].currentTextChanged.connect(self.change_socket_combo)
        for idx in range(len(self.socket_connectors)):
            self.socket_connectors[idx].stateChanged.connect(self.change_socket_combo)

    def disconnect_triggers(self):
        if not self.triggers_connected:
            return
        for idx in range(len(self.socket_widgets)):
            self.socket_widgets[idx].currentTextChanged.disconnect(self.change_socket_combo)
        for idx in range(len(self.socket_connectors)):
            self.socket_connectors[idx].stateChanged.disconnect(self.change_socket_combo)

    def fill_widgets(self):
        self.disconnect_triggers()

        self.setWindowTitle(self.item.name)
        self.label_Item.setText(self.item.tooltip())
        base_item = self.base_items[self.item.base_name]
        self.max_num_sockets = base_item.get("max_num_sockets", 0)
        # Hide unused socket combos and connectors
        if self.max_num_sockets != 6:
            for idx in range(self.max_num_sockets, 6):
                self.socket_widgets[idx].setHidden(True)
            for idx in range(self.max_num_sockets - 1, 5):
                self.socket_connectors[idx].setHidden(True)

        # Ensure there is a proper socket setup
        if self.item.sockets == "":
            self.item.sockets = base_item.get("initial_sockets", "")
        sockets = self.item.sockets
        if sockets:
            for idx, socket in enumerate(sockets):
                char = sockets[idx]
                match char:
                    case "R" | "G" | "B" | "W" | "A":
                        set_combo_index_by_text(self.socket_widgets[idx // 2], socket)
                        # Colour the edit box with the chosen letter's colour
                        self.socket_widgets[idx // 2].setStyleSheet(
                            f"QComboBox:!editable {{color: {ColourCodes[char].value}}}"
                        )
                    case " ":
                        self.socket_connectors[idx // 2].setChecked(False)
                    case "-":
                        self.socket_connectors[idx // 2].setChecked(True)

        self.connect_triggers()

    @Slot()
    def reset(self):
        """React to the Reset button being pressed"""
        # go via text so we get a unique python object
        del self._item
        self._item = Item(self.base_items)
        self._item.load_from_xml_v2(self.original_item.save_v2())
        self.fill_widgets()

    @Slot()
    def discard(self):
        """React to the Discard button being pressed"""
        self.close()

    @Slot()
    def change_socket_combo(self):
        """React to a socket combo being changed"""
        sockets = ""
        for idx in range(self.max_num_sockets):
            socket = self.socket_widgets[idx].currentText()
            if socket:
                if idx == 5:
                    # no trailing connector
                    sockets += socket
                else:
                    connector = self.socket_connectors[idx].isChecked() and "-" or " "
                    sockets += f'{socket}{self.socket_connectors[idx].isHidden() and "" or connector}'
                self.socket_widgets[idx].setStyleSheet(f"QComboBox:!editable {{color: {ColourCodes[socket].value}}}")
        self.item.sockets = sockets.rstrip("-").rstrip(" ")
