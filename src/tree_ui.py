"""
This Class manages all the elements and owns some elements of the "TREE" tab

"""

from qdarktheme.qtpy.QtCore import QCoreApplication, Qt, Slot, QSize
from qdarktheme.qtpy.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton

from PoB_Main_Window import Ui_MainWindow
from constants import _VERSION, PlayerClasses, _VERSION_str
from pob_config import Config, _debug
from flow_layout import FlowLayout
from manage_tree_dialog import ManageTreeDlg


class TreeUI:
    def __init__(self, _config: Config, frame_tree_tools, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        tr = self.pob_config.app.tr
        self.win = _win
        self.build = self.win.build
        self._curr_class = PlayerClasses.SCION

        self.win.action_ManageTrees.triggered.connect(self.open_manage_trees)

        """
        Add Widgets to the QFrame at the bottom of the treeview, using the fixed version of the PySide6 example
         Flow Layout. You can set size hints for these widgets, but not setGeometry().
        """
        self.layout_tree_tools = FlowLayout(frame_tree_tools, 2)

        self.combo_manage_tree = QComboBox()
        self.combo_manage_tree.setMinimumSize(QSize(180, 22))
        self.combo_manage_tree.setMaximumSize(QSize(300, 16777215))
        self.layout_tree_tools.addWidget(self.combo_manage_tree)

        self.check_Compare = QCheckBox()
        self.check_Compare.setMinimumSize(QSize(50, 22))
        self.check_Compare.setText("Compare Tree")
        self.check_Compare.setLayoutDirection(Qt.RightToLeft)
        self.check_Compare.stateChanged.connect(self.set_combo_compare_visibility)
        self.layout_tree_tools.addWidget(self.check_Compare)

        self.combo_compare = QComboBox()
        self.combo_compare.setMinimumSize(QSize(180, 22))
        self.combo_compare.setMaximumSize(QSize(300, 16777215))
        self.combo_compare.setVisible(False)
        self.layout_tree_tools.addWidget(self.combo_compare)

        self.btn_Reset = QPushButton()
        self.btn_Import = QPushButton()
        self.btn_Export = QPushButton()
        self.btn_Reset.setText(tr(f'{tr("Reset Tree")} ...'))
        self.btn_Import.setText(tr(f'{tr("Import Tree")} ...'))
        self.btn_Export.setText(tr(f'{tr("Export Tree")} ...'))
        self.layout_tree_tools.addWidget(self.btn_Reset)
        self.layout_tree_tools.addWidget(self.btn_Import)
        self.layout_tree_tools.addWidget(self.btn_Export)

        self.label_Search = QLabel()
        self.label_Search.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_Search.setMinimumSize(QSize(50, 22))
        self.label_Search.setText("Search:")
        self.layout_tree_tools.addWidget(self.label_Search)
        self.textEdit_Search = QLineEdit()
        self.textEdit_Search.setMinimumSize(QSize(150, 22))
        self.textEdit_Search.setText("Dexterit")
        self.layout_tree_tools.addWidget(self.textEdit_Search)

        self.check_show_node_power = QCheckBox()
        self.check_show_node_power.setMinimumSize(QSize(50, 22))
        self.check_show_node_power.setText(tr("Show Node Power:"))
        self.check_show_node_power.setLayoutDirection(Qt.RightToLeft)
        self.check_show_node_power.stateChanged.connect(self.set_show_node_power_visibility)
        self.layout_tree_tools.addWidget(self.check_show_node_power)
        self.combo_show_node_power = QComboBox()
        self.combo_show_node_power.setMinimumSize(QSize(180, 22))
        self.combo_show_node_power.setMaximumSize(QSize(180, 16777215))
        self.combo_show_node_power.setVisible(False)
        self.layout_tree_tools.addWidget(self.combo_show_node_power)
        self.btn_show_power_report = QPushButton()
        self.btn_show_power_report.setVisible(False)
        self.btn_show_power_report.setText(f'{tr("Show Power Report")} ...')
        self.layout_tree_tools.addWidget(self.btn_show_power_report)
        """ End Adding Widgets to the QFrame at the bottom of the treeview. """

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
        print("Ctrl-M", type(self))
        self.open_manage_trees()

    def open_manage_trees(self):
        """
        and we need a dialog ...
        :return:
        """
        print("open_manage_trees")
        dlg = ManageTreeDlg(self.build, self.win)
        dlg.exec()
        self.fill_current_tree_combo()

    def fill_current_tree_combo(self):
        """
        Actions required to fill the combo_manage_tree widget. Usually when loading a build.

        :return: N/A
        """
        # let's protect activeSpec as the next part will erase it
        active_spec = self.build.activeSpec
        self.combo_manage_tree.clear()
        self.combo_compare.clear()
        for idx, spec in enumerate(self.build.specs):
            if spec is not None:
                if spec.treeVersion != _VERSION_str:
                    title = f"[{spec.treeVersion}] {spec.title}"
                else:
                    title = spec.title
                self.combo_manage_tree.addItem(title, idx)
                self.combo_compare.addItem(title, idx)
        # reset activeSpec
        self.combo_manage_tree.setCurrentIndex(active_spec)


def test() -> None:
    tree_ui = TreeUI()
    print(tree_ui)


if __name__ == "__main__":
    test()
