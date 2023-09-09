"""
Import dialog

Open a dialog for importing a character.
"""

import urllib3
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialog, QListWidgetItem

from PoB.settings import Settings
from PoB.build import Build, _debug, print_call_stack
from PoB.constants import _VERSION, _VERSION_str, tree_versions
from dialogs.popup_dialogs import yes_no_dialog, NewTreePopup

from ui.PoB_Main_Window import Ui_MainWindow
from ui.dlgManageTree import Ui_ManageTree


class ManageTreeDlg(Ui_ManageTree, QDialog):
    """Manage Trees dialog"""

    def __init__(self, _build: Build, _settings: Settings, _win: Ui_MainWindow = None):
        """
        ManageItems dialog init
        :param _build: A pointer to the currently loaded build
        :param _settings: A pointer to the settings
        :param _win: A pointer to MainWindow
        """
        super().__init__(_win)
        self.build = _build
        self.settings = _settings
        self.win = _win
        self.spec_to_be_moved = None
        self.item_being_edited = None
        self.triggers_connected = False

        self.setupUi(self)

        for spec in self.build.specs:
            title = spec.title
            lwi = QListWidgetItem(title)
            lwi.setData(Qt.UserRole, spec)
            lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
            self.list_Trees.addItem(lwi)

        self.list_Trees.setFocus()
        self.list_Trees.setCurrentRow(0)
        self.add_detail_to_spec_names()  # turns on triggers

        self.btnConvert.setToolTip(self.btnConvert.toolTip().replace("_VERSION", f"{_VERSION}"))

        self.btnNew.clicked.connect(self.new_spec)
        self.btnCopy.clicked.connect(self.duplicate_specs)
        self.btnConvert.clicked.connect(self.convert_specs)
        self.btnDelete.clicked.connect(self.delete_specs)
        self.btnClose.clicked.connect(self.close)
        self.list_Trees.model().rowsMoved.connect(self.specs_rows_moved, Qt.QueuedConnection)
        self.list_Trees.model().rowsAboutToBeMoved.connect(self.specs_rows_about_to_be_moved, Qt.QueuedConnection)

    def connect_triggers(self):
        # print("connect_triggers", self.triggers_connected)
        # print_call_stack(True)
        if self.triggers_connected:
            return
        self.list_Trees.itemDoubleClicked.connect(self.list_item_double_clicked)
        self.list_Trees.itemChanged.connect(self.list_item_changed)
        self.list_Trees.currentItemChanged.connect(self.list_current_item_changed)
        self.triggers_connected = True

    def disconnect_triggers(self):
        # print("disconnect_triggers", self.triggers_connected)
        # print_call_stack(True)
        if not self.triggers_connected:
            return
        self.list_Trees.itemDoubleClicked.disconnect(self.list_item_double_clicked)
        self.list_Trees.itemChanged.disconnect(self.list_item_changed)
        self.list_Trees.currentItemChanged.disconnect(self.list_current_item_changed)
        self.triggers_connected = False

    def add_detail_to_spec_names(self):
        """
        Add the tree version and other information to the spec title

        :return:
        """
        self.disconnect_triggers()
        for idx, spec in enumerate(self.build.specs):
            text = spec.treeVersion != _VERSION_str and f"[{tree_versions[spec.treeVersion]}] {spec.title}" or spec.title
            text += f" ({spec.ascendClassId_str()}, {len(spec.nodes)} points)"
            self.list_Trees.item(idx).setText(text)
        self.connect_triggers()

    # Overridden function
    def keyReleaseEvent(self, event):
        """

        :param: QKeyEvent. The event matrix
        :return:
        """
        # https://doc.qt.io/qtforpython/PySide6/QtGui/QKeyEvent.html#detailed-description
        # A key event contains a special accept flag that indicates whether the receiver will handle the key event.
        # This flag is set by default for KeyPress and KeyRelease, so there is no need to call accept() when
        # acting on a key event.
        ctrl_pressed = event.keyCombination().keyboardModifiers() == Qt.ControlModifier
        # print(event)
        if self.list_Trees.hasFocus():
            if ctrl_pressed and event.key() == Qt.Key_A:
                self.list_Trees.selectAll()
            elif ctrl_pressed and event.key() == Qt.Key_E:
                # start editing on the current item
                item = self.list_Trees.currentItem()
                if item is not None:
                    self.list_item_double_clicked(item)
                    self.list_Trees.editItem(item)
            else:
                event.ignore()
        else:
            event.ignore()
        super(ManageTreeDlg, self).keyPressEvent(event)

    def duplicate_specs(self):
        """Duplicate selected rows, adding a new one after the selected row"""
        selected_items = sorted(self.list_Trees.selectedItems())
        if len(selected_items) <= 0:
            return
        for item in selected_items:
            row = self.list_Trees.row(item)
            spec = self.build.copy_spec(row, row + 1)
            self.list_Trees.insertItem(row + 1, spec.title)
        self.add_detail_to_spec_names()

    def convert_specs(self):
        """Convert selected rows, adding the new one after the selected row"""
        # print("manage.convert_specs")
        selected_items = sorted(self.list_Trees.selectedItems())
        if len(selected_items) <= 0:
            return
        for item in selected_items:
            row = self.list_Trees.row(item)
            spec = self.build.specs[row]
            if spec.treeVersion != _VERSION_str:
                spec = self.build.convert_spec(row, row + 1)
                self.list_Trees.insertItem(row + 1, spec.title)
        self.add_detail_to_spec_names()

    def delete_specs(self):
        copied_items = self.list_Trees.selectedItems()
        if len(copied_items) <= 0:
            return
        text = "You are about to delete the following Passives Trees\n"
        for item in copied_items:
            text += f"{item.text()}\n"
        text += "\nReally DO this ?\n"
        if yes_no_dialog(self, "Deleting Passives Trees", text):
            for item in copied_items:
                index = self.list_Trees.row(item)
                self.list_Trees.takeItem(index)
                self.build.delete_spec(index)

    @Slot()
    def new_spec(self):
        """Add a new empty tree to the list"""
        # print("new_spec")
        dlg = NewTreePopup(self.settings.app.tr, self.win)
        _return = dlg.exec()
        new_name = dlg.lineedit.text()
        version = dlg.combo_tree_version.currentData()
        if _return and new_name != "":
            spec = self.build.new_spec(new_name, version)
            lwi = QListWidgetItem(new_name)
            lwi.setData(Qt.UserRole, spec)
            lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
            self.list_Trees.addItem(lwi)
            self.add_detail_to_spec_names()

    @Slot()
    def list_item_changed(self, lwi):
        """Update line text after the user hits enter or clicks away"""
        # print("list_current_text_changed", item.text())
        self.item_being_edited = None
        row = self.list_Trees.currentRow()
        self.build.specs[row].title = lwi.text()
        self.add_detail_to_spec_names()

    @Slot()
    def list_item_double_clicked(self, lwi):
        """
        Set up the list widget for editing this item.

        :param lwi: QListWidgetItem:
        :return: N/A
        """
        self.disconnect_triggers()
        self.item_being_edited = lwi
        # Reset the text, removing the spec version information
        row = self.list_Trees.currentRow()
        lwi.setText(self.build.specs[row].title)
        self.connect_triggers()

    @Slot()
    def list_current_item_changed(self, current_lwi, previous_lwi):
        """

        :param current_lwi: QListWidgetItem:
        :param previous_lwi: QListWidgetItem:
        :return: N/A
        """
        print("list_current_item_changed", current_lwi, previous_lwi)
        if self.item_being_edited == previous_lwi:
            self.list_item_changed(previous_lwi)
            self.add_detail_to_spec_names()
        # Abandon previous edit
        self.item_being_edited = None

    @Slot()
    def specs_rows_moved(self, parent, start, end, destination, dest_row):
        """
        Respond to a spec being moved, by moving it's matching entry in build's list. It's called 4 times (sometimes)

        :param parent: QModelIndex: not Used.
        :param start: int: where the row was moved from.
        :param end: int: not Used. It's the same as start as multi-selection is not allowed.
        :param destination: QModelIndex: not Used.
        :param dest_row: int: The destination row.
        :return: N/A
        """
        # print("specs_rows_moved")
        # if not None, do move in self.build.specs and set self.spec_to_be_moved = None
        # this way the last three are ignored.
        if self.spec_to_be_moved is None:
            return
        # Do move
        self.build.move_spec(start, dest_row)

        # reset to none, this one we only respond to the first call of the four.
        self.spec_to_be_moved = None

    @Slot()
    def specs_rows_about_to_be_moved(
        self,
        source_parent,
        source_start,
        source_end,
        dest_parent,
        dest_row,
    ):
        """
        Setup for a spec move. It's called 4 times (sometimes)

        :param source_parent: QModelIndex: Used to notify the move
        :param source_start: int: not Used
        :param source_end: int: not Used
        :param dest_parent: QModelIndex: not Used
        :param dest_row: int: not Used
        :return: N/A
        """
        # print("specs_rows_about_to_be_moved")
        self.spec_to_be_moved = source_parent
