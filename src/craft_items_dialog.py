"""
Craft Items dialog

Open a dialog for crafting items.
"""

import xml.etree.ElementTree as ET
import re

from qdarktheme.qtpy.QtWidgets import QDialog, QDialogButtonBox
from qdarktheme.qtpy.QtCore import Slot

from dlg_CraftItems import Ui_CraftItems
from pob_config import Config
from item import Item
from build import Build


class CraftItemsDlg(Ui_CraftItems, QDialog):
    """Craft Items dialog"""

    def __init__(self, _config: Config, _base_items, parent=None):
        super().__init__(parent)
        self.config = _config

        self._item = None
        # copy a copy of the item as passed in for
        self.original_item = Item(_base_items)
        self.setupUi(self)

        self.btnBox.addButton("Discard", QDialogButtonBox.RejectRole)
        self.btnBox.addButton("Import", QDialogButtonBox.AcceptRole)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)
        btn_reset = self.btnBox.button(QDialogButtonBox.Reset)
        btn_reset.clicked.connect(self.reset)

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, newitem: Item):
        self._item = newitem
        # go via text so we get a unique python object
        self.original_item.load_from_xml_v2(newitem.save_v2())
        self.fill_widgets()

    def fill_widgets(self):
        return

    @Slot()
    def reset(self):
        """React to the Reset button being pressed"""
        # go via text so we get a unique python object
        self._item.load_from_xml_v2(self.original_item.save_v2())
        self.fill_widgets()

    @Slot()
    def discard(self):
        """React to the Discard button being pressed"""
        self.close()
