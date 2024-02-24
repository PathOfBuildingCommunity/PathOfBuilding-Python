"""
Utilities for the UI that do not have dependencies on MainWindow
"""

import base64
import datetime
import glob
import itertools
import operator
import re
import traceback
import zlib
import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize
from PySide6.QtGui import QAbstractTextDocumentLayout, QPalette, QTextDocument
from PySide6.QtWidgets import QApplication, QComboBox, QProxyStyle, QStyle, QStyleOptionViewItem, QStyledItemDelegate

from PoB.constants import ColourCodes, pob_debug, locale


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


is_str_a_boolean = str_to_bool


def is_str_a_number(in_str):
    """
    Check if this string is a number
    :param: in_str: String: The setting to be evaluated
    :returns: True if it looks like it could be afloat or integer
    """
    return in_str.startswith("-") and in_str[1:].isdigit() or in_str.isdigit()


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
        print(f"{datetime.datetime.now()}: {text}", ":", lines[-2].strip().partition("\n")[0])


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


def html_colour_text(colour, text):
    """
    Put text into html span tags.

    :param colour: string: the #xxxxxx colour to be used or ColourCodes name.
    :param text: the text to be coloured.
    :return: str: html colour coded text.
    """
    if colour[0] == "#":
        c = colour
    else:
        c = ColourCodes[colour.upper()].value
    newline = "\n"
    return f'<span style="color:{c};">{text.replace(newline,"<BR>")}</span>'


def set_combo_index_by_data(_combo: QComboBox, _data):
    """
    Set a combo box current index based on it's data field.

    :param _combo: the combo box.
    :param _data: the data. There is no type to this, so the passed in type should match what the combo has.
    :return: int: the index of the combobox or -1 if not found.
    """
    if _data is None:
        _data = "None"
    # print_call_stack()
    for i in range(_combo.count()):
        if _combo.itemData(i) == _data:
            _combo.setCurrentIndex(i)
            return i
    return -1


def set_combo_index_by_text(_combo: QComboBox, _text):
    """
    Set a combo box current index based on it's text field.

    :param _combo: the combo box.
    :param _text: string: the text.
    :return: int: the index of the combobox or -1 if not found.
    """
    if _text is None:
        _text = "None"
    # print_call_stack()
    for i in range(_combo.count()):
        if _combo.itemText(i) == _text:
            _combo.setCurrentIndex(i)
            return i
    return -1


def format_number(the_number, format_str, settings, pos_neg_colour=False):
    """
    Locale aware number formatting
    :param the_number: int or float.
    :param format_str: str: A format string : like '%10.2f' or '%d'
    :param settings: Settings(). So we can access the colours and show_thousands_separators
    :param pos_neg_colour: bool. Whether to colour the return value
    :return: str: String represntation of the number, formatted as needed.
    """
    # if format is an int, force the value to be an int.
    if "d" in format_str:
        the_number = round(the_number)  # locale.format_string will round 99.5 or 99.6 to 99 using a %d format_str (truncates).
    return_str = locale.format_string(format_str, the_number, grouping=settings.show_thousands_separators)
    if pos_neg_colour:
        colour = the_number < 0 and settings.colour_negative or settings.colour_positive
        return_str = html_colour_text(colour, return_str)
    return return_str


def search_list_for_regex(_list, regex, debug=False) -> list:
    """
    Standardise the regex searching of stats.
    :param _list: list of stats that should match the regex.
    :param regex: the regex.
    :param debug: bool: Ease of printing facts for a given specification.
    :return: list: the list of values that match the regex.
    """
    return [line for line in _list if re.search(regex, line)]


def search_stats_list_for_regex(stat_list, regex, default_value, debug=False) -> list:
    """
    Standardise the regex searching of stats
    :param stat_list: list of stats that should match the regex.
    :param regex: the regex.
    :param default_value: int: A value that suits the calculation if no stats found (EG: 1 for multiplication, 0 for addition).
    :param debug: bool: Ease of printing facts for a given specification.
    :return: list: the list of values of the digits. Some results need to be sum'd and others product'd.
    """
    value = []
    for stat in stat_list:
        m = re.search(regex, stat)
        # print(f"{stat=}, {regex=}")
        if m:
            if debug:
                print(f"{stat=}, {regex=}, {value=}, {m=}")
            value.append(int(m.group(1)))
    return value == [] and [int(default_value)] or value


# https://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt
class HTMLDelegate(QStyledItemDelegate):
    def __init__(self) -> None:
        super().__init__()
        # the list of WidgetItems from a QListView
        self._list = None
        self.doc = QTextDocument()

    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        style = QApplication.style() if options.widget is None else options.widget.style()

        doc = QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(text_rect.topLeft())
        painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """Inherited function to return the max width of all text items"""
        if type(index) == int:
            # print("HTMLDelegate.sizeHint", self._list.objectName(), index)
            self.doc.setHtml(self._list.item(index).text())
        else:
            # print("HTMLDelegate.sizeHint", self._list.objectName(), index.row())
            self.doc.setHtml(self._list.item(index.row()).text())
        return QSize(self.doc.idealWidth() + 20, self.doc.size().height())
