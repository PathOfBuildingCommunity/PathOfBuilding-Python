"""
Configuration Class

Defines reading and writing the settings xml as well as the settings therein
The variables that come from the lua version of Path of Building retain their current naming
As the settings.xml can be altered by humans, care must be taken to ensure data integrity, where possible

Global constants as found in all locations in the lua version

This is a base PoB class. It doesn't import any other PoB ui classes
Imports pob_file
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import traceback
from collections import OrderedDict

from qdarktheme.qtpy.QtCore import QSize

import pob_file
from constants import *


def str_to_bool(in_str):
    """
    Return a boolean from a string. As the settings could be manipulated by a human, we can't trust eval()
      EG: eval('os.system(`rm -rf /`)')
    :param: str: The setting to be evaluated
    :returns: True if it looks like it could be true, otherwise False
    """
    return in_str.lower() in ("yes", "true", "t", "1", "on")


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
    except (IndexError, KeyError):
        return False


def print_call_stack(full=False):
    """
    Ahh debug. It's wonderful
    :param: full: Bool: True if you want the full stack trace,
            elsewise just print the parent caller of the function that called this
    :return:
    """
    lines = traceback.format_stack()
    if full:
        for line in lines:
            print(line.strip())
            print()
    else:
        print(lines[-3].strip())


def print_a_xml_element(the_element):
    """
    Debug: Print the contents so you can see what happened and why 'it' isn't working.
    Prints the parent caller to help track when there are many of them.
    :param the_element: xml element
    :return:
    """
    lines = traceback.format_stack()
    print(lines[-2].strip())
    print(ET.tostring(the_element, encoding='utf8').decode('utf8'))
    print()


class Config:
    def __init__(self, _win, _app) -> None:
        # To reduce circular references, have the app and main window references here
        self.win = _win
        self.app = _app
        self.screen_rect = self.app.primaryScreen().size()

        # this is the xml tree representing the xml
        self.root = None
        self.tree = None
        # easy access to the Misc tag
        self.misc = None

        # Path and directory variables
        self.exe_dir = Path.cwd()
        self.settings_file = Path(self.exe_dir, "settings.xml")
        self.build_dir = Path(self.exe_dir, "builds")
        if not self.build_dir.exists():
            self.build_dir.mkdir()
        self.tree_data_path = Path(self.exe_dir, "TreeData")
        if not self.tree_data_path.exists():
            self.tree_data_path.mkdir()
        self.read()

    def reset(self):
        """Reset to default config"""
        self.tree = ET.ElementTree(ET.fromstring(default_config))
        self.root = self.tree.getroot()
        self.misc = self.root.find("Misc")

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
            print("Misc not found")
            self.misc = ET.Element("Misc")
            self.root.append(self.misc)

    def write(self):
        """Write the settings file"""
        pob_file.write_xml(self.settings_file, self.tree)

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
        return float(self.misc.get("defaultItemAffixQuality", ".50"))

    @default_item_affix_quality.setter
    def default_item_affix_quality(self, new_quality):
        self.misc.set("defaultItemAffixQuality", f"{new_quality}")

    @property
    def build_path(self):
        _dir = self.misc.get("buildPath", "")
        if _dir == "":
            _dir = self.build_dir
        return _dir

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
        :returns: an Ordered dictionary list of recent builds
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
