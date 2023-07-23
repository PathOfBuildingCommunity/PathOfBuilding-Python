"""
simple popups that don't need complex activities to load or execute them
"""

import re
import base64
import requests

from qdarktheme.qtpy.QtCore import Slot, Qt, QSize
from qdarktheme.qtpy.QtGui import QGuiApplication, QIcon
from qdarktheme.qtpy.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)

from constants import ColourCodes, _VERSION_str, get_http_headers, tree_versions
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
    def __init__(self, tr, node, current_spec, mastery_effects_nodes):
        """
        Choose a mastery from the passed in Node.

        :param tr: App translate function
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
            item.setData(20, idx)
            tooltip = effect.get("reminderText", None)
            stats = " ".join(effect["stats"])
            effects_assigned_node = assigned_effects.get(effect["effect"], -1)
            # if effect is assigned elsewhere, make it unselectable. Make this node's effect green if it's assigned.
            match effects_assigned_node:
                case -1:
                    # unassigned
                    item.setText(html_colour_text("WHITE", stats))
                case node.id:
                    # assigned to this node
                    item.setText(html_colour_text("GREEN", stats))
                    tooltip = tr(f"(Currently Assigned), {effect}")
                    self.selected_row = idx
                    self.selected_effect = effect["effect"]
                case _:
                    # assigned to another node
                    item.setFlags(Qt.NoItemFlags)
                    item.setText(html_colour_text("RED", stats))
                    tooltip = tr(f"(Already Assigned), {effect}")
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

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Double Click to select an effect."))
        self.layout.addWidget(self.listbox)
        self.layout.addWidget(self.button_box)
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
        current_row = current_item.data(20)
        self.selected_row = current_row
        effect = self.effects[current_row]
        self.selected_effect = effect["effect"]
        # print("effect_selected: item, row, effect", QListWidgetItem(current_item).data(20), current_row, effect)
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


"""######## ImportTreePopup. Import a passive Tree URL ########"""


class ImportTreePopup(QDialog):
    def __init__(self, tr):
        """
        Initialize
        :param tr: App translate function
        """
        super().__init__()
        self.label_intro_text = tr("Enter passive tree URL.")
        self.label_seems_legit_text = tr(html_colour_text("GREEN", "Seems valid. Lets go."))
        self.label_not_valid_text = tr(html_colour_text("RED", "Not valid. Try again."))
        self.setWindowTitle(tr("Import tree from URL"))
        self.setWindowIcon(QIcon(":/Art/Icons/paper-plane-return.png"))

        self.label = QLabel(self.label_intro_text)
        self.lineedit = QLineEdit()
        self.lineedit.setMinimumWidth(600)
        self.lineedit.textChanged.connect(self.validate_url)

        self.btn_import = QPushButton("Import")
        self.btn_import.setEnabled(False)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.addButton(self.btn_import, QDialogButtonBox.AcceptRole)
        self.button_box.setCenterButtons(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def validate_url(self, text):
        """
        Validate the lineedit input (url hopefuilly). Turn on/off the import button and change label text as needed.

        :param text: str: the current text of the line edit
        :return: N/A
        """
        if text == "":
            self.label.setText(self.label_intro_text)
        else:
            # check the validity of what was passed in
            ggg = re.search(r"http.*passive-skill-tree/(.*/)?(.*)", text + "==")
            poep = re.search(r"http.*poeplanner.com/(.*)", text + "==")
            if ggg is not None:
                # output[0] will be the encoded string and the rest will variable=value, which we don't care about
                output = ggg.group(2).split("?")
                decoded_str = base64.urlsafe_b64decode(output[0])
                self.btn_import.setEnabled(decoded_str and len(decoded_str) > 7)
                self.label.setText(self.label_seems_legit_text)
            elif poep is not None:
                # Remove any variables at the end (probably not required for poeplanner)
                output = poep.group(1).split("?")
                decoded_str = base64.urlsafe_b64decode(output[0])
                self.btn_import.setEnabled(decoded_str and len(decoded_str) > 15)
                self.label.setText(
                    self.label_seems_legit_text + " Tree nodes and Bandits info only. Cluster nodes won't show."
                )
            else:
                self.btn_import.setEnabled(False)
                self.label.setText(self.label_not_valid_text)


"""######## ExportTreePopup. Export a passive Tree URL ########"""


class ExportTreePopup(QDialog):
    def __init__(self, tr, url, win):
        """
        Initialize
        :param tr: App translate function
        :param url: str: the encoded url
        :param win: MainWindow(): reference for accessing the statusbar
        """
        super().__init__()
        self.tr = tr
        self.win = win
        self.label_intro_text = tr("Passive tree URL.")
        self.shrink_text = f'{tr("Shrink with")} PoEURL'
        self.setWindowTitle(tr("Export tree to URL"))
        self.setWindowIcon(QIcon(":/Art/Icons/paper-plane.png"))

        self.label = QLabel(self.label_intro_text)
        self.lineedit = QLineEdit()
        self.lineedit.setMinimumWidth(600)
        self.lineedit.setText(url)

        self.btn_copy = QPushButton(tr("Copy"))
        self.btn_copy.setAutoDefault(False)
        self.btn_copy.clicked.connect(self.copy_url)
        self.btn_shrink = QPushButton(self.shrink_text)
        self.btn_shrink.clicked.connect(self.shrink_url)
        self.btn_shrink.setAutoDefault(False)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.addButton(self.btn_shrink, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.btn_copy, QDialogButtonBox.ActionRole)
        self.button_box.setCenterButtons(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)
        self.set_lineedit_selection()

    def set_lineedit_selection(self):
        """Ensure linedit has focus and the text selected"""
        self.lineedit.setFocus(Qt.OtherFocusReason)
        self.lineedit.setSelection(0, len(self.lineedit.text()))

    def copy_url(self):
        """Copy the text in the lineedit to the clipboard"""
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.lineedit.text())
        self.set_lineedit_selection()

    def shrink_url(self):
        """Call poeurl and get the url 'shrinked'"""
        self.btn_shrink.setText(f'{self.tr("Shrinking")} ...')
        self.btn_shrink.setEnabled(False)
        url = f"http://poeurl.com/shrink.php?url={self.lineedit.text()}"
        response = None
        try:
            response = requests.get(url, headers=get_http_headers, timeout=6.0)
            url = f'http://poeurl.com/{response.content.decode("utf-8")}'
            self.lineedit.setText(url)
            self.lineedit.setSelection(0, len(url))
            self.btn_shrink.setText(self.tr("Done"))
        except requests.RequestException as e:
            self.win.update_status_bar(f"Error retrieving 'Data': {response.reason} ({response.status_code}).")
            self.btn_shrink.setEnabled(True)
            self.btn_shrink.setText(self.shrink_text)
            print(f"Error accessing 'http://poeurl.com': {e}.")
        self.set_lineedit_selection()


"""######## NewTreePopup. Export a passive Tree URL ########"""


class NewTreePopup(QDialog):
    def __init__(self, tr):
        """
        Initialize
        :param tr: App translate function
        """
        super().__init__()
        # self.label_intro_text = tr("New passive tree.")
        self.setWindowTitle(tr("New passive tree"))
        self.setWindowIcon(QIcon(":/Art/Icons/tree--pencil.png"))

        # self.label = QLabel(self.label_intro_text)
        self.lineedit = QLineEdit()
        self.lineedit.setMinimumWidth(400)
        self.lineedit.setPlaceholderText("New tree, Rename Me")
        # self.lineedit.textChanged.connect(self.validate_url)
        self.combo_tree_version = QComboBox()
        for ver in tree_versions.keys():
            self.combo_tree_version.addItem(tree_versions[ver], ver)
        self.combo_tree_version.setCurrentIndex(len(tree_versions) - 1)

        self.btn_exit = QPushButton("Don't Save")
        # self.btn_exit.setEnabled(False)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.addButton(self.btn_exit, QDialogButtonBox.RejectRole)
        self.button_box.setCenterButtons(True)

        self.hlayout = QHBoxLayout()
        # self.hlayout.addWidget(self.label)
        self.hlayout.addWidget(self.lineedit)
        self.hlayout.addWidget(self.combo_tree_version)

        self.vlayout = QVBoxLayout()
        self.vlayout.addLayout(self.hlayout)
        self.vlayout.addWidget(self.button_box)
        self.setLayout(self.vlayout)
