"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

import builtins
import re
import xml.etree.ElementTree as ET
from pprint import pprint
from pathlib import Path, WindowsPath
from typing import Union

from PoB.constants import (
    PlayerClasses,
    _VERSION,
    _VERSION_str,
    bandits,
    empty_build,
    empty_build_xml,
    empty_gem,
    empty_socket_group,
    program_title,
    tree_versions,
)
from PoB.settings import Settings
from PoB.tree import Tree
from PoB.spec import Spec
from PoB.pob_file import read_v1_custom_mods, read_json, read_xml, write_xml
from dialogs.popup_dialogs import critical_dialog, yes_no_dialog
from widgets.ui_utils import (
    _debug,
    is_str_a_boolean,
    is_str_a_number,
    str_to_bool,
    bool_to_str,
    print_a_xml_element,
    print_call_stack,
    set_combo_index_by_data,
)

from ui.PoB_Main_Window import Ui_MainWindow


class Build:
    def __init__(self, _settings: Settings, _win: Ui_MainWindow) -> None:
        self.settings = _settings
        self.win = _win
        self.tr = self.settings.app.tr
        self._name = "Default"
        # self.player = player.Player()
        self.filename = ""
        self.search_text = ""
        self.need_saving = True
        # self.current_tab = "TREE"
        # An dict of tree versions used in the build. Load the default tree first.
        self.trees = {_VERSION_str: Tree(self.settings, _VERSION_str)}
        self.current_tree = self.trees.get(_VERSION_str)
        # list of xml specs in this build
        self.specs = []
        self.activeSpec = 0
        self._current_spec = None
        self.compare_spec = None

        # variables from the xml
        self.json = True
        self.xml_PoB = None
        self.xml_root = None
        self.xml_build = None
        self.xml_import_field = None
        self.xml_calcs = None
        self.xml_skills = None
        self.xml_tree = None
        self.xml_notes = None
        self.xml_notes_html = None
        self.xml_tree_view = None
        self.xml_items = None
        self.xml_config = None
        self.last_account_hash = ""
        self.last_character_hash = ""
        self.last_realm = ""
        self.last_league = ""

        self.json_build = None

        self.nodes_assigned = 0
        self.ascnodes_assigned = 0
        self.sockets_assigned = 0

        """Now fill out everything above out with a new build
           This stops the creation of other classes() erroring out because variables are setup
           So yes, build variables are filled out twice on start up
           Once from here, and the 2nd from MainWindow.init.build_loader("Default")
           """
        self.new(ET.ElementTree(ET.fromstring(empty_build_xml)))

    def __repr__(self) -> str:
        ret_str = f"[BUILD]: '{self.name}', {self.current_tree.version}"
        # ret_str += f"{self.player}"
        return ret_str

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self.win.setWindowTitle(f"{program_title} - {new_name}")
        if new_name != "Default" and (self.filename == "" or self.filename == "Default"):
            self.filename = new_name

    @property
    def current_class(self):
        return self.current_spec.classId

    @current_class.setter
    def current_class(self, new_class):
        """
        Actions required for changing classes

        :param new_class: Integer representing the PlayerClasses enumerations
        :return:
        """
        self.current_spec.classId = new_class
        self.className = PlayerClasses(new_class).name.title()

    @property
    def className(self):
        return self.xml_build.get("className", "Scion")

    @className.setter
    def className(self, new_name):
        self.xml_build.set("className", new_name)

    @property
    def ascendClassName(self):
        return self.xml_build.get("ascendClassName", "None")

    @ascendClassName.setter
    def ascendClassName(self, new_name):
        self.xml_build.set("ascendClassName", new_name)

    @property
    def level(self):
        return int(self.xml_build.get("level"))

    @level.setter
    def level(self, new_level):
        self.xml_build.set("level", f"{new_level}")
        self.win.spin_level.setValue(new_level)

    @property
    def mainSocketGroup(self):
        # Use a property to ensure the correct +/- 1
        return max(int(self.xml_build.get("mainSocketGroup", 1)) - 1, 0)

    @mainSocketGroup.setter
    def mainSocketGroup(self, new_group):
        # Use a property to ensure the correct +/- 1
        self.xml_build.set("mainSocketGroup", f"{new_group + 1}")

    @property
    def resistancePenalty(self):
        return self.get_config_tag_item("Input", "resistancePenalty", -60)

    @resistancePenalty.setter
    def resistancePenalty(self, new_value):
        self.set_config_tag_item("Input", "resistancePenalty", new_value)

    @property
    def bandit(self):
        return self.get_config_tag_item("Input", "bandit", "None")

    @bandit.setter
    def bandit(self, new_bandit):
        self.xml_build.set("bandit", new_bandit)
        self.set_config_tag_item("Input", "bandit", new_bandit)
        set_combo_index_by_data(self.win.combo_Bandits, self.bandit)

    def set_bandit_by_number(self, new_int):
        """Use a number to set the bandit name. Used by import from poeplanner mainly"""
        self.bandit = list(bandits.keys())[new_int]

    @property
    def pantheonMajorGod(self):
        return self.get_config_tag_item("Input", "pantheonMajorGod", "None")

    @pantheonMajorGod.setter
    def pantheonMajorGod(self, new_name):
        self.xml_build.set("pantheonMajorGod", new_name)
        self.set_config_tag_item("Input", "pantheonMajorGod", new_name)

    @property
    def pantheonMinorGod(self):
        return self.get_config_tag_item("Input", "pantheonMinorGod", "None")

    @pantheonMinorGod.setter
    def pantheonMinorGod(self, new_name):
        self.xml_build.set("pantheonMinorGod", new_name)
        self.set_config_tag_item("Input", "pantheonMinorGod", new_name)

    @property
    def targetVersion(self):
        return self.xml_build.get("targetVersion")

    @targetVersion.setter
    def targetVersion(self, new_name):
        self.xml_build.set("targetVersion", new_name)

    @property
    def version_int(self):
        return int(self.xml_build.get("version", "1"))

    @property
    def version(self):
        return self.xml_build.get("version", "1")

    @version.setter
    def version(self, curr_ver):
        self.xml_build.set("version", curr_ver)

    @property
    def viewMode(self):
        return self.xml_build.get("viewMode")

    @viewMode.setter
    def viewMode(self, curr_mode):
        self.xml_build.set("viewMode", curr_mode.upper())

    @property
    def current_spec(self):
        """Manage the currently chosen spec in the config class so it can be used by many other classes"""
        return self._current_spec

    @current_spec.setter
    def current_spec(self, new_spec):
        self._current_spec = new_spec

    # @property
    # def (self):
    #     return self.xml_build[""]

    # @.setter
    # def (self, new_name):
    #     self.xml_build[""] = new_name

    def get_config_tag_item(self, key, name, default=Union[str, int, float, bool]):
        """
        Get an item from the <Config> ... </Config> tag set

        :param key: string: the key: Input or Placeholder for example
        :param name: string: the value of the 'name' property
        :param default: Union[str, int, bool]): a default value in case the item is not in the xml
        :return: The appropriate value from xml or the default
        """
        _input = [element for element in self.xml_config.findall(key) if element.get("name") == name]
        if _input:
            _input = _input[0]
            # Find out what kind of value we have. Assume that XML might have: name="x" number="1" or: number="1" name="x"
            key = [key for key in _input.keys() if key in ("string", "boolean", "number")]
            if key:
                match key[0]:
                    case "string":
                        return _input.get("string")
                    case "boolean":
                        return str_to_bool(_input.get("boolean"))
                    case "number":
                        _value = _input.get("number")
                        # is this an int or simple float (1.2) ?
                        if is_str_a_number(_value):
                            return int(_input.get("number", f"{default}"))
                        elif is_str_a_number(_value.replace(".", "")):
                            return float(_input.get("number", f"{default}"))
                        else:
                            print(f"get_config_tag_item: Can't determine if this is a number, returning default: {key}/{name}, {_value}")
                            return default
            else:
                return default
        else:
            return default

        # for _input in self.config.findall(key):
        #     if _input.get("name") == name:
        #         # Find out what kind of value we have. Assume that XML might have name="x" number="1" or number="1" name="x"
        #         keys = _input.keys()[:]
        #         keys.remove("name")
        #         match keys[0]:
        #             case "string":
        #                 return _input.get("string", f"{default}")
        #             case "boolean":
        #                 return str_to_bool(_input.get("boolean", f"{default}"))
        #             case "number":
        #                 _value = _input.get("number", f"{default}")
        #                 # is this an int or simple float (1.2) ?
        #                 if is_str_a_number(_value):
        #                     return int(_input.get("number", f"{default}"))
        #                 elif is_str_a_number(_value.replace(".", "")):
        #                     return float(_input.get("number", f"{default}"))
        #                 else:
        #                     print(f"get_config_tag_item: Can't determine if this is a number, returning default: {key}/{name}, {_value}")
        #                     return default
        # return default

    def set_config_tag_item(self, key, name, new_value=Union[builtins.str, int, float, bool]):
        """
        Set an item from the <Config> ... </Config> tag set

        :param key: string: the key: Input or Placeholder for example
        :param name: string: the value of the 'name' property
        :param new_value: Union[str, int, bool]): the value to be recorded
        :return: The appropriate value from xml or "default"
        """
        # find element name for output
        match new_value:
            # bool() must come before int
            case bool():
                value_type = "boolean"
            case int() | float():
                value_type = "number"
            case _:
                value_type = "string"
        # Find an existing entry
        _input = [element for element in self.xml_config.findall(key) if element.get("name") == name]
        # print(f"set_config_tag_item, {key=}, {name=}, {new_value=}, {value_type=}, {type(new_value), {_input}}")
        if _input:
            _input[0].set(value_type, f"{new_value}")
        else:
            # The key / name combo was not found, lets make one and add it.
            self.xml_config.append(ET.fromstring(f'<{key} name="{name}" {value_type}="{new_value}" />'))

    def delete_config_tag_item(self, key, name):
        """
        Delete an item from the <Config> ... </Config> tag set
        :param key: string: the key: Input or Placeholder for example
        :param name: string: the value of the 'name' property
        :return: The appropriate value from xml or "default"
        """
        # Find an existing entry
        _input = [element for element in self.xml_config.findall(key) if element.get("name") == name]
        if _input:
            del _input[0]

    def delete_config_all_tag_item(self, key):
        """
        Delete an item from the <Config> ... </Config> tag set
        :param key: string: the key: Input or Placeholder for example
        :return: The appropriate value from xml or "default"
        """
        # Find an existing entry
        for _input in self.xml_config.findall(key):
            del _input

    def new(self, _xml):
        """
        common function to load internal variables from the ET

        :param _xml: xml tree object from loading the source XML or the default one
        :return: N/A
        """

        if self.json:
            self.json_build = empty_build
        else:
            self.name = "Default"
            self.xml_PoB = _xml
            self.xml_root = _xml.getroot()
            self.xml_build = self.xml_root.find("Build")
            self.xml_import_field = self.xml_root.find("Import")
            if self.xml_import_field is not None:
                self.last_account_hash = self.xml_import_field.get("lastAccountHash", "")
                self.last_character_hash = self.xml_import_field.get("lastCharacterHash", "")
                self.last_realm = self.xml_import_field.get("lastRealm", "")
                self.last_league = self.xml_import_field.get("lastLeague", "")
            self.xml_calcs = self.xml_root.find("Calcs")
            self.xml_skills = self.xml_root.find("Skills")
            self.xml_tree = self.xml_root.find("Tree")
            self.xml_notes = self.xml_root.find("Notes")
            self.xml_notes_html = self.xml_root.find("NotesHTML")
            # lua version doesn't have NotesHTML, expect it to be missing
            if self.xml_notes_html is None:
                self.xml_notes_html = ET.Element("NotesHTML")
                self.xml_root.append(self.xml_notes_html)
            self.xml_tree_view = self.xml_root.find("TreeView")
            self.xml_items = self.xml_root.find("Items")
            self.xml_config = self.xml_root.find("Config")
            # print("build.new", print_a_xml_element(self.config))

            self.specs.clear()
            # Find invalid trees, alert and convert to latest
            invalid_spec_versions = set()
            for xml_spec in self.xml_tree.findall("Spec"):
                vers = xml_spec.get("treeVersion", _VERSION_str)
                if vers not in tree_versions.keys():
                    v = re.sub("_", ".", vers)
                    invalid_spec_versions.add(v)
                    xml_spec.set("treeVersion", _VERSION_str)
                    title = xml_spec.get("title", "Default")
                    xml_spec.set("title", f"{title} ({self.tr('was')} v{v})")
            if invalid_spec_versions:
                critical_dialog(
                    self.win,
                    f"{self.tr('Load build')}: v{self.version}",
                    f"{self.tr('The build contains the following unsupported Tree versions')}:\n"
                    f"{str(invalid_spec_versions)[1:-1]}\n\n"
                    + self.tr(f"These will be converted to {_VERSION} and renamed to indicate this.\n"),
                    self.tr("Close"),
                )

            # Do not use self.new_spec() as this will duplicate the xml information
            for xml_spec in self.xml_tree.findall("Spec"):
                self.specs.append(Spec(self, xml_spec))
            self.current_spec = self.specs[0]

            # In the xml, activeSpec is 1 based, but python indexes are 0 based, so we subtract 1
            self.activeSpec = int(self.xml_tree.get("activeSpec", 1)) - 1
            self.current_spec = self.specs[self.activeSpec]
            self.className = self.current_spec.classId_str()
            self.ascendClassName = self.current_spec.ascendClassId_str()
        # new

    def load_from_file(self, filename):
        """
        Load a build. Use new() as a common function.

        :param filename: str: XML file to load.
        :return: N/A
        """
        if type(filename) is Path or type(filename) is WindowsPath:
            filename = filename.name
        self.json = "json" in filename

        if self.json:
            self.json_build = read_json(filename)
            self.new(self.json_build)
        else:
            _build_pob = read_xml(filename)
            if _build_pob is None:
                # How do we want to deal with corrupt builds
                critical_dialog(
                    self.win,
                    self.tr("Load Build"),
                    f"{self.tr('An error occurred to trying load')}:\n{filename}",
                    self.tr("Close"),
                )
            self.new(_build_pob)
        # else:
        self.filename = filename
        self.name = Path(Path(filename).name).stem
        if self.version_int == 1:
            # Custom Mods has newlines in it, but python XML turns them into a space.
            custom_mods = read_v1_custom_mods(filename)
            if custom_mods:
                # add in a str of custom mods
                self.set_config_tag_item("Input", "customMods", custom_mods)

    def save_to_xml(self, version="2"):
        """
        Save the build to the filename recorded in the build Class
        :param:version: str. 1 for version 1 xml data,  2 for updated.
        :return: N/A
        """
        self.version = version
        self.xml_import_field.set("lastAccountHash", self.last_account_hash)
        self.xml_import_field.set("lastCharacterHash", self.last_character_hash)
        self.xml_import_field.set("lastRealm", self.last_realm)
        self.xml_import_field.set("lastLeague", self.last_league)
        for spec in self.specs:
            spec.save()
        # ensure these get updated to match last tree shown.
        self.className = self.current_spec.classId_str()
        self.ascendClassName = self.current_spec.ascendClassId_str()

        """Debug Please leave until build is mostly complete"""
        # print("build")
        # print(ET.tostring(self.xml_build, encoding='utf8'))  # .decode('utf8'))
        # print("import_field")
        # print(ET.tostring(self.xml_import_field, encoding='utf8').decode('utf8'))
        # print("calcs")
        # print(ET.tostring(self.xml_calcs, encoding='utf8').decode('utf8'))
        # print("skills")
        # print(ET.tostring(self.xml_skills, encoding='utf8').decode('utf8'))
        # print("tree")
        # print(ET.tostring(self.xml_tree, encoding='utf8').decode('utf8'))
        # print("notes")
        # print(ET.tostring(self.xml_notes, encoding='utf8').decode('utf8'))
        # print("notes_html")
        # print(ET.tostring(self.xml_notes_html, encoding='utf8').decode('utf8'))
        # print("tree_view")
        # print(ET.tostring(self.xml_tree_view, encoding='utf8').decode('utf8'))
        # print("items")
        # print(ET.tostring(self.xml_items, encoding='utf8').decode('utf8'))
        # print("config")
        # print(ET.tostring(self.xml_config, encoding='utf8').decode('utf8'))
        """Debug Please leave until build is mostly complete"""

    def save_build_to_file(self, filename):
        """
        Save the build to file. Separated from the save routine above so export can use the above save routine.

        :param filename:
        :return:
        """
        write_xml(filename, self.xml_PoB)
        self.name = Path(Path(filename).name).stem

    def ask_for_save_if_modified(self):
        """
        Check if the build has been modified and if so, prompt for saving.

        :return: True if build saved
        :return: False if build save was refused by the user
        """
        return True

    def assign_items_to_sockets(self, xml_items):
        """

        :param xml_items: the list of items
        :return:
        """
        for node_id in self.current_spec.sockets.keys():
            item_id = self.current_spec.sockets[node_id]

    def count_allocated_nodes(self):
        """
        Loop through the current tree's active nodes and split the normal and ascendancy nodes.

        :return: N/A
        """
        self.nodes_assigned, self.ascnodes_assigned, self.sockets_assigned = 0, 0, 0
        for node_id in self.current_spec.nodes:
            node = self.current_tree.nodes.get(node_id, None)
            if node is not None:
                if node.type != "ClassStart" and not node.isAscendancyStart:
                    if node.ascendancyName == "":
                        self.nodes_assigned += 1
                    else:
                        if not node.isMultipleChoiceOption:
                            self.ascnodes_assigned += 1
                    if node.type == "Socket":
                        self.sockets_assigned += 1

        self.nodes_assigned += len(self.current_spec.extended_hashes)

    def change_tree(self, tree_id):
        """
        Process changing a tree inside a build.

        :param tree_id: int/None: index into self.specs which comes from combo_ManageTree.currentData().
        :return: bool: True if the previous and new trees have different versions.
        """
        if tree_id is None:
            return True
        new_spec = self.specs[tree_id]
        different_version = self.current_spec.treeVersion != new_spec.treeVersion
        # Check if this version is loaded
        if self.trees.get(new_spec.treeVersion, None) is None:
            self.trees[new_spec.treeVersion] = Tree(self.settings, new_spec.treeVersion)
        self.current_tree = self.trees[new_spec.treeVersion]

        self.activeSpec = tree_id
        self.current_spec = new_spec
        self.count_allocated_nodes()
        return different_version

    def check_socket_group_for_an_active_gem(self, _sg):
        """
        Check a socket group and if the first gem is not an active gem, find an active gem in the group
        and if found, set it to be first.

        :param _sg: ET.element: the socket group to check
        :return: N/A
        """
        if _sg is not None:
            for _idx, _gem in enumerate(_sg.findall("Gem")):
                # find the first active gem and move it if it's index is not 0
                if "Support" not in _gem.get("skillId"):
                    if _idx != 0:
                        _sg.remove(_gem)
                        _sg.insert(0, _gem)
                    break

    """
    ################################################### SPECS ###################################################
    """

    def move_spec(self, start, destination):
        """
        Move a spec entry. This is called by the manage tree dialog.

        :param start: int: the index of the spec to be moved
        :param destination: the index where to insert the moved spec
        :return:
        """
        spec = self.specs[start]
        xml_spec = spec.xml_spec
        if start < destination:
            # need to decrement destination by one as we are going to remove start first
            destination -= 1
        self.specs.remove(spec)
        self.specs.insert(destination, spec)
        self.xml_tree.remove(xml_spec)
        self.xml_tree.insert(destination, xml_spec)

    def new_spec(self, new_title="", version=_VERSION_str, xml_spec=None, destination=-1):
        """
        Add a new empty tree/Spec

        :param new_title: str
        :param version: float: the version number of this spec. Default to the default Tree version
        :param xml_spec: ET.elementtree: If specified, the new xml representation
        :param destination: int: If specified, insert the new spec at destination elsewise append to the end
        :return: Spec(): the newly created Spec()
        """
        # print("build.new_spec")
        spec = Spec(self, xml_spec, version)
        spec.classId = self.current_spec.classId
        spec.ascendClassId = self.current_spec.ascendClassId
        if new_title != "":
            spec.title = new_title
        if destination == -1:
            self.specs.append(spec)
            self.xml_tree.append(spec.xml_spec)
        else:
            self.specs.insert(destination, spec)
            self.xml_tree.insert(destination, spec.xml_spec)
        return spec

    def copy_spec(self, source, destination):
        """
        Copy an existing Spec() and xml_spec

        :param source: int: The source index into self.specs and self.tree
        :param destination: int: The destination index into self.specs and self.tree
        :return: Spec(): the newly created Spec()
        """
        # print("build.copy_spec")
        # converting to a string ensures it is copied and not one element that is shared.
        # internet rumour indicates .clone() and .copy() may not be good enough
        new_xml_spec = ET.fromstring(ET.tostring(self.specs[source].xml_spec))
        return self.new_spec(new_title="", xml_spec=new_xml_spec, destination=destination)

    def convert_spec(self, source, destination):
        """
        Convert an existing Spec() and xml_spec to the latest tree version.

        :param source: int: The source index into self.specs and self.tree
        :param destination: int: The destination index into self.specs and self.tree
        :return: Spec(): the newly created Spec(), None if conversion didn't happen
        """
        print("build.convert_spec")
        # Looking at the lua version, convert is just copy, with the tree version set to current.
        # ToDo: should we at least check the nodes are still valid ?
        spec = self.specs[source]
        if spec.treeVersion != _VERSION_str:
            spec = self.copy_spec(source, destination)
            spec.treeVersion = _VERSION_str
            return spec
        else:
            return None

    def delete_spec(self, index):
        """
        Delete a tree/Spec

        :param index: int: The index into self.specs and self.tree
        :return:  N/A
        """
        # print("build.delete_spec")
        if index == "all":
            # Then remove all
            for count in range(len(self.specs)):
                xml_spec = self.specs[0].xml_spec
                self.xml_tree.remove(xml_spec)
                del self.specs[count]
        elif 0 <= index < len(self.specs):
            xml_spec = self.specs[index].xml_spec
            self.xml_tree.remove(xml_spec)
            del self.specs[index]

    """
    ################################################### IMPORT ###################################################
    """

    def import_passive_tree_jewels_ggg_json(self, json_tree, json_character):
        """
        Import the tree (and later the jewels)

        :param json_tree: json import of tree and jewel data
        :param json_character: json import of the character information
        :return: N/A
            character={ ascendancyClass=1, class="Inquisitor", classId=5, experience=1028062232,
                league="Standard", level=82, name="Mirabel__Sentinel" },
        """
        # print("import_passive_tree_jewels_json", json_character)
        # print("import_passive_tree_jewels_json", json_tree)
        new_spec = self.new_spec()
        self.name = f"Imported {json_character.get('name', '')}"
        new_spec.load_from_ggg_json(json_tree, json_character)
        self.current_class = new_spec.classId
        self.ascendClassName = json_character.get("class", "")
        self.level = json_character.get("level", 1)

        # add to combo
        self.win.tree_ui.fill_current_tree_combo()
        # show tree
        self.win.tree_ui.combo_manage_tree.setCurrentIndex(self.win.tree_ui.combo_manage_tree.count() - 1)

    def import_passive_tree_jewels_poep_json(self, json_tree, json_stats):
        """
        Import the tree (and later the jewels)
        :param json_tree: json import of character, tree and jewel data
        :param json_stats: json import of stats
        :return: N/A
        """
        self.delete_spec("all")
        vers = json_tree.get("version", _VERSION_str).split(".")
        new_spec = self.new_spec("Imported from poeplanner", f"{vers[0]}_{vers[1]}")
        new_spec.import_from_poep_json(json_tree)
        self.current_class = new_spec.classId
        self.ascendClassName = json_tree.get("ascendancy", "")
        self.level = json_stats.get("level", 1)

        # add to combo, willl be the only tree there, so it will be shown
        self.win.tree_ui.fill_current_tree_combo()

    def reset_tree(self):
        """
        Actions for the build for resetting the tree.
        :return:
        """
        self.current_spec.nodes.clear()
        start_node = self.current_tree.classes[self.current_class]["startNodeId"]
        self.current_spec.nodes.add(start_node)
        # self.current_spec.nodes = [start_node]
        self.win.gview_Tree.add_tree_images(True)
