"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

import xml.etree.ElementTree as ET
from pprint import pprint
from pathlib import Path
from typing import Union

from constants import (
    PlayerClasses,
    _VERSION,
    _VERSION_str,
    bandits,
    empty_build,
    empty_gem,
    empty_socket_group,
    program_title,
    slot_map,
)
from pob_config import (
    _debug,
    Config,
    str_to_bool,
    bool_to_str,
    print_a_xml_element,
    print_call_stack,
)
import pob_file
import dialogs.popup_dialogs as popup_dialogs
from tree import Tree
from views.PoB_Main_Window import Ui_MainWindow
from spec import Spec
from ui_utils import set_combo_index_by_data


class Build:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self._name = "Default"
        # self.player = player.Player()
        self.filename = ""
        self.search_text = ""
        self.need_saving = True
        self.current_tab = "TREE"
        # Load the default tree into the array
        self.trees = {_VERSION_str: Tree(self.pob_config, _VERSION_str)}
        self.current_tree = self.trees.get(_VERSION_str)
        # list of specs in this build
        self.specs = []
        self.activeSpec = 0
        self._current_spec = None
        self.compare_spec = None

        # variables from the xml
        self.xml_build = None
        self.root = None
        self.build = None
        self.import_field = None
        self.calcs = None
        self.skills = None
        self.tree = None
        self.notes = None
        self.notes_html = None
        self.tree_view = None
        self.items = None
        self.config = None
        self.last_account_hash = ""
        self.last_character_hash = ""
        self.last_realm = ""
        self.last_league = ""

        self.gems_by_name_or_id = None
        self.nodes_assigned, self.ascnodes_assigned, self.sockets_assigned = 0, 0, 0

        """Now fill out everything above out with a new build
           This stops the creation of other classes() erroring out because variables are setup
           So yes, build variables are filled out twice on start up
           Once from here, and the 2nd from MainWindow.init.build_loader("Default")
           """
        self.new(ET.ElementTree(ET.fromstring(empty_build)))

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
        self.pob_config.win.setWindowTitle(f"{program_title} - {new_name}")

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
        return self.build.get("className")

    @className.setter
    def className(self, new_name):
        self.build.set("className", new_name)

    @property
    def ascendClassName(self):
        return self.build.get("ascendClassName")

    @ascendClassName.setter
    def ascendClassName(self, new_name):
        self.build.set("ascendClassName", new_name)

    @property
    def level(self):
        return int(self.build.get("level"))

    @level.setter
    def level(self, new_level):
        self.build.set("level", f"{new_level}")
        self.win.spin_level.setValue(new_level)

    @property
    def mainSocketGroup(self):
        # Use a property to ensure the correct +/- 1
        return max(int(self.build.get("mainSocketGroup", 1)) - 1, 0)

    @mainSocketGroup.setter
    def mainSocketGroup(self, new_group):
        # Use a property to ensure the correct +/- 1
        self.build.set("mainSocketGroup", f"{new_group + 1}")

    @property
    def resistancePenalty(self):
        return self.get_config_tag_item("Input", "resistancePenalty", "number", 0)

    @resistancePenalty.setter
    def resistancePenalty(self, new_name):
        self.set_config_tag_item("Input", "resistancePenalty", "number", new_name)

    @property
    def bandit(self):
        return self.get_config_tag_item("Input", "bandit", "string", "None")

    @bandit.setter
    def bandit(self, new_name):
        self.build.set("bandit", new_name)
        self.set_config_tag_item("Input", "bandit", "string", new_name)
        set_combo_index_by_data(self.win.combo_Bandits, self.bandit)

    def set_bandit_by_number(self, new_int):
        """Use a number to set the bandit name. Used by import from poeplanner mainly"""
        self.bandit = list(bandits.keys())[new_int]

    @property
    def pantheonMajorGod(self):
        return self.get_config_tag_item("Input", "pantheonMajorGod", "string", "None")

    @pantheonMajorGod.setter
    def pantheonMajorGod(self, new_name):
        self.build.set("pantheonMajorGod", new_name)
        self.set_config_tag_item("Input", "pantheonMajorGod", "string", new_name)

    @property
    def pantheonMinorGod(self):
        return self.get_config_tag_item("Input", "pantheonMinorGod", "string", "None")

    @pantheonMinorGod.setter
    def pantheonMinorGod(self, new_name):
        self.build.set("pantheonMinorGod", new_name)
        self.set_config_tag_item("Input", "pantheonMinorGod", "string", new_name)

    @property
    def targetVersion(self):
        return self.build.get("targetVersion")

    @targetVersion.setter
    def targetVersion(self, new_name):
        self.build.set("targetVersion", new_name)

    @property
    def version(self):
        return int(self.build.get("version", "2"))

    @version.setter
    def version(self, curr_ver):
        self.build.set("version", str(curr_ver))

    @property
    def viewMode(self):
        return self.build.get("viewMode")

    @viewMode.setter
    def viewMode(self, curr_mode):
        self.build.set("viewMode", curr_mode.upper())

    @property
    def current_spec(self):
        """Manage the currently chosen spec in the config class so it can be used by many other classes"""
        return self._current_spec

    @current_spec.setter
    def current_spec(self, new_spec):
        self._current_spec = new_spec

    # @property
    # def (self):
    #     return self.build[""]

    # @.setter
    # def (self, new_name):
    #     self.build[""] = new_name

    def get_config_tag_item(self, key, name, value_type, default=Union[str, int, bool]):
        """
        Get an item from the <Config> ... </Config> tag set

        :param key: string: the key: Input or Placeholder for example
        :param name: string: the value of the 'name' property
        :param value_type: string: just to be confusing, the name of the 'value' property (string, boolean, number)
        :param default: Union[str, int, bool]): a default value in case the item is not in the xml
        :return: The appropriate value from xml or the default
        """
        for _input in self.config.findall(key):
            if _input.get("name") == name:
                _value = _input.get(value_type, default)
                match value_type:
                    case "string":
                        return _value
                    case "boolean":
                        return str_to_bool(_value)
                    case "number":
                        return int(_value)
        return None

    def set_config_tag_item(self, key, name, value_type, new_value=Union[str, int, bool]):
        """
        Get an item from the <Config> ... </Config> tag set

        :param key: string: the key: Input or Placeholder for example
        :param name: string: the value of the 'name' property
        :param value_type: string: just to be confusing, the name of the 'value' property (string, boolean, number)
        :param new_value: Union[str, int, bool]): the value to be recorded
        :return: The appropriate value from xml or "default"
        """
        for _input in self.config.findall(key):
            if _input.get("name") == name:
                match value_type:
                    case "boolean":
                        new_value = bool_to_str(new_value)
                    case "number":
                        new_value = f"{new_value}"
                return _input.set(value_type, new_value)
        # if we get here, the key/ name combo was not found, lets make one and add it
        self.config.append(ET.fromstring(f'<{key} name="{name}" {value_type}="{new_value}" />'))

    def new(self, _xml):
        """
        common function to load internal variables from the dictionary

        :param _xml: xml tree object from loading the source XML or the default one
        :return: N/A
        """
        self.name = "Default"
        self.xml_build = _xml
        self.root = _xml.getroot()
        self.build = self.root.find("Build")
        self.import_field = self.root.find("Import")
        if self.import_field is not None:
            self.last_account_hash = self.import_field.get("lastAccountHash", "")
            self.last_character_hash = self.import_field.get("lastCharacterHash", "")
            self.last_realm = self.import_field.get("lastRealm", "")
            self.last_league = self.import_field.get("lastLeague", "")
        self.calcs = self.root.find("Calcs")
        self.skills = self.root.find("Skills")
        self.tree = self.root.find("Tree")
        self.notes = self.root.find("Notes")
        self.notes_html = self.root.find("NotesHTML")
        # lua version doesn't have NotesHTML, expect it to be missing
        if self.notes_html is None:
            self.notes_html = ET.Element("NotesHTML")
            self.root.append(self.notes_html)
        self.tree_view = self.root.find("TreeView")
        self.items = self.root.find("Items")
        self.config = self.root.find("Config")

        self.specs.clear()
        # Do not use self.new_spec() as this will duplicate the xml information
        for xml_spec in self.tree.findall("Spec"):
            self.specs.append(Spec(self, xml_spec))
        self.current_spec = self.specs[0]

        # In the xml, activeSpec is 1 based, but python indexes are 0 based, so we subtract 1
        self.activeSpec = int(self.tree.get("activeSpec", 1)) - 1
        self.current_spec = self.specs[self.activeSpec]
        # new

    def save_to_xml(self, version=2):
        """
        Save the build to the filename recorded in the build Class
        :param:version: int. 1 for version 1 xml data,  2 for updated.
        :return: N/A
        """
        self.import_field.set("lastAccountHash", self.last_account_hash)
        self.import_field.set("lastCharacterHash", self.last_character_hash)
        self.import_field.set("lastRealm", self.last_realm)
        self.import_field.set("lastLeague", self.last_league)
        self.notes.text, self.notes_html.text = self.win.notes_ui.save(version)
        self.win.stats.save(self.build)
        self.win.skills_ui.save()
        self.win.items_ui.save(version)
        self.win.config_ui.save()
        for spec in self.specs:
            spec.save()

        """Debug Please leave until build is mostly complete"""
        # print("build")
        # print(ET.tostring(self.build, encoding='utf8'))  # .decode('utf8'))
        # print("import_field")
        # print(ET.tostring(self.import_field, encoding='utf8').decode('utf8'))
        # print("calcs")
        # print(ET.tostring(self.calcs, encoding='utf8').decode('utf8'))
        # print("skills")
        # print(ET.tostring(self.skills, encoding='utf8').decode('utf8'))
        # print("tree")
        # print(ET.tostring(self.tree, encoding='utf8').decode('utf8'))
        # print("notes")
        # print(ET.tostring(self.notes, encoding='utf8').decode('utf8'))
        # print("notes_html")
        # print(ET.tostring(self.notes_html, encoding='utf8').decode('utf8'))
        # print("tree_view")
        # print(ET.tostring(self.tree_view, encoding='utf8').decode('utf8'))
        # print("items")
        # print(ET.tostring(self.items, encoding='utf8').decode('utf8'))
        # print("config")
        # print(ET.tostring(self.config, encoding='utf8').decode('utf8'))
        """Debug Please leave until build is mostly complete"""

    def save_build_to_file(self, filename):
        """
        Save the build to file. Separated from the save routine above so export can use the above save routine.

        :param filename:
        :return:
        """
        # Temporarily write to a test file to not corrupt the original and make for easy compare
        pob_file.write_xml(filename, self.xml_build)
        # pob_file.write_xml(self.filename, self.xml_build)

    def save_as(self, filename):
        """
        Save the build to a new name

        :param filename:
        :return: N/A
        """
        self.filename = filename
        self.save()

    def ask_for_save_if_modified(self):
        """
        Check if the build has been modified and if so, prompt for saving.

        :return: True if build saved
        :return: False if build save was refused by the user
        """
        return True

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
            self.trees[new_spec.treeVersion] = Tree(self.pob_config, new_spec.treeVersion)
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
            # need to decrement dest by one as we are going to remove start first
            destination -= 1
        self.specs.remove(spec)
        self.specs.insert(destination, spec)
        self.tree.remove(xml_spec)
        self.tree.insert(destination, xml_spec)

    def new_spec(self, new_title="", version=_VERSION_str, xml_spec=None, destination=-1):
        """
        Add a new empty tree/Spec

        :param new_title: str
        :param version: float: the version number of this spec. Default to the default Tree version
        :param xml_spec: ET.elementtree: If specified, the new x,l representation
        :param destination: int: If specified, insert the new spec at destination elsewise append to the end
        :return: Spec(): the newly created Spec()
        """
        # print("build.new_spec")
        spec = Spec(self, xml_spec, version)
        if new_title != "":
            spec.title = new_title
        if destination == -1:
            self.specs.append(spec)
            self.tree.append(spec.xml_spec)
        else:
            self.specs.insert(destination, spec)
            self.tree.insert(destination, spec.xml_spec)
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
                self.tree.remove(xml_spec)
                del self.specs[count]
        elif 0 < index < len(self.specs):
            xml_spec = self.specs[index].xml_spec
            self.tree.remove(xml_spec)
            del self.specs[index]

    """
    ################################################### IMPORT ###################################################
    """

    def load_from_file(self, filename):
        """
        Load a build. Use new() as a common function

        :param filename: str() XML file to load
        :return: N/A
        """
        _build_pob = pob_file.read_xml(filename)
        if _build_pob is None:
            tr = self.pob_config.app.tr
            popup_dialogs.critical_dialog(
                self.pob_config.win,
                tr("Load Build"),
                f"{tr('An error occurred to trying load')}:\n{filename}",
                tr("Close"),
            )
        else:
            # How do we want to deal with corrupt builds
            self.filename = filename
            self.new(_build_pob)
            self.name = Path(Path(filename).name).stem

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
