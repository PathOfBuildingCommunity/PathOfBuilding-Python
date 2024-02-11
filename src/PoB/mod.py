"""
A class to encapsulate one mod.
Numeric values default to None so that they can be checked for non use. -1 or 0 could be legitimate values.
"""

import xml.etree.ElementTree as ET
import re

from PoB.pob_file import read_xml, write_xml
from PoB.constants import slot_map, ColourCodes
from widgets.ui_utils import _debug, html_colour_text, format_number, index_exists, str_to_bool, bool_to_str, print_call_stack


class Mod:
    def __init__(self, settings, _line) -> None:
        """
        Initialise defaults
        :param _line: the full line of the mod, including variant stanzas.
        """
        # this is the text without {variant}, {crafted}. At this point {range} is still present
        self.settings = settings
        self.line = re.sub(
            r"{variant:\d+}",
            "",
            _line.replace("{crafted}", "").replace("{fractured}", "").replace("{crucible}", ""),
        )
        # this is the text with the (xx-yy), eg '% increased Duration'.
        # It is to avoid recalculating this value needlessly
        self.line_without_range = ""
        self.line_with_range = ""
        # print(f"\n_line", _line)
        self.corrupted = self.line == "Corrupted"
        if self.corrupted:
            self.tooltip = f'{html_colour_text("STRENGTH",self.line)}<br/>'
            return

        # value for managing the range of values. EG: 20-40% of ... _range will be between 0 and 1
        self._range = -1
        self.min = 0
        self.max = 0
        self.range_sep = ""
        self.min2 = 0
        self.max2 = 0
        # the actual value of the mod, where valid. EG: if _range is 0.5, then this will be 30%
        self.value = 0
        self.value2 = 0

        self.crafted = "{crafted}" in _line
        self.fractured = "{fractured}" in _line
        self.crucible = "{crucible}" in _line
        self.tooltip_colour = ColourCodes.MAGIC.value
        if self.crafted:
            self.tooltip_colour = ColourCodes.CRAFTED.value
        if self.fractured:
            self.tooltip_colour = ColourCodes.FRACTURED.value
        if self.crucible:
            self.tooltip_colour = ColourCodes.CRUCIBLE.value
        # preformed text for adding to the tooltip. Let's set a default in case there is no 'range'
        self.tooltip = f"{html_colour_text(self.tooltip_colour, self.line)}<br/>"

        # check for and keep variant information
        m = re.search(r"({variant:\d+})", _line)
        self.variant_text = m and m.group(1) or None

        # sort out the range, min, max,value and the tooltip, if applicable
        tooltip = self.line
        self.line_without_range = self.line
        m1 = re.search(r"{range:([0-9.]+)}(.*)", tooltip)
        if m1:
            # this is now stripped of the {range:n}
            self.line = m1.group(2)
            m2 = (
                re.search(r"\(([0-9.]+)-([0-9.]+)\)(.*)\(([0-9.]+)-([0-9.]+)\)(.*)", self.line)
                or re.search(r"\(([0-9.]+)-([0-9.]+)\)(.*)", self.line)
                or re.search(r"([0-9.]+) to ([0-9.]+)", self.line)
            )
            match len(m2.groups()):
                case 2:
                    print(f"2: {m2.groups()=}, {self.line=}")
                case 3:
                    self.min = float(m2.group(1))
                    self.max = float(m2.group(2))
                    self.line_without_range = re.sub(r"\([0-9.]+-[0-9.]+\)", "{}", self.line)
                    self.range = float(m1.group(1))  # Trigger setting self.value and self.line_with_range
                case 6:
                    self.min = float(m2.group(1))
                    self.max = float(m2.group(2))
                    self.range_sep = m2.group(3)
                    self.min2 = float(m2.group(4))
                    self.max2 = float(m2.group(5))
                    self.line_without_range = re.sub(r"\([0-9.]+-[0-9.]+\)", "{0}", self.line, count=1)
                    self.line_without_range = re.sub(r"\([0-9.]+-[0-9.]+\)", "{1}", self.line_without_range, count=1)
                    self.range = float(m1.group(1))  # Trigger setting self.value and self.line_with_range

            # trigger property to update value and tooltip
            self.range = float(m1.group(1))
        # print("self.text", self.text)

    @property
    def text_for_xml(self):
        """Return the text formatted for the xml output"""
        text = (
            f'{self.variant_text and self.variant_text or ""}'
            f'{self.crafted and "{crafted}" or ""}'
            f'{self.fractured and "{fractured}" or ""}'
            f'{self.crucible and "{crucible}" or ""}'
        )
        if self.range >= 0:
            r = f"range:{self.range}".rstrip("0").rstrip(".")
            text += f"{{{r}}}"
        text += f'{self.line.replace("&", "&amp;")}'
        return text

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, new_range):
        """Set a new range and update value and tooltip"""
        self._range = new_range
        self.value = self.min + ((self.max - self.min) * self.range)
        # get the value without the trailing .0, so we don't end up with 40.0% or such.
        fmt = self.value < 10 and "%0.3g" or "%0.5g"
        # value_str = format_number(self.value, fmt, self.settings)
        # put the crafted colour on the value only
        value_str = html_colour_text("CRAFTED", format_number(self.value, fmt, self.settings))
        if self.min2:
            self.value2 = self.min2 + ((self.max2 - self.min2) * self.range)
            # value_str2 = format_number(self.value2, fmt, self.settings)
            value_str2 = html_colour_text("CRAFTED", format_number(self.value2, fmt, self.settings))
            self.line_with_range = self.line_without_range.format(value_str, value_str2)
        else:
            self.line_with_range = self.line_without_range.format(value_str)
        # tooltip = f'{html_colour_text("CRAFTED",value_str)}{self.line_without_range}'
        # colour the whole tip
        self.tooltip = f"{html_colour_text(self.tooltip_colour,self.line_with_range)}<br/>"
