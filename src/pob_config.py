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


def print_call_stack():
    """
    Ahh debug. It's wonderful
    :return:
    """
    for line in traceback.format_stack():
        print(line.strip())


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
        self.exeDir = Path.cwd()
        self.settingsFile = Path(self.exeDir, "settings.xml")
        self.buildPath = Path(self.exeDir, "builds")
        if not self.buildPath.exists():
            self.buildPath.mkdir()
        self.tree_data_path = Path(self.exeDir, "TreeData")
        if not self.tree_data_path.exists():
            self.tree_data_path.mkdir()
        self.read()

    def read(self):
        """Set self.root with the contents of the settings file"""
        if self.settingsFile.exists():
            try:
                self.tree = pob_file.read_xml(self.settingsFile)
            except ET.ParseError:
                self.tree = ET.ElementTree(ET.fromstring(default_config))
        else:
            self.tree = ET.ElementTree(ET.fromstring(default_config))

        if self.tree is None:
            self.tree = ET.ElementTree(ET.fromstring(default_config))

        self.root = self.tree.getroot()
        self.misc = self.root.find("Misc")
        if self.misc is None:
            print("Misc not found")
            self.misc = ET.Element("Misc")
            self.root.append(self.misc)

    def write(self):
        """Write the settings file"""
        pob_file.write_xml(self.settingsFile, self.tree)

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
    def slotOnlyTooltips(self):
        return str_to_bool(self.misc.get("slotOnlyTooltips", True))

    @slotOnlyTooltips.setter
    def slotOnlyTooltips(self, new_bool):
        self.misc.set("slotOnlyTooltips", str(new_bool))

    @property
    def showTitlebarName(self):
        return str_to_bool(self.misc.get("showTitlebarName", True))

    @showTitlebarName.setter
    def showTitlebarName(self, new_bool):
        self.misc.set("showTitlebarName", f"{new_bool}")

    @property
    def showWarnings(self):
        return str_to_bool(self.misc.get("showWarnings", True))

    @showWarnings.setter
    def showWarnings(self, new_bool):
        self.misc.set("showWarnings", str(new_bool))

    @property
    # fmt: off
    def defaultCharLevel(self):
        _defaultCharLevel = self.misc.get("defaultCharLevel", 1)
        if _defaultCharLevel < 1:
            _defaultCharLevel = 1
            self.misc.set("defaultCharLevel", f"{_defaultCharLevel}")
        if _defaultCharLevel > 100:
            _defaultCharLevel = 100
            self.misc.set("defaultCharLevel", f"{_defaultCharLevel}")
        return _defaultCharLevel
    # fmt: on

    @defaultCharLevel.setter
    def defaultCharLevel(self, new_int):
        self.misc.set("defaultCharLevel", f"{new_int}")

    @property
    def nodePowerTheme(self):
        return self.misc.get("nodePowerTheme", "RED/BLUE")

    @nodePowerTheme.setter
    def nodePowerTheme(self, new_theme):
        self.misc.set("nodePowerTheme", new_theme)

    @property
    def connectionProtocol(self):
        return self.misc.get("connectionProtocol", "nil")

    @connectionProtocol.setter
    def connectionProtocol(self, new_conn):
        # what is this for
        self.misc.set("connectionProtocol", new_conn)

    @property
    def decimalSeparator(self):
        return self.misc.get("decimalSeparator", ".")

    @decimalSeparator.setter
    def decimalSeparator(self, new_sep):
        self.misc.set("decimalSeparator", new_sep)

    @property
    def thousandsSeparator(self):
        return self.misc.get("thousandsSeparator", ",")

    @thousandsSeparator.setter
    def thousandsSeparator(self, new_sep):
        self.misc.set("thousandsSeparator", new_sep)

    @property
    def showThousandsSeparators(self):
        return str_to_bool(self.misc.get("showThousandsSeparators", True))

    @showThousandsSeparators.setter
    def showThousandsSeparators(self, new_bool):
        self.misc.set("showThousandsSeparators", str(new_bool))

    @property
    # fmt: off
    def defaultGemQuality(self):
        _defaultGemQuality = self.misc.get("defaultGemQuality", 1)
        if _defaultGemQuality < 0:
            _defaultGemQuality = 0
            self.misc.set("defaultGemQuality", f"{_defaultGemQuality}")
        if _defaultGemQuality > 20:
            _defaultGemQuality = 0
            self.misc.set("defaultGemQuality", f"{_defaultGemQuality}")
        return _defaultGemQuality
    # fmt: on

    @defaultGemQuality.setter
    def defaultGemQuality(self, new_int):
        self.misc.set("defaultGemQuality", f"{new_int}")

    @property
    def buildSortMode(self):
        return self.misc.get("buildSortMode", "NAME")

    @buildSortMode.setter
    def buildSortMode(self, new_mode):
        self.misc.set("buildSortMode", new_mode)

    @property
    def betaMode(self):
        return str_to_bool(self.misc.get("betaMode", False))

    @betaMode.setter
    def betaMode(self, new_bool):
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
