"""
simple popups that don't need complex activities to load or execute them
"""

from qdarktheme.qtpy.QtCore import Slot, Qt, QSize
from qdarktheme.qtpy.QtGui import QTextDocument
from qdarktheme.qtpy.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from constants import ColourCodes
from ui_utils import HTMLDelegate, html_colour_text


def yes_no_dialog(win, title, text):
    """Return true if the user selects Yes."""
    return QMessageBox.question(win, title, text, QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes


def ok_dialog(win, title, text, btn_text="OK"):
    """Notify the user of some information."""
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Information)
    dlg.exec_()


def critical_dialog(win, title, text, btn_text="Close"):
    """Notify the user of some critical? information."""
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Critical)
    dlg.exec_()


"""######## MasteryPopup. Choose a mastery from the passed in Node ########"""


class MasteryPopup(QDialog):
    def __init__(self, node, current_effect=-1):
        """
        Choose a mastery from the passed in Node.

        :param node: node(): this mastery
        :param current_effect: int: the currect effect if set
        """
        super().__init__()

        self.id = node.id
        self.effects = node.masteryEffects
        self.selected_effect = current_effect
        self.selected_row = -1
        self.starting = True

        self.setWindowTitle(node.name)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.listbox = QListWidget()
        for idx, effect in enumerate(self.effects):
            stats = " ".join(effect["stats"])
            item = QListWidgetItem()
            item.setText(html_colour_text("WHITE", stats))
            tooltip = effect.get("reminderText", None)
            if tooltip is not None:
                item.setToolTip(" ".join(tooltip))
            self.listbox.addItem(item)
            if int(effect["effect"]) == self.selected_effect:
                self.selected_row = idx

        # Allow us to print in colour. Do we need this. It gives us size hint, which we could do manually
        delegate = HTMLDelegate()
        delegate._list = self.listbox
        self.listbox.setItemDelegate(delegate)
        size = delegate.sizeHint(0, 0)
        self.listbox.setMinimumWidth(size.width() + 20)
        self.listbox.setMaximumHeight(size.height()*len(self.effects) + 20)

        self.layout.addWidget(self.listbox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.listbox.setCurrentRow(self.selected_row)
        self.listbox.currentRowChanged.connect(self.select_an_effect)

    @Slot()
    def select_an_effect(self, current_row):
        """

        :param: current_row: int: the selected row
        :return:
        """
        print("select_an_effect", current_row)
        if current_row < 0:
            return
        if self.starting and current_row == 0:
            self.starting = False
            self.listbox.setCurrentRow(-1)
        else:
            self.selected_row = current_row
            effect = self.effects[current_row]
            self.selected_effect = int(effect["effect"])
            self.accept()
