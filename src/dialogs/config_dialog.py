"""

"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QPushButton, QFileDialog
from views.dlgConfig import Ui_dlg_Config


class ConfigDlg(Ui_dlg_Config, QDialog):
    """Settings dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Run the .setupUi() method to show the GUI
        self.set_dialog(True)
        self.setupUi(self)

    @Slot()
    def setting_restore_defaults(self):
        self.set_dialog(True)

    @Slot()
    def setting_show_affix_quality_value(self):
        self.label_AffixQValue.setText(f"{self.slider_AffixQuality.value() / 100}")

    @Slot()
    def setting_set_build_path_tooltip(self):
        self.lineedit_BuildPath.setToolTip(self.lineedit_BuildPath.text())

    @Slot()
    def setting_directory_dialog(self):
        """
        Open a directory only file dialog for setting the build path
        :return: Path
        """
        print("setting_directory_dialog")
        directory = QFileDialog.getExistingDirectory(self, "Select Build Path")
        if directory != "":
            self.lineedit_BuildPath.setText(directory)

    @Slot()
    def set_dialog(self, default=False):
        """
        Set dialog widgets with values.
        :param default: If True, set widgets with default values
        :return:
        """
        if default:
            self.reset()
        # print_a_xml_element(_config)
        self.combo_Protocol.setCurrentIndex(self.connection_protocol)
        # self.combo_Proxy.setCurrentIndex(config.p)
        # self.lineedit_Proxy.setText(config.p)
        self.lineedit_BuildPath.setText(str(self.build_path))
        self.combo_NP_Colours.setCurrentIndex(self.node_power_theme)
        self.check_Beta.setChecked(self.beta_mode)
        self.check_ShowBuildName.setChecked(self.show_titlebar_name)
        self.check_ShowThousandsSeparators.setChecked(self.show_thousands_separators)
        self.lineedit_ThousandsSeparator.setText(self.thousands_separator)
        self.lineedit_DecimalSeparator.setText(self.decimal_separator)
        self.spin_GemQuality.setValue(self.default_gem_quality)
        self.spin_Level.setValue(self.default_char_level)
        self.slider_AffixQuality.setValue(int(self.default_item_affix_quality * 100))
        self.check_BuildWarnings.setChecked(self.show_warnings)
        self.check_Tooltips.setChecked(self.slot_only_tooltips)
