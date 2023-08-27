"""
Craft Items dialog

Open a dialog for crafting items.

Note that there are six combo boxes for changing colours of sockets but only five connector widgets.
To make maths and other things easier, the array holding all the connector widgets is a 1 based array.
The array holding the colour combo widgets is 0 based, therefore the first combo has nothing to manage.
For the purposes of processing, the colour comboBox manages the connector to the left of it.
  This is because Abyssal sockets cannot be connected to normal sockets and they only seem to be to the right of the
  socket list. There is processing to force this.
"""

import xml.etree.ElementTree as ET
import re

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QMainWindow, QStatusBar
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QColor, QBrush, QIcon

from PoB.constants import ColourCodes
from PoB.settings import Settings
from PoB.item import Item
from widgets.ui_utils import html_colour_text, set_combo_index_by_text

from ui.PoB_Main_Window import Ui_MainWindow
from ui.dlgCraftItems import Ui_CraftItems


class CraftItemsDlg(Ui_CraftItems, QDialog):
    """Craft Items dialog"""

    def __init__(self, _settings: Settings, _base_items, _mods, task, _win: Ui_MainWindow = None):
        """
        Craft Items dialog init
        :param _settings: A pointer to the settings
        :param _base_items: dict: the loaded base_items.json
        :param task: str: Either "save" or "add"
        :param _win: A pointer to MainWindow
        """
        super().__init__(_win)
        self.settings = _settings
        self.base_items = _base_items
        self.mods = _mods

        # duplicate of the item as passed in
        self._item = Item(self.settings, _base_items)
        # save a copy of the item as passed in for recovering if dlg cancelled or reset is used.
        self.original_item = None
        self.setupUi(self)
        self.triggers_connected = False
        # used for rejecting changes and putting previous values back. Only has letters
        self.curr_socket_state = list()
        # used for rejecting changes and putting previous values back. Only has " " and "-"
        self.curr_connector_state = list()

        # Status bar timer
        self.sb_timer = QTimer(self)
        self.sb_timer.setTimerType(Qt.CoarseTimer)
        self.sb_timer.setSingleShot(True)
        self.sb_timer.timeout.connect(self.update_status_bar)

        self.btnBox.addButton("Discard", QDialogButtonBox.RejectRole)
        if task == "add":
            self.btnBox.addButton("Add to Build", QDialogButtonBox.AcceptRole)
        else:
            self.btnBox.addButton("Save", QDialogButtonBox.AcceptRole)
        self.btnBox.accepted.connect(self.save)
        self.btnBox.rejected.connect(self.reject)
        btn_reset = self.btnBox.button(QDialogButtonBox.Reset)
        btn_reset.clicked.connect(self.reset)

        self.max_num_sockets = 0
        self.socket_widgets = [  # 0 based array
            self.combo_Socket1,
            self.combo_Socket2,
            self.combo_Socket3,
            self.combo_Socket4,
            self.combo_Socket5,
            self.combo_Socket6,
        ]
        self.connector_widgets = [  # 1 based array
            None,
            self.check_Connector2,
            self.check_Connector3,
            self.check_Connector4,
            self.check_Connector5,
            self.check_Connector6,
        ]
        # fill the socket combos with coloured letters
        for combo in self.socket_widgets:
            combo.clear()
            for idx, letter in enumerate("RBGAW"):
                combo.addItem(letter)
                combo.setItemData(idx, QBrush(ColourCodes[letter].value), Qt.ForegroundRole)

    @property
    def sockets(self):
        # No sockets if the first combo is hidden
        if self.socket_widgets[0].isHidden():
            return ""
        _sockets = self.socket_widgets[0].currentText()
        for idx in range(1, self.max_num_sockets):
            char = self.socket_widgets[idx].currentText()
            connector = self.connector_widgets[idx].checkState() == Qt.Checked and "-" or " "
            _sockets += f"{self.connector_widgets[idx].isHidden() and '' or connector}{char}"
        return _sockets

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, newitem: Item):
        self.original_item = newitem
        # go via text so we get a unique python object
        self._item.load_from_xml_v2(newitem.save_v2())
        self.fill_widgets()
        self.update_status_bar(f"Loaded {newitem.coloured_name}")

    def fill_widgets(self):
        """Fill the widgets with default values. called when setting self.item"""
        self.setWindowTitle(self.item.name)
        self.label_Item.setText(self.item.tooltip())
        base_item = self.base_items[self.item.base_name]

        # Ensure there is a proper socket setup
        if self.item.sockets == "":
            self.item.sockets = base_item.get("initial_sockets", "")
        # Some belts have sockets, but will not have a max_num_sockets entry, so setup a new max_num_sockets.
        self.curr_socket_state = [char for char in " " + self.item.sockets if char in ("R", "G", "B", "W", "A")]
        self.curr_connector_state = [char for char in " " + self.item.sockets if char in (" ", "-")]
        self.max_num_sockets = max(base_item.get("max_num_sockets", 0), len(self.curr_socket_state))

        # Hide unused socket combos and connectors, yes this may hide them all
        if self.max_num_sockets != len(self.socket_widgets):
            for s_idx in range(self.max_num_sockets, len(self.socket_widgets)):
                self.socket_widgets[s_idx].setHidden(True)
            for c_idx in range(self.max_num_sockets, len(self.connector_widgets)):
                self.connector_widgets[c_idx].setHidden(True)

        self.connect_triggers()

        sockets = self.item.sockets
        if sockets:
            for idx, socket in enumerate(self.curr_socket_state):
                # protect against data errors (or people fiddling)
                match socket:
                    case "R" | "G" | "B" | "W" | "A":
                        set_combo_index_by_text(self.socket_widgets[idx], socket)

    def connect_triggers(self):
        def make_combo_connection(_idx, _combo):
            """
            Connect the menu item to _open_previous_build passing in extra information
            Lambdas in python share the variable scope they're created in so make a function containing just the lambda
            :param _idx: int: Current index into self.socket_widgets
            :param _combo: QComboBox: Current combo
            :return: N/A
            """
            _combo.currentTextChanged.connect(lambda text: self.change_socket_combo(text, _idx, _combo))

        def make_checkbox_connection(_idx, _checkbox):
            """
            Connect the menu item to _open_previous_build passing in extra information
            Lambdas in python share the variable scope they're created in so make a function containing just the lambda
            :param _idx: int: Current index into self.socket_widgets
            :param _checkbox: QComboBox: Current checkbox
            :return: N/A
            """
            if _checkbox:
                _checkbox.stateChanged.connect(lambda state: self.change_connector(state, _idx))

        if self.triggers_connected:
            # Don't re-connect
            return
        for idx, combo in enumerate(self.socket_widgets):
            make_combo_connection(idx, combo)
        for idx, checkbox in enumerate(self.connector_widgets):  # Remember self.connector_widgets is a 1 based array
            make_checkbox_connection(idx, checkbox)

    @Slot()
    def update_status_bar(self, message="", timeout=10):
        """
        Update the status bar. Use default text if no message is supplied.
        This triggers when the message is set and when it is cleared after the time out.
        :param message: str: the message.
        :param timeout: int: time for the message to be shown, in secs
        :return: N/A
        """
        self.label_StatusBar.setText(message)
        if message != "":
            self.sb_timer.start(timeout * 1000)

    @Slot()
    def change_socket_combo(self, socket, idx, combo: QComboBox):
        """
        React to a socket combo being changed, and change the color of the text,
          and it's associated connector, if 'A' is chosen.
        :param socket: str: The new text of the combo.
        :param idx: int: Current index into self.socket_widgets
        :param combo: QComboBox: The combo that sent it.
        :return: N/A
        """
        # print("change_socket_combo", socket, idx, combo)
        self.update_status_bar("")
        # check if the combo to right of this combo is also 'A' or hidden. If not disallow and revert.
        if idx != 6 and socket == "A" and self.socket_widgets[idx + 1].isVisible() and self.socket_widgets[idx + 1].currentText() != "A":
            combo.setCurrentText(self.curr_socket_state[idx])
            self.update_status_bar(
                html_colour_text(
                    "RED",
                    f"Rejecting Update to {socket}: Socket to the right is not 'A' ('{self.socket_widgets[idx + 1].currentText()}')",
                )
            )
            return
        # check if the combo to left of this combo is also 'A'. If it is, disallow and revert.
        elif idx != 0 and socket != "A" and self.curr_socket_state[idx] == "A" and self.socket_widgets[idx - 1].currentText() == "A":
            combo.setCurrentText(self.curr_socket_state[idx])
            self.update_status_bar(
                html_colour_text(
                    "RED",
                    f"Rejecting Update to {socket}: Socket to the left is not 'A' ('{self.socket_widgets[idx + 1].currentText()}')",
                )
            )
            return

        # Colour the edit box with the chosen letter's colour. '{{' is the fstr escape equiv of '\{'
        combo.setStyleSheet(f"QComboBox:!editable {{color: {ColourCodes[socket].value}}}")
        self.curr_socket_state[idx] = socket
        # Manage the connector to the left of combo. Left most combo doesn't have one.
        # Remember self.connector_widgets is a 1 based array
        if idx != 0:
            connector = self.connector_widgets[idx]
            match socket:
                case "R" | "G" | "B" | "W":
                    # This will also recover from 'A' being selected and restore the previous state.
                    connector.setEnabled(True)
                    connector.setTristate(False)
                    connector.setChecked(self.curr_connector_state[idx] == "-")
                case "A":
                    # Disable the connector, and set it to a red cross.
                    connector.setEnabled(False)
                    connector.setTristate(True)
                    connector.setCheckState(Qt.PartiallyChecked)

    @Slot()
    def change_connector(self, state, idx):
        """
        Update self.curr_connector_state if the state of the connector is not PartiallyChecked.
        This is so we have a restore state of the connector in case the user selects 'A' and then selects something else.
        :param state: Qt.CheckState: The current state of the connector QCheckBox.
        :param idx: int: Current index into self.socket_widgets.
        :return:
        """
        # print("change_socket_combo", Qt.CheckState(state), idx)
        self.update_status_bar("")
        match Qt.CheckState(state):
            case Qt.Checked:
                self.curr_connector_state[idx] = "-"
            case Qt.Unchecked:
                self.curr_connector_state[idx] = " "
            # ignore Qt.PartiallyChecked. Don't update self.curr_connector_state for the 'A' socket being selected.

    @Slot()
    def reset(self):
        """React to the Reset button being pressed. Restore self.item from self.original_item.
        Trigger fill_widgets by setting self.item"""
        self.update_status_bar("")
        del self._item
        _item = Item(self.settings, self.base_items)
        # go via text so we get a unique python object
        _item.load_from_xml_v2(self.original_item.save_v2())
        self.item = _item

    @Slot()
    def discard(self):
        """React to the Discard button being pressed"""
        self.close()

    @Slot()
    def save(self):
        """
        Save any information to self.item. Used by AcceptRole button
        :return: N/A
        """
        self.item.sockets = self.sockets
        self.accept()
