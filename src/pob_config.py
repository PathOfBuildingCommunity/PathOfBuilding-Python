
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
from collections import OrderedDict

from qdarktheme.qtpy.QtCore import QSize

import pob_file
from constants import *
from constants import _VERSION


def str_to_bool(in_str):
    """
    Return a boolean from a string. As the settings could be manipulated by a human, we can't trust eval()
      EG: eval('os.system(`rm -rf /`)')
    :returns: True if it looks like it could be true, otherwise false
    """
    return in_str.lower() in ("yes", "true", "t", "1", "on")


class Config:
    def __init__(self, _win, _app) -> None:
        # To reduce circular references, have the app and main window references here
        self.win = _win
        self.app = _app
        self.config = (
            None  # this is the dictionary representing the xml, not a pointer to itself
        )
        self.screen_rect = self.app.primaryScreen().size()

        self.current_spec = empty_build["PathOfBuilding"]["Tree"]["Spec"]
        self.default_notes_text_colour = None

        self.exeDir = Path.cwd()
        self.settingsFile = Path(self.exeDir, "settings.xml")
        self.buildPath = Path(self.exeDir, "builds")
        if not self.buildPath.exists():
            self.buildPath.mkdir()
        self.tree_data_path = Path(self.exeDir, "TreeData")
        if not self.tree_data_path.exists():
            self.tree_data_path.mkdir()
        self.misc = {}
        self.read()

    def read(self):
        """Set self.config with the contents of the settings file"""
        if self.settingsFile.exists():
            # try:
            self.config = OrderedDict(pob_file.read_xml(self.settingsFile))
            self.misc = self.config["PathOfBuilding"]["Misc"]
        if self.config is None:
            self.config = default_config

    def write(self):
        """Write the settings file"""
        pob_file.write_xml(self.settingsFile, self.config)

    @property
    def theme(self):
        _theme = self.misc.get("theme", "Dark")
        if _theme not in ("Dark", "Light"):
            _theme = "Dark"
        return _theme

    @theme.setter
    def theme(self, new_theme):
        self.misc["theme"] = new_theme and "Dark" or "Light"

    @property
    def slotOnlyTooltips(self):
        return str_to_bool(self.misc.get("slotOnlyTooltips", True))

    @slotOnlyTooltips.setter
    def slotOnlyTooltips(self, new_bool):
        self.misc["slotOnlyTooltips"] = str(new_bool)

    @property
    def showTitlebarName(self):
        return str_to_bool(self.misc.get("showTitlebarName", True))

    @showTitlebarName.setter
    def showTitlebarName(self, new_bool):
        self.misc["showTitlebarName"] = str(new_bool)

    @property
    def showWarnings(self):
        return str_to_bool(self.misc.get("showWarnings", True))

    @showWarnings.setter
    def showWarnings(self, new_bool):
        self.misc["showWarnings"] = str(new_bool)

    @property
    # fmt: off
    def defaultCharLevel(self):
        _defaultCharLevel = self.misc.get("defaultCharLevel", 1)
        if _defaultCharLevel < 1:
            _defaultCharLevel = 1
            self.misc["defaultCharLevel"] = f"{_defaultCharLevel}"
        if _defaultCharLevel > 100:
            _defaultCharLevel = 100
            self.misc["defaultCharLevel"] = f"{_defaultCharLevel}"
        return _defaultCharLevel
    # fmt: on

    @defaultCharLevel.setter
    def defaultCharLevel(self, new_int):
        self.misc["defaultCharLevel"] = f"{new_int}"

    @property
    def nodePowerTheme(self):
        return self.misc.get("nodePowerTheme", "RED/BLUE")

    @nodePowerTheme.setter
    def nodePowerTheme(self, new_theme):
        self.misc["nodePowerTheme"] = new_theme

    @property
    def connectionProtocol(self):
        return self.misc.get("connectionProtocol", "nil")

    @connectionProtocol.setter
    def connectionProtocol(self, new_conn):
        # what is this for
        self.misc["connectionProtocol"] = new_conn

    @property
    def decimalSeparator(self):
        return self.misc.get("decimalSeparator", ".")

    @decimalSeparator.setter
    def decimalSeparator(self, new_sep):
        self.misc["decimalSeparator"] = new_sep

    @property
    def thousandsSeparator(self):
        return self.misc.get("thousandsSeparator", ",")

    @thousandsSeparator.setter
    def thousandsSeparator(self, new_sep):
        self.misc["thousandsSeparator"] = new_sep

    @property
    def showThousandsSeparators(self):
        return str_to_bool(self.misc.get("showThousandsSeparators", True))

    @showThousandsSeparators.setter
    def showThousandsSeparators(self, new_bool):
        self.misc["showThousandsSeparators"] = str(new_bool)

    @property
    # fmt: off
    def defaultGemQuality(self):
        _defaultGemQuality = self.misc.get("defaultGemQuality", 1)
        if _defaultGemQuality < 0:
            _defaultGemQuality = 0
            self.misc["defaultGemQuality"] = f"{_defaultGemQuality}"
        if _defaultGemQuality > 20:
            _defaultGemQuality = 0
            self.misc["defaultGemQuality"] = f"{_defaultGemQuality}"
        return _defaultGemQuality
    # fmt: on

    @defaultGemQuality.setter
    def defaultGemQuality(self, new_int):
        self.misc["defaultGemQuality"] = f"{new_int}"

    @property
    def buildSortMode(self):
        return self.misc.get("buildSortMode", "NAME")

    @buildSortMode.setter
    def buildSortMode(self, new_mode):
        self.misc["buildSortMode"] = new_mode

    @property
    def betaMode(self):
        return str_to_bool(self.misc.get("betaMode", False))

    @betaMode.setter
    def betaMode(self, new_bool):
        self.misc["betaMode"] = str(new_bool)

    @property
    def size(self):
        """
        Return the window size as they were last written to settings. This ensures the user has the same experience.
        800 x 600 was chosen as the default as it has been learnt, with the lua version,
          that some users in the world have small screen laptops.
        Attempt to protect against silliness by limiting size to the screen size.
          This could happen if someone changes their desktop size or copy program from another machine.
        :returns: a QSize(width, height)
        """
        try:
            width = int(self.config["PathOfBuilding"]["size"]["width"])
            if width < 800:
                width = 800
            height = int(self.config["PathOfBuilding"]["size"]["height"])
            if height < 600:
                height = 600
        except KeyError:
            width = 800
            height = 600
        if width > self.screen_rect.width():
            print(f"Width: {width} is bigger than {self.screen_rect}. Correcting ...")
            _size = self.screen_rect
        if height > self.screen_rect.height():
            print(f"Height: {height} is bigger than {self.screen_rect}. Correcting ...")
            _size = self.screen_rect
        return QSize(width, height)

    @size.setter
    def size(self, new_size: QSize):
        self.config["PathOfBuilding"]["size"] = {
            "width": new_size.width(),
            "height": new_size.height(),
        }

    def recent_builds(self):
        """
        Recent builds are a list of xml's that have been opened, to a maximum of 10 entries
        :returns: an Ordered dictionary list of recent builds
        """
        try:
            output = self.config["PathOfBuilding"]["recentBuilds"]
        except KeyError:
            print("recentBuilds exception")
            output = {
                "r0": "",
                "r1": "",
                "r2": "",
                "r3": "",
                "r4": "",
            }
        self.config["PathOfBuilding"]["recentBuilds"] = output
        return OrderedDict(output)

    def add_recent_build(self, filename):
        """
        Adds one build to the list of recent builds
        :param filename: str(): name of build xml
        :returns: n/a
        """
        if filename not in self.config["PathOfBuilding"]["recentBuilds"].values():
            for idx in [3, 2, 1, 0]:
                # fmt: off
                self.config["PathOfBuilding"]["recentBuilds"][f"r{idx + 1}"]\
                    = self.config["PathOfBuilding"]["recentBuilds"][f"r{idx}"]
                # fmt: on
            self.config["PathOfBuilding"]["recentBuilds"]["r0"] = filename
