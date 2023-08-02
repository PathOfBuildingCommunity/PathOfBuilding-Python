"""
A class to encapsulate one mod.
Numeric values default to None so that they can be checked for non use. -1 or 0 could be legitimate values.
"""

import xml.etree.ElementTree as ET
import re

from pob_config import _debug, index_exists, str_to_bool, bool_to_str, print_call_stack
from pob_file import read_xml, write_xml
from constants import slot_map, ColourCodes
from widgets.ui_utils import HTMLDelegate, html_colour_text


class Mod:
    def __init__(self, _line) -> None:
        """
        Initialise defaults
        :param _line: the full line of the mod, including variant stanzas.
        """
        # this is the text without {variant}, {crafted}. At this point {range} is still present
        self.line = re.sub(
            r"{variant:\d+}",
            "",
            _line.replace("{crafted}", "").replace("{fractured}", ""),
        )
        # this is the text with the (xx-yy), eg '% increased Duration'.
        # It is to avoid recalculating this value needlessly
        self.line_without_range = None
        # print(f"\n_line", _line)
        self.corrupted = self.line == "Corrupted"
        if self.corrupted:
            self.tooltip = f'{html_colour_text("STRENGTH",self.line)}<br/>'
            return

        # value for managing the range of values. EG: 20-40% of ... _range will be between 0 and 1
        self._range = -1
        self.min = 0
        self.max = 0
        # the actual value of the mod, where valid. EG: if _range is 0.5, then this will be 30%
        self.value = 0

        self.crafted = "{crafted}" in _line
        self.fractured = "{fractured}" in _line
        self.tooltip_colour = ColourCodes.MAGIC.value
        if self.crafted:
            self.tooltip_colour = ColourCodes.CRAFTED.value
        if self.fractured:
            self.tooltip_colour = ColourCodes.FRACTURED.value
        # preformed text for adding to the tooltip. Let's set a default in case there is no 'range'
        self.tooltip = f"{html_colour_text(self.tooltip_colour, self.line)}<br/>"

        # check for and keep variant information
        m = re.search(r"({variant:\d+})", _line)
        self.variant_text = m and m.group(1) or None

        # sort out the range, min, max,value and the tooltip, if applicable
        tooltip = self.line
        m1 = re.search(r"{range:([0-9.]+)}(.*)", tooltip)
        if m1:
            # this is now stripped of the {range:n}
            self.line = m1.group(2)
            m2 = re.search(r"\(([0-9.]+)-([0-9.]+)\)(.*)", self.line)
            if m2:
                self.min = float(m2.group(1))
                self.max = float(m2.group(2))
                self.line_without_range = m2.group(3)[1:]

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
        self.value = self.min + (self.max - self.min) * self.range
        # get the value without the trailing .0, so we don't end up with 40.0% or such.
        value = f"{self.value:.1f}".replace(".0", "")
        # put the crafted colour on the value only
        tooltip = f'{html_colour_text("CRAFTED",value)}{self.line_without_range}'
        # colour the whole tip
        self.tooltip = f"{html_colour_text(self.tooltip_colour,tooltip)}<br/>"
