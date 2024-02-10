"""

"""

import re

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QPushButton, QFileDialog, QDialogButtonBox

from widgets.ui_utils import set_combo_index_by_text, format_number

from ui.PoB_Main_Window import Ui_MainWindow
from ui.dlgSettings import Ui_Settings


class SettingsDlg(Ui_Settings, QDialog):
    """Settings dialog"""

    def __init__(self, _settings, _win: Ui_MainWindow = None):
        """
        Settings dialog init
        :param _settings: A pointer to the settings
        :param _win: A pointer to MainWindowUI
        """
        super().__init__(_win)
        # Run the .setupUi() method to show the GUI
        self.settings = _settings
        self.tr = self.settings.app.tr

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
        self.label_AffixQValue.setText(f"{format_number(self.slider_AffixQuality.value() / 100 ,'%0.2f', self.settings)}")

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
            self.settings.reset()
        self.combo_Protocol.setCurrentIndex(self.settings.connection_protocol)
        self.lineedit_BuildPath.setText(str(self.settings.build_path))
        self.combo_NP_Colours.setCurrentIndex(self.settings.node_power_theme)
        self.check_Beta.setChecked(self.settings.beta_mode)
        self.check_ShowBuildName.setChecked(self.settings.show_titlebar_name)
        self.check_ShowThousandsSeparators.setChecked(self.settings.show_thousands_separators)
        # self.lineedit_ThousandsSeparator.setText(self.settings.thousands_separator)
        # self.lineedit_DecimalSeparator.setText(self.settings.decimal_separator)
        self.spin_GemQuality.setValue(self.settings.default_gem_quality)
        self.spin_Level.setValue(self.settings.default_char_level)
        self.slider_AffixQuality.setValue(int(self.settings.default_item_affix_quality * 100))
        self.setting_show_affix_quality_value()
        self.check_BuildWarnings.setChecked(self.settings.show_warnings)
        self.check_Tooltips.setChecked(self.settings.slot_only_tooltips)
        self.lineedit_Pos_Colour.setText(str(self.settings.colour_positive))
        self.lineedit_Neg_Colour.setText(str(self.settings.colour_negative))
        self.lineedit_HL_Colour.setText(str(self.settings.colour_highlight))
        m = re.search(r"^(\w+)://(.*)$", self.settings.proxy_url)
        if m:
            set_combo_index_by_text(self.combo_Proxy, m.group(1).upper())
            self.lineedit_Proxy.setText(m.group(2))

        # self.combo_Proxy.setCurrentIndex(config.p)
        #
