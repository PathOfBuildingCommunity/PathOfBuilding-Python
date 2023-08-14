"""

"""
import re

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QPushButton, QFileDialog, QDialogButtonBox

from widgets.ui_utils import set_combo_index_by_text

from ui.dlgSettings import Ui_Settings


class SettingsDlg(Ui_Settings, QDialog):
    """Settings dialog"""

    def __init__(self, _config, parent=None):
        super().__init__(parent)
        # Run the .setupUi() method to show the GUI
        self.config = _config
        self.tr = self.config.app.tr

        self.setupUi(self)

        discard = self.btnBox.button(QDialogButtonBox.Discard)
        # Force discard button to close the dialog
        discard.clicked.connect(self.reject)
        discard.setToolTip(self.tr("Abandon these setting. Change nothing."))

        restore_defaults = self.btnBox.button(QDialogButtonBox.RestoreDefaults)
        restore_defaults.clicked.connect(self.setting_restore_defaults)
        restore_defaults.setToolTip(self.tr("Load the original default settings."))
        # For some reason this button comes up as default. Stop it
        # restore_defaults.setAutoDefault(False)

        reset = self.btnBox.button(QDialogButtonBox.RestoreDefaults)
        reset.clicked.connect(self.reset_settings)
        reset.setToolTip(self.tr("Load your current unchanged settings."))

        save = self.btnBox.button(QDialogButtonBox.Save)
        save.setDefault(True)
        save.setToolTip(self.tr("Save the settings to use now."))

        self.btn_BuildPath.clicked.connect(self.setting_directory_dialog)
        self.slider_AffixQuality.valueChanged.connect(self.setting_show_affix_quality_value)
        self.lineedit_BuildPath.textChanged.connect(self.setting_set_build_path_tooltip)

        # fill the fields, triggering components.
        self.load_settings(False)

    @Slot()
    def setting_restore_defaults(self):
        self.load_settings(True)

    @Slot()
    def reset_settings(self):
        self.load_settings(False)

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
        # print("setting_directory_dialog")
        directory = QFileDialog.getExistingDirectory(self, "Select Build Path")
        if directory != "":
            self.lineedit_BuildPath.setText(directory)

    @Slot()
    def load_settings(self, default=False):
        """
        Set dialog widgets with values.
        :param default: If True, set widgets with default values
        :return:
        """
        if default:
            self.config.reset()
        # print_a_xml_element(_config)
        self.combo_Protocol.setCurrentIndex(self.config.connection_protocol)
        self.lineedit_BuildPath.setText(str(self.config.build_path))
        self.combo_NP_Colours.setCurrentIndex(self.config.node_power_theme)
        self.check_Beta.setChecked(self.config.beta_mode)
        self.check_ShowBuildName.setChecked(self.config.show_titlebar_name)
        self.check_ShowThousandsSeparators.setChecked(self.config.show_thousands_separators)
        self.lineedit_ThousandsSeparator.setText(self.config.thousands_separator)
        self.lineedit_DecimalSeparator.setText(self.config.decimal_separator)
        self.spin_GemQuality.setValue(self.config.default_gem_quality)
        self.spin_Level.setValue(self.config.default_char_level)
        self.slider_AffixQuality.setValue(int(self.config.default_item_affix_quality * 100))
        self.check_BuildWarnings.setChecked(self.config.show_warnings)
        self.check_Tooltips.setChecked(self.config.slot_only_tooltips)
        m = re.search(r"^(\w+)://(.*)$", self.config.proxy_url)
        if m:
            set_combo_index_by_text(self.combo_Proxy, m.group(1).upper())
            self.lineedit_Proxy.setText(m.group(2))

        # self.combo_Proxy.setCurrentIndex(config.p)
        #
