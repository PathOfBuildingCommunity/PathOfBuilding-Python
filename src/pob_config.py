"""
Configuration Class

Read, Writes and manages the settings xml as well as the settings therein
As the settings.xml can be altered by humans, care must be taken to ensure data integrity, where possible

This is a base PoB class. It doesn't import any other PoB ui classes
"""

from pathlib import Path
import base64
import datetime
import glob
import itertools
import operator
import os
import tempfile
import traceback
import xml.etree.ElementTree as ET
import zlib

# from qdarktheme.qtpy.QtCore import QSize, Slot
# from qdarktheme.qtpy.QtWidgets import QFileDialog, QDialogButtonBox
from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import QFileDialog, QDialogButtonBox
from PySide6.QtUiTools import QUiLoader

import pob_file
from constants import pob_debug, default_config


def str_to_bool(in_str):
    """
    Return a boolean from a string. As the settings could be manipulated by a human, we can't trust eval()
      EG: eval('os.system(`rm -rf /`)')
    :param: in_str: String: The setting to be evaluated
    :returns: True if it looks like it could be true, otherwise False
    """
    return in_str.lower() in ("yes", "true", "t", "1", "on")


def bool_to_str(in_bool):
    """
    Return a string from a boolean.
    :param: in_bool: Boolean: The setting to be evaluated
    :returns: String: true or false
    """
    return in_bool and "true" or "false"


def index_exists(_list_or_dict, index):
    """
    Test if a list contains a given index
    :param _list_or_dict: object to be tested
    :param index: index to be tested
    :return: Boolean: True / False
    """
    try:
        _l = _list_or_dict[index]
        return True
    except (IndexError, KeyError, TypeError):
        return False


def print_call_stack(full=False, idx=-3):
    """
    Ahh debug. It's wonderful
    :param: full: Bool: True if you want the full stack trace,
            elsewise just print the parent of the function that called this
    :return: N/A
    """
    lines = traceback.format_stack()
    if full:
        for line in lines[:-2]:
            print(line.strip())
    else:
        print(lines[idx].strip())
    print("------\n")


def _debug(*text):
    """
    print a debug line if debug is enabled
    :param: text: list. The info to print
    :return: N/A
    """
    if pob_debug:
        lines = traceback.format_stack()
        print(
            f"{datetime.datetime.now()}: {text}",
            ":",
            lines[-2].strip().partition("\n")[0],
        )


def print_a_xml_element(the_element):
    """
    Debug: Print the contents so you can see what happened and why 'it' isn't working.
    Prints the parent caller to help track when there are many of them.
    :param the_element: xml element
    :return: N/A
    """
    if the_element is None:
        print(the_element)
        return
    lines = traceback.format_stack()
    print(lines[-2].strip())
    print(ET.tostring(the_element, encoding="utf8").decode("utf8"))
    print()


def unique_sorted(values):
    """Return a sorted list of the given values, without duplicates."""
    return map(operator.itemgetter(0), itertools.groupby(sorted(values)))


def decode_base64_and_inflate(byte_array):
    """
    Decode a byte array and then zlib inflate it to make real characters
    :param byte_array: an array like you get fro downloading from pastebin or pobb.in
    :return: a string of real characters
    """
    try:
        decoded_data = base64.urlsafe_b64decode(byte_array)
        return zlib.decompress(decoded_data, 0)
    except:
        return None


def deflate_and_base64_encode(string_val):
    """
    zlib compress a string of characters and base64 encoded them
    :param string_val: a string or real characters
    :return: a byte array or the compressed and encoded string_val
    """
    # try:
    zlibbed_str = zlib.compress(string_val)
    return base64.urlsafe_b64encode(zlibbed_str)
    # except:
    #     return None


class Config:
    def __init__(self, _win, _app) -> None:
        # To reduce circular references, have the app and main window references here
        self.win = _win
        self.app = _app
        self.screen_rect = self.app.primaryScreen().size()
        self.loader = QUiLoader()

        # this is the xml tree representing the xml
        self.root = None
        self.tree = None
        # easy access to the Misc tag
        self.misc = None
        self.pastebin = None

        # Path and directory variables
        self.exe_dir = Path.cwd()
        self.data_dir = (
            "NUITKA_ONEFILE_PARENT" in os.environ
            and Path(tempfile.gettempdir(), f"PoB_{os.environ['NUITKA_ONEFILE_PARENT']}")
            or self.exe_dir
        )
        self.settings_file = Path(self.exe_dir, "settings.xml")
        self.tree_data_path = Path(self.data_dir, "tree_data")
        if not self.tree_data_path.exists():
            self.tree_data_path.mkdir()
        self.read()
        if self.build_path == "":
            self.build_path = Path(self.exe_dir, "builds")
        if not Path(self.build_path).exists():
            Path(self.build_path).mkdir()

    def reset(self):
        """Reset to default config"""
        self.tree = ET.ElementTree(ET.fromstring(default_config))
        self.root = self.tree.getroot()
        self.misc = self.root.find("Misc")
        self.pastebin = self.root.find("Misc")

    def read(self):
        """Set self.root with the contents of the settings file"""
        if self.settings_file.exists():
            try:
                self.tree = pob_file.read_xml(self.settings_file)
            except ET.ParseError:
                self.reset()
        else:
            self.reset()

        if self.tree is None:
            self.reset()

        self.root = self.tree.getroot()
        self.misc = self.root.find("Misc")
        if self.misc is None:
            print("Misc section not found, creating ...")
            self.misc = ET.Element("Misc")
            self.root.append(self.misc)
        self.pastebin = self.root.find("pastebin")
        if self.pastebin is None:
            print("pastebin section not found, creating ...")
            self.pastebin = ET.Element("pastebin")
            self.root.append(self.pastebin)

    def write(self):
        """Write the settings file"""
        pob_file.write_xml(self.settings_file, self.tree)

    @property
    def pastebin_dev_api_key(self):
        return self.pastebin.get("dev_api_key", "")

    @pastebin_dev_api_key.setter
    def pastebin_dev_api_key(self, new_key):
        self.pastebin.set("dev_api_key", new_key)

    @property
    def pastebin_user_api_key(self):
        return self.pastebin.get("user_api_key", "")

    @pastebin_user_api_key.setter
    def pastebin_user_api_key(self, new_key):
        self.pastebin.set("user_api_key", new_key)

    @property
    def pastebin_user_name(self):
        return self.pastebin.get("user_name", "")

    @pastebin_user_name.setter
    def pastebin_user_name(self, new_key):
        self.pastebin.set("user_name", new_key)

    @property
    def theme(self):
        _theme = self.misc.get("theme", "Dark")
        if _theme not in ("Dark", "Light"):
            _theme = "Dark"
        return _theme

    @theme.setter
    def theme(self, new_theme):
        self.misc.set("theme", new_theme and "Dark" or "Light")

    @property
    def slot_only_tooltips(self):
        return str_to_bool(self.misc.get("slotOnlyTooltips", "True"))

    @slot_only_tooltips.setter
    def slot_only_tooltips(self, new_bool):
        self.misc.set("slotOnlyTooltips", f"{new_bool}")

    @property
    def show_titlebar_name(self):
        return str_to_bool(self.misc.get("showTitlebarName", "True"))

    @show_titlebar_name.setter
    def show_titlebar_name(self, new_bool):
        self.misc.set("showTitlebarName", f"{new_bool}")

    @property
    def show_warnings(self):
        return str_to_bool(self.misc.get("showWarnings", "True"))

    @show_warnings.setter
    def show_warnings(self, new_bool):
        self.misc.set("showWarnings", f"{new_bool}")

    @property
    def default_char_level(self):
        i = int(self.misc.get("defaultCharLevel", 0))
        if 1 <= i <= 100:
            return i
        self.default_char_level = 1
        return 1

    @default_char_level.setter
    def default_char_level(self, new_level):
        self.misc.set("defaultCharLevel", f"{new_level}")

    @property
    def node_power_theme(self):
        i = int(self.misc.get("nodePowerTheme", 0))
        if 0 <= i <= 2:
            return i
        self.node_power_theme = 0
        return 0

    def node_power_theme_text(self):
        text = ["RED/BLUE", "RED/GREEN", "GREEN/BLUE"]
        return text[int(self.misc.get("nodePowerTheme", 0))]

    @node_power_theme.setter
    def node_power_theme(self, new_theme):
        self.misc.set("nodePowerTheme", f"{new_theme}")

    @property
    def connection_protocol(self):
        i = int(self.misc.get("connectionProtocol", 0))
        if 0 <= i <= 2:
            return i
        self.connection_protocol = 0
        return 0

    @connection_protocol.setter
    def connection_protocol(self, new_protocol):
        self.misc.set("connectionProtocol", f"{new_protocol}")

    @property
    def decimal_separator(self):
        # ToDo: Use locale
        # c = self.misc.get("decimalSeparator", "")
        # if c = "":
        # use locale
        return self.misc.get("decimalSeparator", ".")

    @decimal_separator.setter
    def decimal_separator(self, new_sep):
        self.misc.set("decimalSeparator", new_sep)

    @property
    def thousands_separator(self):
        # ToDo: Use locale
        # c = self.misc.get("thousandsSeparator", "")
        # if c = "":
        # use locale
        return self.misc.get("thousandsSeparator", ",")

    @thousands_separator.setter
    def thousands_separator(self, new_sep):
        self.misc.set("thousandsSeparator", new_sep)

    @property
    def show_thousands_separators(self):
        return str_to_bool(self.misc.get("showThousandsSeparators", "True"))

    @show_thousands_separators.setter
    def show_thousands_separators(self, new_bool):
        self.misc.set("showThousandsSeparators", f"{new_bool}")

    @property
    def default_gem_quality(self):
        i = int(self.misc.get("defaultGemQuality", "0"))
        if 0 <= i <= 20:
            return i
        self.default_gem_quality = 0
        return 0

    @default_gem_quality.setter
    def default_gem_quality(self, new_quality):
        self.misc.set("defaultGemQuality", f"{new_quality}")

    @property
    def build_sort_mode(self):
        return self.misc.get("buildSortMode", "NAME")

    @build_sort_mode.setter
    def build_sort_mode(self, new_mode):
        self.misc.set("buildSortMode", new_mode)

    @property
    def proxy_url(self):
        return self.misc.get("proxyURL", "")

    @proxy_url.setter
    def proxy_url(self, new_proxy):
        self.misc.set("proxyURL", new_proxy)

    @property
    def default_item_affix_quality(self):
        """Aways store the number as a float between 0 and 1.00 so stats and items can call it correctly"""
        return float(self.misc.get("defaultItemAffixQuality", ".50"))

    @default_item_affix_quality.setter
    def default_item_affix_quality(self, new_quality):
        """Aways store the number as a float between 0 and 1.00 so stats and items can call it correctly"""
        if new_quality < 0 or new_quality > 1.00:
            new_quality /= 100
        if new_quality < 0 or new_quality > 1.00:
            new_quality = 0.50
        self.misc.set("defaultItemAffixQuality", f"{new_quality}")

    @property
    def build_path(self):
        return self.misc.get("buildPath", "")

    @build_path.setter
    def build_path(self, new_path):
        self.misc.set("buildPath", new_path)

    @property
    def beta_mode(self):
        return str_to_bool(self.misc.get("betaMode", "False"))

    @beta_mode.setter
    def beta_mode(self, new_bool):
        self.misc.set("betaMode", str(new_bool))

    @property
    def size(self):
        """
        Return the window size as they were last written to settings. This ensures the user has the same experience.
        800 x 600 was chosen as the default as it has been learnt, with the lua version,
          that some users in the world have small screen laptops.
        Attempt to protect against silliness by limiting size to the screen size.
          This could happen if someone changes their desktop size or copies the program from another machine.
        :returns: a QSize(width, height)
        """
        _size = self.root.find("size")
        width = int(_size.get("width", 800))
        height = int(_size.get("height", 600))
        if width < 800:
            width = 800
        if height < 600:
            height = 600
        if width > self.screen_rect.width():
            print(f"Width: {width} is bigger than {self.screen_rect}. Correcting ...")
            width = self.screen_rect.width()
        if height > self.screen_rect.height():
            print(f"Height: {height} is bigger than {self.screen_rect}. Correcting ...")
            height = self.screen_rect.height()
        self.size = QSize(width, height)
        return QSize(width, height)

    @size.setter
    def size(self, new_size: QSize):
        _size = self.root.find("size")
        _size.set("width", f"{new_size.width()}")
        _size.set("height", f"{new_size.height()}")

    def recent_builds(self):
        """
        Recent builds are a list of xml's that have been opened, to a maximum of 10 entries
        :returns: a list of recent builds
        """
        output = []
        _recent = self.root.find("recentBuilds")
        if _recent is None:
            print("recentBuilds not found")
            self.root.append(ET.Element("recentBuilds"))
            return output
        # get all builds into an object so we can delete them from the live xml tree without crashing
        builds = _recent.findall("build")
        for idx, build in enumerate(builds):
            if idx < 10:
                output.append(build.text)
            else:
                _recent.remove(build)
        return output

    def add_recent_build(self, filename):
        """
        Adds one build to the list of recent builds
        :param filename: string: name of build xml
        :returns: n/a
        """
        _recent = self.root.find("recentBuilds")
        found = [element for element in _recent.iter() if element.text == filename]
        if len(found) == 0:
            build = ET.Element("build")
            build.text = filename
            _recent.insert(0, build)

    @property
    def last_account_name(self):
        _accounts = self.root.find("Accounts")
        return _accounts.get("lastaccountName", "")

    @last_account_name.setter
    def last_account_name(self, new_account_name):
        _accounts = self.root.find("Accounts")
        _accounts.set("lastaccountName", new_account_name)

    @property
    def last_realm(self):
        _accounts = self.root.find("Accounts")
        return _accounts.get("lastRealm", "PC")

    @last_realm.setter
    def last_realm(self, new_realm):
        _accounts = self.root.find("Accounts")
        _accounts.set("lastRealm", new_realm)

    def accounts(self):
        """
        Recent accounts are a list of accounts that have been opened, to a maximum of 10 entries
        :returns: a list of recent accounts
        """
        output = []
        _accounts = self.root.find("Accounts")
        if _accounts is None:
            print("Accounts not found")
            self.root.append(ET.Element("Accounts"))
            return output
        # get all builds into an object so we can delete them from the live xml tree without crashing
        accounts = _accounts.findall("account")
        for idx, account in enumerate(accounts):
            if idx < 20:
                output.append(account.text)
            else:
                _accounts.remove(account)
        return output

    def add_account(self, new_account):
        """
        Adds one account to the list of recent accounts
        :param new_account: string: name of account
        :returns: n/a
        """
        _account = self.root.find("Accounts")
        found = [element for element in _account.iter() if element.text == new_account]
        if len(found) == 0:
            build = ET.Element("account")
            build.text = new_account
            _account.insert(0, build)

    @Slot()
    def open_settings_dialog(self):
        """
        Load and Open the settings dialog. Save the results if needed.
        :return:
        """
        # ToDo: Another function for loading the widgets, which can also setup a default settings, for use with a default settings button
        # ToDo: show thousands separator for player stats

        @Slot()
        def setting_restore_defaults():
            set_dialog(True)

        @Slot()
        def setting_show_affix_quality_value():
            dlg.label_AffixQValue.setText(f"{dlg.slider_AffixQuality.value() / 100}")

        @Slot()
        def setting_set_build_path_tooltip():
            dlg.lineedit_BuildPath.setToolTip(dlg.lineedit_BuildPath.text())

        @Slot()
        def setting_directory_dialog():
            """
            Open a directory only file dialog for setting the build path
            :return: Path
            """
            print("setting_directory_dialog")
            directory = QFileDialog.getExistingDirectory(self, "Select Build Path")
            if directory != "":
                dlg.lineedit_BuildPath.setText(directory)

        @Slot()
        def set_dialog(default=False):
            """
            Set dialog widgets with values.
            :param default: If True, set widgets with default values
            :return:
            """
            if default:
                self.reset()
            # print_a_xml_element(_config)
            dlg.combo_Protocol.setCurrentIndex(self.connection_protocol)
            # dlg.combo_Proxy.setCurrentIndex(config.p)
            # dlg.lineedit_Proxy.setText(config.p)
            dlg.lineedit_BuildPath.setText(str(self.build_path))
            dlg.combo_NP_Colours.setCurrentIndex(self.node_power_theme)
            dlg.check_Beta.setChecked(self.beta_mode)
            dlg.check_ShowBuildName.setChecked(self.show_titlebar_name)
            dlg.check_ShowThousandsSeparators.setChecked(self.show_thousands_separators)
            dlg.lineedit_ThousandsSeparator.setText(self.thousands_separator)
            dlg.lineedit_DecimalSeparator.setText(self.decimal_separator)
            dlg.spin_GemQuality.setValue(self.default_gem_quality)
            dlg.spin_Level.setValue(self.default_char_level)
            dlg.slider_AffixQuality.setValue(int(self.default_item_affix_quality * 100))
            dlg.check_BuildWarnings.setChecked(self.show_warnings)
            dlg.check_Tooltips.setChecked(self.slot_only_tooltips)

        dlg = self.loader.load(Path(self.exe_dir, "ui_files/dlgConfig.ui"), self.win)
        # Force discard to close the dialog
        discard = dlg.btnBox.button(QDialogButtonBox.Discard)
        discard.clicked.connect(dlg.reject)
        discard.setToolTip("Abandon these setting. Change nothing.")

        restore_defaults = dlg.btnBox.button(QDialogButtonBox.RestoreDefaults)
        restore_defaults.clicked.connect(setting_restore_defaults)
        restore_defaults.setToolTip("Load the original default settings.")
        # For some reason this button comes up as default. Stop it
        restore_defaults.setAutoDefault(False)

        save = dlg.btnBox.button(QDialogButtonBox.Save)
        save.setDefault(True)
        save.setToolTip("Save the setting to current use and the settings file.")

        dlg.btn_BuildPath.clicked.connect(setting_directory_dialog)
        dlg.slider_AffixQuality.valueChanged.connect(setting_show_affix_quality_value)
        dlg.lineedit_BuildPath.textChanged.connect(setting_set_build_path_tooltip)
        # fill the fields
        set_dialog()

        # 0 is discard, 1 is save
        _return = dlg.exec()
        if _return:
            # read the fields
            self.connection_protocol = dlg.combo_Protocol.currentIndex()
            self.build_path = dlg.lineedit_BuildPath.text()
            self.node_power_theme = dlg.combo_NP_Colours.currentIndex()
            self.beta_mode = dlg.check_Beta.isChecked()
            self.show_titlebar_name = dlg.check_ShowBuildName.isChecked()
            self.show_thousands_separators = dlg.check_ShowThousandsSeparators.isChecked()
            self.thousands_separator = dlg.lineedit_ThousandsSeparator.text()
            self.decimal_separator = dlg.lineedit_DecimalSeparator.text()
            self.default_gem_quality = dlg.spin_GemQuality.value()
            self.default_char_level = dlg.spin_Level.value()
            self.default_item_affix_quality = dlg.slider_AffixQuality.value() / 100
            self.show_warnings = dlg.check_BuildWarnings.isChecked()
            self.slot_only_tooltips = dlg.check_Tooltips.isChecked()
            self.write()
        else:
            """discard a changes"""
            self.read()
        del dlg
