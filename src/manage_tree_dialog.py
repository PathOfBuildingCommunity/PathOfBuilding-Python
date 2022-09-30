"""
Import dialog

Open a dialog for importing a character.
"""

import urllib3

from qdarktheme.qtpy.QtCore import Qt, Slot
from qdarktheme.qtpy.QtWidgets import QDialog

# from qdarktheme.qtpy.QtGui import

from dlg_ManageTree import Ui_Dialog
from build import Build
from constants import _VERSION, _VERSION_str


class ManageTreeDlg(Ui_Dialog, QDialog):
    """Manage Trees dialog"""

    def __init__(self, _build: Build, parent=None):
        super().__init__(parent)
        self.build = _build
        self.http = urllib3.PoolManager()
        self.spec_to_be_moved = None
        self.triggers_connected = False
        self.item_being_edited = None

        self.setupUi(self)

        for spec in self.build.specs:
            self.list_Trees.addItem(spec.title)
            # if spec.treeVersion != _VERSION_str:
            #     title = f"[{spec.treeVersion}] {spec.title}"
            # else:
            #     title = spec.title
            # self.list_Trees.addItem(title)

        self.list_Trees.setFocus()
        self.list_Trees.setCurrentRow(0)
        for index in range(self.list_Trees.count()):
            item = self.list_Trees.item(index)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.add_detail_to_spec_name()

        self.btnConvert.setToolTip(self.btnConvert.toolTip().replace("_VERSION", f"{_VERSION}"))
        self.btnNew.setToolTip(self.btnNew.toolTip().replace("_VERSION", f"{_VERSION}"))
        self.btnNew.clicked.connect(self.new_spec)
        self.btnClose.clicked.connect(self.close)
        self.list_Trees.model().rowsMoved.connect(self.specs_rows_moved, Qt.QueuedConnection)
        self.list_Trees.model().rowsAboutToBeMoved.connect(self.specs_rows_about_to_be_moved, Qt.QueuedConnection)

    def connect_triggers(self):
        if self.triggers_connected:
            return
        self.list_Trees.itemDoubleClicked.connect(self.list_item_double_clicked)
        self.list_Trees.itemChanged.connect(self.list_item_changed)
        self.list_Trees.currentItemChanged.connect(self.list_current_item_changed)
        self.triggers_connected = True

    def disconnect_triggers(self):
        if not self.triggers_connected:
            return
        self.list_Trees.itemDoubleClicked.disconnect(self.list_item_double_clicked)
        self.list_Trees.itemChanged.disconnect(self.list_item_changed)
        self.list_Trees.currentItemChanged.disconnect(self.list_current_item_changed)
        self.triggers_connected = False

    def add_detail_to_spec_name(self):
        """
        Add the tree version and other information to the spec title

        :return:
        """
        self.disconnect_triggers()
        for idx, spec in enumerate(self.build.specs):
            text = spec.treeVersion != _VERSION_str and f"[{spec.treeVersion}] {spec.title}" or spec.title
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
            else:
                event.ignore()
        else:
            event.ignore()

        super(ManageTreeDlg, self).keyPressEvent(event)

    def duplicate_rows(self):
        """Duplicate selected rows, adding a new one after the selected row"""
        print("Ctrl-C")
        print(self.list_Trees.selectedItems())

    def delete_rows(self):
        print("Delete")

    @Slot()
    def new_spec(self):
        """Add a new empty tree to the list"""
        # print("new_spec")
        spec = self.build.new_spec("New tree, Rename Me")
        self.list_Trees.addItem(spec.title)

    @Slot()
    def list_item_changed(self, item):
        print("list_current_text_changed", item.text())
        self.item_being_edited = None
        row = self.list_Trees.currentRow()
        self.build.specs[row].title = item.text()
        self.add_detail_to_spec_name()

    @Slot()
    def list_item_double_clicked(self, item):
        """
        Set up the list widget for editing this item.

        :param item: QListWidgetItem:
        :return: N/A
        """
        # print("list_item_double_clicked", item.text())
        self.disconnect_triggers()
        self.item_being_edited = item
        row = self.list_Trees.currentRow()
        item.setText(self.build.specs[row].title)
        self.connect_triggers()

    @Slot()
    def list_current_item_changed(self, current, previous):
        """

        :param current: QListWidgetItem:
        :param previous: QListWidgetItem:
        :return: N/A
        """
        # print("list_current_item_changed", current, previous, self.item_being_edited)
        # print("list_current_item_changed", current.text(), previous.text())
        if self.item_being_edited == previous:
            # Abandon previous edit
            self.item_being_edited = None
            self.add_detail_to_spec_name()

    @Slot()
    def specs_rows_moved(self, parent, start, end, destination, destination_row):
        """
        Respond to a spec being moved, by moving it's matching entry in build's list. It's called 4 times (sometimes)

        :param parent: QModelIndex: not Used.
        :param start: int: where the row was moved from.
        :param end: int: not Used. It's the same as start as multi-selection is not allowed.
        :param destination: QModelIndex: not Used.
        :param destination_row: int: The destination row.
        :return: N/A
        """
        # print("specs_rows_moved")
        # if not None, do move in self.build.specs and set self.spec_to_be_moved = None
        # this way the last three are ignored.
        if self.spec_to_be_moved is None:
            return
        # Do move
        self.build.move_spec(start, destination_row)

        # reset to none, this one we only respond to the first call of the four.
        self.spec_to_be_moved = None

    @Slot()
    def specs_rows_about_to_be_moved(
        self, source_parent, source_start, source_end, destination_parent, destination_row
    ):
        """
        Setup for a spec move. It's called 4 times (sometimes)

        :param source_parent: QModelIndex: Used to notify the move
        :param source_start: int: not Used
        :param source_end: int: not Used
        :param destination_parent: QModelIndex: not Used
        :param destination_row: int: not Used
        :return: N/A
        """
        print("specs_rows_about_to_be_moved")
        self.spec_to_be_moved = source_parent
