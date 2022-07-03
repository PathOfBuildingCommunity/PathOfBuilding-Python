"""
Configuration Class

Defines reading and writing the setting xml ass well as the settings therein
"""
import pathlib
import sys

from qdarktheme.qtpy.QtCore import QSize

import pob_xml

# Default config in case the settings file doesn't exist
default_config = {
    "PathOfBuilding": {
        "Misc": {
            "theme": "Dark",
            "slotOnlyTooltips": "true",
            "showTitlebarName": "true",
            "showWarnings": "true",
            "defaultCharLevel": "1",
            "nodePowerTheme": "RED/BLUE",
            "connectionProtocol": "nil",
            "thousandsSeparator": ",",
            "betaTest": "false",
            "decimalSeparator": ".",
            "defaultGemQuality": "0",
            "showThousandsSeparators": "true",
            "buildSortMode": "NAME",
        },
        "recentBuilds": {
            "r0": "",
            "r1": "",
            "r2": "",
            "r3": "",
            "r4": "",
        },
    }
}

custom_colours = {
    "Custom1": "#282A36",
    "Custom2": "#F8F8F2",
    "Custom3": "#44475A",
    "Custom4": "#6272A4",
    "Custom5": "#8BE9FD",
    "Custom6": "#50FA7B",
    "Custom7": "#FFB86C",
    "Custom8": "#FF79C6",
    "Custom9": "#BD93F9",
}

color_codes = {
    "NORMAL": "#000000",
    "MAGIC": "#8888FF",
    "RARE": "#FFFF77",
    "UNIQUE": "#AF6025",
    "RELIC": "#60C060",
    "GEM": "#1AA29B",
    "PROPHECY": "#B54BFF",
    "CURRENCY": "#AA9E82",
    "CRAFTED": "#B8DAF1",
    "CUSTOM": "#5CF0BB",
    "SOURCE": "#88FFFF",
    "UNSUPPORTED": "#F05050",
    "WARNING": "#FF9922",
    "TIP": "#80A080",
    "FIRE": "#B97123",
    "COLD": "#3F6DB3",
    "LIGHTNING": "#ADAA47",
    "CHAOS": "#D02090",
    "POSITIVE": "#33FF77",
    "NEGATIVE": "#DD0022",
    "OFFENCE": "#E07030",
    "DEFENCE": "#8080E0",
    "SCION": "#FFF0F0",
    "MARAUDER": "#E05030",
    "RANGER": "#70FF70",
    "WITCH": "#7070FF",
    "DUELIST": "#E0E070",
    "TEMPLAR": "#C040FF",
    "SHADOW": "#30C0D0",
    "MAINHAND": "#50FF50",
    "MAINHANDBG": "#071907",
    "OFFHAND": "#B7B7FF",
    "OFFHANDBG": "#070719",
    "SHAPER": "#55BBFF",
    "ELDER": "#AA77CC",
    "FRACTURED": "#A29160",
    "ADJUDICATOR": "#E9F831",
    "BASILISK": "#00CB3A",
    "CRUSADER": "#2946FC",
    "EYRIE": "#AAB7B8",
    "CLEANSING": "#F24141",
    "TANGLE": "#038C8C",
    "CHILLBG": "#151e26",
    "FREEZEBG": "#0c262b",
    "SHOCKBG": "#191732",
    "SCORCHBG": "#270b00",
    "BRITTLEBG": "#00122b",
    "SAPBG": "#261500",
    "SCOURGE": "#FF6E25",
}
color_codes["STRENGTH"] = color_codes["MARAUDER"]
color_codes["DEXTERITY"] = color_codes["RANGER"]
color_codes["INTELLIGENCE"] = color_codes["WITCH"]

color_codes["LIFE"] = color_codes["MARAUDER"]
color_codes["MANA"] = color_codes["WITCH"]
color_codes["ES"] = color_codes["SOURCE"]
color_codes["WARD"] = color_codes["RARE"]
color_codes["EVASION"] = color_codes["POSITIVE"]
color_codes["RAGE"] = color_codes["WARNING"]
color_codes["PHYS"] = color_codes["NORMAL"]


def str_to_bool(text: str) -> bool:
    """Convert a string to a boolean.

    As the settings could be manipulated by a human, we can't trust eval().
    EG: eval('os.system(‘rm -rf /’)')
    return True if it looks like it could be true, otherwise false.
    """
    return text.lower() in {"yes", "true", "t", "1", "on"}


class Config:
    def __init__(self) -> None:
        self.config = {}
        self.exe_dir = pathlib.Path(sys.argv[0]).absolute().parent
        self.build_path = self.exe_dir / "builds"
        self.settings_path = self.exe_dir / "settings.xml"
        self.build_path.mkdir(exist_ok=True)

    def read(self) -> None:
        config = pob_xml.read_xml(self.settings_path)
        self.config = config if config is not None else default_config

    def write(self) -> None:
        pob_xml.write_xml(self.settings_path, self.config)

    @property
    def theme(self):
        return self.config["PathOfBuilding"]["Misc"]["theme"]

    @theme.setter
    def theme(self, new_theme):
        self.config["PathOfBuilding"]["Misc"]["theme"] = new_theme

    def slotOnlyTooltips(self):
        return str_to_bool(self.config["PathOfBuilding"]["Misc"]["slotOnlyTooltips"])

    def set_slotOnlyTooltips(self, new_bool):
        self.config["PathOfBuilding"]["Misc"]["slotOnlyTooltips"] = str(new_bool)

    def showTitlebarName(self):
        return str_to_bool(self.config["PathOfBuilding"]["Misc"]["showTitlebarName"])

    def set_showTitlebarName(self, new_bool):
        self.config["PathOfBuilding"]["Misc"]["showTitlebarName"] = str(new_bool)

    def showWarnings(self):
        return str_to_bool(self.config["PathOfBuilding"]["Misc"]["showWarnings"])

    def set_showWarnings(self, new_bool):
        self.config["PathOfBuilding"]["Misc"]["showWarnings"] = str(new_bool)

    def defaultCharLevel(self):
        return int(self.config["PathOfBuilding"]["Misc"]["defaultCharLevel"])

    def set_defaultCharLevel(self, new_int):
        self.config["PathOfBuilding"]["Misc"]["defaultCharLevel"] = str(new_int)

    def nodePowerTheme(self):
        return self.config["PathOfBuilding"]["Misc"]["nodePowerTheme"]

    def set_NodePowerTheme(self, new_theme):
        self.config["PathOfBuilding"]["Misc"]["nodePowerTheme"] = new_theme

    def connectionProtocol(self):
        return self.config["PathOfBuilding"]["Misc"]["connectionProtocol"]

    def set_connectionProtocol(self, new_conn):
        # what is this for
        self.config["PathOfBuilding"]["Misc"]["connectionProtocol"] = new_conn

    def decimalSeparator(self):
        return self.config["PathOfBuilding"]["Misc"]["decimalSeparator"]

    def set_decimalSeparator(self, new_sep):
        self.config["PathOfBuilding"]["Misc"]["decimalSeparator"] = new_sep

    def thousandsSeparator(self):
        return self.config["PathOfBuilding"]["Misc"]["thousandsSeparator"]

    def set_thousandsSeparator(self, new_sep):
        self.config["PathOfBuilding"]["Misc"]["thousandsSeparator"] = new_sep

    def showThousandsSeparators(self):
        return str_to_bool(
            self.config["PathOfBuilding"]["Misc"]["showThousandsSeparators"]
        )

    def set_showThousandsSeparators(self, new_bool):
        self.config["PathOfBuilding"]["Misc"]["showThousandsSeparators"] = str(new_bool)

    def defaultGemQuality(self):
        return self.config["PathOfBuilding"]["Misc"]["defaultGemQuality"]

    def set_defaultGemQuality(self, new_int):
        if new_int < 0 or new_int > 20:
            new_int = 0
        self.config["PathOfBuilding"]["Misc"]["defaultGemQuality"] = str(new_int)

    def buildSortMode(self):
        return self.config["PathOfBuilding"]["Misc"]["buildSortMode"]

    def set_buildSortMode(self, new_mode):
        self.config["PathOfBuilding"]["Misc"]["buildSortMode"] = new_mode

    def betaMode(self):
        return self.config["PathOfBuilding"]["Misc"]["betaMode"]

    def set_betaMode(self, new_bool):
        self.config["PathOfBuilding"]["Misc"]["betaMode"] = str(new_bool)

    def recentBuilds(self):
        output = dict()
        try:
            output = self.config["PathOfBuilding"]["recentBuilds"]
        except:
            print("recentBuilds exception")
            output = {
                "r0": "",
                "r1": "",
                "r2": "",
                "r3": "",
                "r4": "",
            }
        self.config["PathOfBuilding"]["recentBuilds"] = output
        return output

    def size(self):
        try:
            width = int(self.config["PathOfBuilding"]["size"]["width"])
            height = int(self.config["PathOfBuilding"]["size"]["height"])
        except KeyError:
            width = 800
            height = 600
            self.set_size(QSize(width, height))
        return QSize(width, height)

    def set_size(self, new_size: QSize):
        self.config["PathOfBuilding"]["size"] = {
            "width": new_size.width(),
            "height": new_size.height(),
        }
