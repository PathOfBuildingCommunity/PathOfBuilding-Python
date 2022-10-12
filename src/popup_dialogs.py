"""
simple popups that don't need complex activities to load or execute them
"""

from qdarktheme.qtpy.QtCore import Slot, Qt, QSize
from qdarktheme.qtpy.QtGui import QTextDocument
from qdarktheme.qtpy.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
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
    def __init__(self, node, current_spec, mastery_effects_nodes):
        """
        Choose a mastery from the passed in Node.

        :param node: node(): this mastery node
        :param current_spec: Spec(): the current Spec class for looking up assigned effects
        :param mastery_effects_nodes: list: list of node ids in this mastery group
        """
        super().__init__()

        self.id = node.id
        self.effects = node.masteryEffects
        self.selected_effect = -1
        self.selected_row = -1
        self.starting = True

        assigned_effects = {}
        # turn mastery_effects_nodes into a dict indexed by effect, *IF* it is assigned elsewhere
        for _id in mastery_effects_nodes:
            effect = current_spec.get_mastery_effect(_id)
            if effect > 0:
                assigned_effects[effect] = _id

        # Fill list box with effects' name
        self.listbox = QListWidget()
        for idx, effect in enumerate(self.effects):
            item = QListWidgetItem()
            tooltip = effect.get("reminderText", None)
            stats = " ".join(effect["stats"])
            effects_assigned_node = assigned_effects.get(effect["effect"], -1)
            # if effect is assigned elsewhere, make it unselectable. Make this node's effect green if it has one.
            match effects_assigned_node:
                case -1:
                    # unassigned
                    item.setText(html_colour_text("WHITE", stats))
                case node.id:
                    # assigned to this node
                    item.setText(html_colour_text("GREEN", stats))
                    tooltip = "(Currently Assigned)"
                    self.selected_row = idx
                    self.selected_effect = effect["effect"]
                case _:
                    # assigned to another node
                    item.setFlags(Qt.NoItemFlags)
                    item.setText(html_colour_text("RED", stats))
                    tooltip = "(Already Assigned)"
            if tooltip is not None:
                item.setToolTip(" ".join(tooltip))
            self.listbox.addItem(item)

        # Allow us to print in colour.
        delegate = HTMLDelegate()
        delegate._list = self.listbox
        self.listbox.setItemDelegate(delegate)
        size = delegate.sizeHint(0, 0)
        self.listbox.setMinimumWidth(size.width() + 20)
        self.listbox.setMaximumHeight(size.height() * len(self.effects) + 20)

        self.setWindowTitle(node.name)
        self.setWindowIcon(node.active_image.pixmap())

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Double Click to select an effect."))
        self.layout.addWidget(self.listbox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.listbox.setCurrentRow(self.selected_row)
        if self.selected_row < 0:
            self.listbox.clearSelection()
        self.listbox.itemDoubleClicked.connect(self.effect_selected)
        self.listbox.currentRowChanged.connect(self.effect_row_changed)

    @Slot()
    def effect_selected(self, current_item):
        """

        :param: current_item: QListWidgetItem: the selected item. Not used
        :return: N/A
        """
        current_row = self.listbox.currentRow()
        self.selected_row = current_row
        effect = self.effects[current_row]
        self.selected_effect = effect["effect"]
        self.accept()

    def effect_row_changed(self, current_row):
        """
        Turn off the first selection. On first show, the listwidget will select the first row. We don't want that.

        :param: current_row: int: the selected row. -1 for no selection.
        :return: N/A
        """
        if current_row < 0:
            return
        # Protect against the first row selection
        if self.starting:
            self.starting = False
            self.listbox.setCurrentRow(-1)
