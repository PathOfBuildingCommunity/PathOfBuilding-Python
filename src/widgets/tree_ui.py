"""
This Class manages all the elements and owns some elements of the "TREE" tab

"""
import re

from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton, QDialog

from PoB.constants import tree_versions, PlayerClasses, _VERSION_str
from PoB.settings import Settings
from dialogs.manage_tree_dialog import ManageTreeDlg
from dialogs.popup_dialogs import yes_no_dialog, ImportTreePopup, ExportTreePopup
from widgets.flow_layout import FlowLayout

from ui.PoB_Main_Window import Ui_MainWindow


class TreeUI:
    def __init__(self, _settings: Settings, _build, frame_tree_tools, _win: Ui_MainWindow) -> None:
        """
        Items UI
        :param _settings: pointer to Settings()
        :param _build: A pointer to the currently loaded build
        :param frame_tree_tools: QFrame: Frame at the bottom ofthe UI where extra widgets are loaded.
        :param _win: pointer to MainWindow()
        """
        self.settings = _settings
        self.tr = self.settings.app.tr
        self.win = _win
        # reference to Items UI to fill it's tree combo
        self.items_ui = None
        self.build = _build
        self._curr_class = PlayerClasses.SCION
        self.dlg = None  # Is a dialog active

        self.win.action_ManageTrees.triggered.connect(self.open_manage_trees)

        """
        Add Widgets to the QFrame at the bottom of the TreeView, using the fixed version of the PySide6 example
         Flow Layout. You can set size hints for these widgets, but not setGeometry().
        """
        self.layout_tree_tools = FlowLayout(frame_tree_tools, 2)

        widget_height = 24
        self.combo_manage_tree = QComboBox()
        self.combo_manage_tree.setMinimumSize(QSize(180, widget_height))
        self.combo_manage_tree.setMaximumSize(QSize(300, 16777215))
        self.layout_tree_tools.addWidget(self.combo_manage_tree)

        self.check_Compare = QCheckBox()
        self.check_Compare.setMinimumSize(QSize(100, widget_height))
        self.check_Compare.setText("Compare Tree")
        self.check_Compare.setLayoutDirection(Qt.RightToLeft)
        self.check_Compare.stateChanged.connect(self.set_combo_compare_visibility)
        # self.layout_tree_tools.addWidget(self.check_Compare)

        self.combo_compare = QComboBox()
        self.combo_compare.setMinimumSize(QSize(180, widget_height))
        self.combo_compare.setMaximumSize(QSize(300, 16777215))
        self.combo_compare.setVisible(False)
        self.layout_tree_tools.addWidget(self.combo_compare)
        # self.combo_compare.currentIndexChanged.connect(self.change_compare_combo)

        self.btn_Reset = QPushButton()
        self.btn_Import = QPushButton()
        self.btn_Export = QPushButton()
        self.btn_Reset.setText(f'{self.tr("&Reset Tree")} ...')
        self.btn_Import.setText(f'{self.tr("I&mport Tree")} ...')
        self.btn_Export.setText(f'{self.tr("E&xport Tree")} ...')
        # self.layout_tree_tools.addWidget(self.btn_Reset)
        # self.layout_tree_tools.addWidget(self.btn_Import)
        # self.layout_tree_tools.addWidget(self.btn_Export)
        self.btn_Reset.clicked.connect(self.reset_tree)
        self.btn_Import.clicked.connect(self.import_tree)
        self.btn_Export.clicked.connect(self.export_tree)

        self.label_Search = QLabel()
        self.label_Search.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_Search.setMinimumSize(QSize(50, widget_height))
        self.label_Search.setText("Search:")
        # self.layout_tree_tools.addWidget(self.label_Search)
        self.lineEdit_Search = QLineEdit()
        self.lineEdit_Search.setMinimumSize(QSize(150, widget_height))
        # self.layout_tree_tools.addWidget(self.lineEdit_Search)

        self.check_show_node_power = QCheckBox()
        self.check_show_node_power.setMinimumSize(QSize(140, widget_height))
        self.check_show_node_power.setText(self.tr("Show Node Power:"))
        self.check_show_node_power.setLayoutDirection(Qt.RightToLeft)
        self.check_show_node_power.stateChanged.connect(self.set_show_node_power_visibility)
        self.check_show_node_power.setEnabled(True)
        # self.layout_tree_tools.addWidget(self.check_show_node_power)
        self.combo_show_node_power = QComboBox()
        self.combo_show_node_power.setMinimumSize(QSize(180, widget_height))
        self.combo_show_node_power.setMaximumSize(QSize(180, 16777215))
        self.combo_show_node_power.setVisible(False)
        self.combo_show_node_power.setEnabled(True)
        # self.layout_tree_tools.addWidget(self.combo_show_node_power)
        self.btn_show_power_report = QPushButton()
        self.btn_show_power_report.setText(f'{self.tr("Show Power Report")} ...')
        self.btn_show_power_report.setVisible(False)
        self.btn_show_power_report.setEnabled(True)
        # self.layout_tree_tools.addWidget(self.btn_show_power_report)
        """ End Adding Widgets to the QFrame at the bottom of the TreeView. """

        self.lineEdit_Search.textChanged.connect(self.search_text_changed)
        self.lineEdit_Search.returnPressed.connect(self.search_text_return_pressed)

    def load(self):
        """Load internal structures from the build object."""
        pass

    def save(self):
        """Save internal structures back to the build object."""
        pass

    @property
    def curr_class(self):
        return self._curr_class

    @curr_class.setter
    def curr_class(self, new_class):
        """
        Actions required for changing classes
        :param new_class:PlayerClasses. Current class
        :return: N/A
        """
        # get the dictionary associated with this class
        _class = self.build.current_tree.classes[new_class.value]

    @Slot()
    def set_combo_compare_visibility(self, checked_state):
        """
        Enable or disable the compare comboBox.
        :param checked_state: Integer: 0 = unchecked, 2 = checked
        :return: N/A
        """
        self.combo_compare.setVisible(checked_state > 0)
        self.build.compare_spec = checked_state > 0 and self.build.specs[self.combo_compare.currentIndex()] or None
        self.win.gview_Tree.add_tree_images(False)

    @Slot()
    def set_show_node_power_visibility(self, checked_state):
        """
        Enable or disable the compare comboBox.
        :param checked_state: Integer: 0 = unchecked, 2 = checked
        :return: N/A
        """
        self.combo_show_node_power.setVisible(checked_state > 0)
        self.btn_show_power_report.setVisible(checked_state > 0)

    @Slot()
    def shortcut_CtrlM(self):
        """
        Respond to Ctrl-M and open the appropriate dialog
        :return: N/A
        """
        # print("Ctrl-M", type(self))
        self.open_manage_trees()

    @Slot()
    def open_manage_trees(self):
        """
        and we need a dialog ...
        :return: N/A
        """
        # Ctrl-M (from MainWindow) won't know if there is another window open, so stop opening another instance.
        if self.dlg is None:
            self.dlg = ManageTreeDlg(self.build, self.settings, self.win)
            self.dlg.exec()
            self.dlg = None
            self.fill_current_tree_combo()

    def fill_current_tree_combo(self):
        """
        Actions required to fill the combo_manage_tree widget. Usually when loading a build.

        :return: N/A
        """
        # let's protect activeSpec as the next part will erase it
        active_spec = self.build.activeSpec
        for combo in (self.combo_manage_tree, self.win.combo_ItemsManageTree, self.combo_compare):
            combo.clear()
        for idx, spec in enumerate(self.build.specs):
            if spec is not None:
                if spec.treeVersion != _VERSION_str:
                    title = f"[{tree_versions[spec.treeVersion]}] {spec.title}"
                else:
                    title = spec.title
                for combo in (self.combo_manage_tree, self.win.combo_ItemsManageTree, self.combo_compare):
                    curr_visibility = combo.isHidden()
                    print(combo, curr_visibility)
                    combo.addItem(title, idx)
                    combo.view().setMinimumWidth(combo.minimumSizeHint().width())
                    combo.view().updateGeometries()
                    combo.view().reset()
                    # combo.setHidden(True)
                    # combo.setHidden(curr_visibility)

        # reset activeSpec
        self.combo_manage_tree.setCurrentIndex(active_spec)

    @Slot()
    def change_compare_combo(self, index):
        """
        Processes for changing the compare combo

        :param index:
        :return: N/A
        """
        self.build.compare_spec = self.build.specs[index]
        self.win.gview_Tree.add_tree_images(False)

    @Slot()
    def reset_tree(self):
        """

        :return:
        """
        print("reset_tree")
        if yes_no_dialog(
            self.win,
            self.tr("Resetting your Tree"),
            self.tr("Are you sure? It could be dangerous."),
        ):
            self.build.reset_tree()

    @Slot()
    def import_tree(self):
        """
        Import a passive tree URL.

        :return: N/A
        """
        dlg = ImportTreePopup(self.settings.app.tr, self.combo_manage_tree.currentText(), self.win)
        _return = dlg.exec()
        if _return:
            self.build.current_spec.import_tree(dlg.lineedit_url.text() + "==")
            # self.win.import_tree(dlg.lineedit_url.text())
            self.win.change_tree("Refresh")

    @Slot()
    def export_tree(self):
        """Export the current nodes as a URL"""
        url = self.build.current_spec.export_nodes_to_url()
        self.build.current_spec.URL = url
        dlg = ExportTreePopup(self.settings.app.tr, url, self.win)
        # we don't care about how the user exits
        dlg.exec()

    @Slot()
    def search_text_changed(self):
        """
        Store the text of Search edit as it is typed.
        Should we use this or just use the return_pressed function
        """
        self.build.search_text = self.lineEdit_Search.text()
        self.win.gview_Tree.refresh_search_rings()

    @Slot()
    def search_text_return_pressed(self):
        """
        refresh the whole scene and Update the search rings

        :return: N/A
        """
        self.win.gview_Tree.add_tree_images(True)
        self.search_text_changed()


# def test() -> None:
#     tree_ui = TreeUI()
#     print(tree_ui)


# if __name__ == "__main__":
#     test()
