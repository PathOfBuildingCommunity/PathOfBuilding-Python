"""
This Class manages all the elements and owns some elements of the "TREE" tab

"""

from qdarktheme.qtpy.QtCore import QCoreApplication, Qt, Slot, QSize
from qdarktheme.qtpy.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton

from PoB_Main_Window import Ui_MainWindow
from constants import _VERSION, PlayerClasses
from pob_config import Config
from ui_utils import FlowLayout


class TreeUI:
    def __init__(self, _config: Config, frame_tree_tools, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self.build = self.win.build
        self.layout_tree_tools = FlowLayout(frame_tree_tools, 2)
        self._curr_class = PlayerClasses.SCION

        """
        Add Widgets to the tool bar at the bottom of the tree, using the fixed version of the PySide6 example Flow Layout
        You can set size hints, but not setGeometry.
        """
        self.win.action_ManageTrees.triggered.connect(self.shortcut_CtrlM)

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
        self.btn_Reset.setText(QCoreApplication.translate("MainWindow", "Reset Tree...", None))
        self.btn_Import.setText(QCoreApplication.translate("MainWindow", "Import Tree ...", None))
        self.btn_Export.setText(QCoreApplication.translate("MainWindow", "Export Tree...", None))
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
        # self.textEdit_Search.setText("Dexterity")
        self.layout_tree_tools.addWidget(self.textEdit_Search)

        self.check_show_node_power = QCheckBox()
        self.check_show_node_power.setMinimumSize(QSize(50, 22))
        self.check_show_node_power.setText(QCoreApplication.translate("MainWindow", "Show Node Power:", None))
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
        self.btn_show_power_report.setText(QCoreApplication.translate("MainWindow", "Show Power Report ...", None))
        self.layout_tree_tools.addWidget(self.btn_show_power_report)

    def load(self):
        """
        Load internal structures from the build object
        """
        pass

    def save(self):
        """
        Save internal structures back to the build object
        """
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

    def fill_current_tree_combo(self):
        """
        Actions required to fill the combo_manage_tree widget. Usually when loading a build
        :return: N/A
        """
        # let's protect activeSpec as the next part will erase it
        active_spec = self.build.activeSpec
        self.combo_manage_tree.clear()
        self.combo_compare.clear()
        for idx, spec in enumerate(self.build.specs):
            if spec is not None:
                self.combo_manage_tree.addItem(spec.title, idx)
                self.combo_compare.addItem(spec.title, idx)
        # reset activeSpec
        self.combo_manage_tree.setCurrentIndex(active_spec)

    def set_current_tab(self):
        """
        Actions required when setting the current tab from the configuration xml file
        :return: N/A
        """
        for i in range(self.win.tab_main.count()):
            if self.win.tab_main.tabWhatsThis(i) == self.build.viewMode:
                self.win.tab_main.setCurrentIndex(i)
                return
        self.win.tab_main.setCurrentIndex(0)


def test() -> None:
    tree_ui = TreeUI()
    print(tree_ui)


if __name__ == "__main__":
    test()
