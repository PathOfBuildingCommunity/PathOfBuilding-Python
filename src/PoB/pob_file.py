"""
Functions for reading and writing xml and json

This is a base PoB class. It doesn't import any other PoB classes
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import xmltodict
import json
import os
import xml

from PoB.constants import ColourCodes


def get_file_info(win, filename, max_length, max_filename_width=40, html=True):
    """
    Open the xml and get the class information, level and version. Format a line for display on the listbox.
    Take into account the maximum width of the listbox and trim names as needed.

    :param win: windows.main_window.MainWindow: pointer to the mainwindow.
    :param filename: name of file in current directory.
    :param max_length: int: of the longest name.
    :param max_filename_width: int: Maximum number of characters of the filename to be shown.
    :param html: bool: If True return the text as html formatted.
    :return: str, str: "", "" if invalid xml, or colourized name and class name.
    """
    try:
        xml_file = read_xml_as_dict(filename)
    except xml.parsers.expat.ExpatError:  # Corrupt file
        return "", ""

    xml_build = xml_file.get("PathOfBuilding", {}).get("Build", {})
    if xml_build != {}:
        name = os.path.splitext(filename)[0]
        # Get the maximum length of a name, trimming it if need be
        name = len(name) > max_filename_width and (name[:max_filename_width] + "..") or name
        # Create a spacer string of the correct length to right justify the class info
        spacer = (min(max_length, max_filename_width) - len(name) + 4) * " "

        # The information on the right
        version = xml_build.get("@version", "1")
        level = xml_build.get("@level", "1")
        class_name = xml_build.get("@className", "Scion")
        ascend_class_name = xml_build.get("@ascendClassName", "None")
        _class = ascend_class_name == "None" and class_name or ascend_class_name
        info_text = f" Level {level} {_class} (v{version})"

        colour = ColourCodes[class_name.upper()].value
        normal = win.qss_default_text  # Default text's colour
        if html:
            return (
                f'<pre style="color:{normal};">{name}{spacer}<span style="color:{colour};">{info_text}</span></pre>',
                class_name,
            )
        else:
            return f"{name}{spacer}{info_text}", class_name
    else:
        return "", ""


def read_xml_as_dict(filename):
    """
    Reads a XML file
    :param filename: Name of xml to be read
    :returns: A dictionary of the contents of the file
    """
    _fn = Path(filename)
    if _fn.exists():
        try:
            with _fn.open("r") as xml_file:
                xml_content = xml_file.read()
                _dict = xmltodict.parse(xml_content)
                return _dict
        # parent of IOError, OSError *and* WindowsError where available
        except EnvironmentError:
            print(f"Unable to open {_fn}")
    return None


def read_xml(filename):
    """
    Reads a XML file
    :param filename: Name of xml to be read
    :returns: A xml tree of the contents of the file
    """
    _fn = Path(filename)
    if _fn.exists():
        try:
            with _fn.open("r") as xml_file:
                tree = ET.parse(_fn)
                return tree
        # parent of IOError, OSError *and* WindowsError where available
        except (EnvironmentError, FileNotFoundError, ET.ParseError):
            print(f"Unable to open {_fn}")
    return None


def write_xml(filename, _tree):
    """
    Write a XML file
    :param filename: Name of xml to be written
    :param _tree: New contents of the file as a xml tree
    :returns: N/A
    """
    _fn = Path(filename)
    try:
        with _fn.open("wb") as xml_file:
            ET.indent(_tree, "\t")
            _tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        print(f"Unable to write to {_fn}")


def write_xml_from_dict(filename, _dict):
    """
    Write a XML file
    :param filename: Name of xml to be written
    :param _dict: New contents of the file
    :returns: N/A
    """
    _fn = Path(filename)
    try:
        with _fn.open("w") as xml_file:
            xml_content = xmltodict.unparse(_dict, pretty=True)
            xml_file.write(xml_content)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        print(f"Unable to write to {_fn}")


def json_to_et(json_content):
    """
    Convert a json string into a ET.ElementTree
    :param json_content: String: the json content
    :return: xml.etree.ElementTree
    """
    # convert via a dictionary
    _dict = json.loads(json_content)
    xml_content = xmltodict.unparse(_dict, pretty=True)
    return ET.ElementTree(ET.fromstring(xml_content))


def read_json(filename):
    """
    Reads a json file
    :param filename: Name of xml to be read
    :returns: A dictionary of the contents of the file
    """
    _fn = Path(filename)
    if _fn.exists():
        try:
            with _fn.open("r") as json_file:
                _dict = json.load(json_file)
                return _dict
        except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
            print(f"Unable to open {_fn}")
    return None


def write_json(filename, _dict):
    """
    Write a json file
    :param filename: Name of json to be written
    :param _dict: New contents of the file
    :returns: N/A
    """
    _fn = Path(filename)
    try:
        with _fn.open("w") as json_file:
            json.dump(_dict, json_file)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        print(f"Unable to write to {_fn}")


# # Why don't these work ?
# def dump_class_to_text(filename, _class):
#     with open(filename, "a") as f_out:
#         pprint(
#             dict(
#                 (name, getattr(_class, name))
#                 for name in dir(_class)
#                 if not name.startswith("__")
#             ),
#             f_out,
#         )
#
# # Why don't these work ?
# def dump_dict_to_text(filename, _dict):
#     with open(filename, "a") as f_out:
#         print(_dict, f_out)
