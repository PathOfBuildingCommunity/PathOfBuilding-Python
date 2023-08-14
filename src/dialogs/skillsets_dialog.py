"""
Import dialog

Open a dialog for importing a character.
"""

from PySide6.QtWidgets import QDialog, QListWidgetItem
from PySide6.QtCore import Qt, Slot, QTimer

from PoB.pob_config import Config
from dialogs.popup_dialogs import LineEditPopup, yes_no_dialog

from ui.dlgManageSkills import Ui_ManageSkillSet


class ManageSkillsDlg(Ui_ManageSkillSet, QDialog):
    """ManageItems dialog"""

    def __init__(self, _skill_ui, _config: Config, parent=None):
        super().__init__(parent)
        self.win = parent
        self.config = _config
        self.skill_ui = _skill_ui
        self.set_to_be_moved = None
        self.set_being_edited = None
        self.triggers_connected = False

        # UI Commands below this one
        self.setupUi(self)
        for _set in self.skill_ui.skill_sets_list:
            title = _set.get("title", "Default")
            lwi = QListWidgetItem(title)
            lwi.setData(Qt.UserRole, _set)
            lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
            self.list_Skills.addItem(lwi)

        self.btnNew.clicked.connect(self.new_set)
        self.btnCopy.clicked.connect(self.duplicate_set)
        self.btnDelete.clicked.connect(self.delete_set)
        self.btnClose.clicked.connect(self.close)
        self.list_Skills.model().rowsMoved.connect(self.sets_rows_moved, Qt.QueuedConnection)
        self.list_Skills.model().rowsAboutToBeMoved.connect(self.sets_rows_about_to_be_moved, Qt.QueuedConnection)

        self.connect_triggers()
        QTimer.singleShot(50, self.on_show)  # waits for this to finish until gui displayed

    @Slot()
    def on_show(self):
        """
        Actions for when the window is shown
        """
        # Set the first row. This is because normally the selection bar is on the first item, but it's not selected
        self.list_Skills.setCurrentRow(0)

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
        if self.list_Skills.hasFocus():
            if ctrl_pressed and event.key() == Qt.Key_A:
                self.list_Skills.selectAll()
            elif ctrl_pressed and event.key() == Qt.Key_E:
                # start editing on the current item
                item = self.list_Skills.currentItem()
                if item is not None:
                    self.list_item_double_clicked(item)
                    self.list_Skills.editItem(item)
            else:
                event.ignore()
        else:
            event.ignore()
        super(ManageSkillsDlg, self).keyPressEvent(event)

    def connect_triggers(self):
        if self.triggers_connected:
            return
        self.list_Skills.itemDoubleClicked.connect(self.list_item_double_clicked)
        self.list_Skills.itemChanged.connect(self.list_item_changed)
        self.list_Skills.currentItemChanged.connect(self.list_current_item_changed)
        self.triggers_connected = True

    def disconnect_triggers(self):
        if not self.triggers_connected:
            return
        self.list_Skills.itemDoubleClicked.disconnect(self.list_item_double_clicked)
        self.list_Skills.itemChanged.disconnect(self.list_item_changed)
        self.list_Skills.currentItemChanged.disconnect(self.list_current_item_changed)
        self.triggers_connected = False

    @Slot()
    def new_set(self):
        # print("new_set")
        dlg = LineEditPopup(self.config.app.tr, "New Skill Set Name")
        dlg.placeholder_text = "New Skill Set, Rename Me"
        _return = dlg.exec()
        new_name = dlg.lineedit.text()
        if _return and new_name != "":
            new_set = self.skill_ui.new_skill_set(new_name)
            lwi = QListWidgetItem(new_name)
            lwi.setData(Qt.UserRole, new_set)
            lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
            self.list_Skills.addItem(lwi)

    @Slot()
    def duplicate_set(self):
        # print("duplicate_set")
        dlg = LineEditPopup(self.config.app.tr, "New Skill Set Name")
        dlg.placeholder_text = "New Skill Set, Rename Me"
        _return = dlg.exec()
        new_name = dlg.lineedit.text()
        if _return and new_name != "":
            row = self.list_Skills.currentRow()
            new_set = self.skill_ui.copy_skill_set(row, new_name)
            lwi = QListWidgetItem(new_name)
            lwi.setData(Qt.UserRole, new_set)
            self.list_Skills.insertItem(row + 1, lwi)

    @Slot()
    def delete_set(self):
        # print("delete_set")
        # Item in this instance is referring to the QlistWidgetItem
        copied_items = self.list_Skills.selectedItems()
        if len(copied_items) <= 0:
            return
        text = "You are about to delete the following Sets:<br><br>"
        for item in copied_items:
            text += f"<em>{item.text()}</em><br>"
        text += "<br><b>Really DO this ?</b><br>"
        if yes_no_dialog(self, "Deleting Skill Sets", text):
            for lwi in copied_items:
                _set = lwi.data(Qt.UserRole)
                self.skill_ui.delete_skill_set(_set)
                # Now remove it from the actual list
                self.list_Skills.takeItem(self.list_Skills.row(lwi))

    @Slot()
    def list_item_changed(self, lwi):
        """
        Update list item's text after the user hits enter or clicks away.
        :param lwi: QListWidgetItem:
        :return: N/A
        """
        # print("list_current_text_changed", lwi.text())
        self.set_being_edited = None
        row = self.list_Skills.currentRow()
        _set = self.skill_ui.skill_sets_list[row]
        xml_set = self.skill_ui.xml_skills[row]
        _set["title"] = lwi.text()
        xml_set["title"] = lwi.text()

    @Slot()
    def list_item_double_clicked(self, lwi):
        """
        Set up the list widget for editing this item.

        :param lwi: QListWidgetItem:
        :return: N/A
        """
        # print("list_item_double_clicked")
        self.disconnect_triggers()
        self.set_being_edited = lwi
        self.connect_triggers()

    @Slot()
    def list_current_item_changed(self, current_lwi, previous_lwi):
        """

        :param current_lwi: QListWidgetItem:
        :param previous_lwi: QListWidgetItem:
        :return: N/A
        """
        # print("list_current_item_changed", current_lwi, previous_lwi)
        if self.set_being_edited == previous_lwi and previous_lwi is not None:
            self.list_item_changed(previous_lwi)
        # Abandon previous edit
        self.set_being_edited = None

    @Slot()
    def sets_rows_moved(self, parent, start, end, destination, dest_row):
        """
        Respond to a spec being moved, by moving it's matching entry in skill_ui's list. It's called 4 times (sometimes).

        :param parent: QModelIndex: not Used.
        :param start: int: where the row was moved from.
        :param end: int: not Used. It's the same as start as multi-selection is not allowed.
        :param destination: QModelIndex: not Used.
        :param dest_row: int: The destination row.
        :return: N/A
        """
        # print("sets_rows_moved", self.set_to_be_moved, parent.row(), start, end, destination.row(), dest_row)
        # If set_to_be_moved is not None, do move in self.skill_ui and set self.set_to_be_moved = None
        # this way the last three params can be ignored.
        if self.set_to_be_moved is None:
            return
        # Do move
        self.skill_ui.move_set(start, dest_row)

        # reset to none, this one we only respond to the first call of the four.
        self.set_to_be_moved = None

    @Slot()
    def sets_rows_about_to_be_moved(self, source_parent, source_start, source_end, dest_parent, dest_row):
        """
        Setup for a spec move. It's called 4 times (sometimes)

        :param source_parent: QModelIndex: Used to notify the move
        :param source_start: int: not Used
        :param source_end: int: not Used
        :param dest_parent: QModelIndex: not Used
        :param dest_row: int: not Used
        :return: N/A
        """
        # print("sets_rows_about_to_be_moved", source_parent.row(), source_start, source_end, dest_parent.row(), dest_row)
        self.set_to_be_moved = source_parent
