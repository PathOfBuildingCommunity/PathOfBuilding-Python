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
    empty_build,
    empty_gem,
    empty_socket_group,
    program_title,
    slot_map,
)
from pob_config import _debug, Config, str_to_bool, bool_to_str, print_a_xml_element
import pob_file
import ui_utils
from tree import Tree
from PoB_Main_Window import Ui_MainWindow
from spec import Spec


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
        self.trees = {_VERSION: Tree(self.pob_config)}
        self.current_tree = self.trees.get(_VERSION)
        # list of specs in this build
        self.specs = []
        self.activeSpec = 0

        # variables from the xml
        self.build_xml_tree = None
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
        self.gems_by_name_or_id = None

        self.nodes_assigned, self.ascnodes_assigned, self.sockets_assigned = 0, 0, 0

        """Now fill out everything above out with a new build
           This stops the creation of other classes() erroring out because variables are setup
           So yes, build variables are filled out twice on start up
           Once from here, and the 2nd from MainWindow.init.build_loader("Default")
           """
        self.new(ET.ElementTree(ET.fromstring(empty_build)))

    def __repr__(self) -> str:
        ret_str = f"[BUILD]: '{self.name}'\n"
        ret_str += f"{self.current_tree.version}"
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
    def viewMode(self):
        return self.build.get("viewMode")

    @viewMode.setter
    def viewMode(self, curr_tab):
        self.build.set("viewMode", curr_tab.upper())

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

    def new(self, _build_tree):
        """
        common function to load internal variables from the dictionary

        :param _build_tree: xml tree object from loading the source XML or the default one
        :return: N/A
        """
        self.name = "Default"
        self.build_xml_tree = _build_tree
        self.root = _build_tree.getroot()
        self.build = self.root.find("Build")
        self.import_field = self.root.find("Import")
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
        for spec in self.tree.findall("Spec"):
            if spec.get("title", -1) == -1:
                spec.set("title", "Default")
            self.specs.append(Spec(self, spec))
        # In the xml, activeSpec is 1 based, but python indexes are 0 based, so we subtract 1
        self.activeSpec = int(self.tree.get("activeSpec", 1)) - 1
        self.current_spec = self.specs[self.activeSpec]

    # new

    def load_from_file(self, filename):
        """
        Load a build. Use new() as a common function

        :param filename: str() XML file to load
        :return: N/A
        """
        _build_pob = pob_file.read_xml(filename)
        if _build_pob is None:
            tr = self.pob_config.app.tr
            ui_utils.critical_dialog(
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

    def save(self, win: Ui_MainWindow):
        """
        Save the build to the filename recorded in the build Class
        :return: N/A
        """
        # pob = {"PathOfBuilding": {}}
        # pob["PathOfBuilding"]["Build"] = self.build
        # pob["PathOfBuilding"]["Import"] = self.import_field
        # pob["PathOfBuilding"]["Calcs"] = self.calcs
        # pob["PathOfBuilding"]["Skills"] = self.skills
        self.notes.text, self.notes_html.text = win.notes_ui.save()
        win.stats.save(self.build)
        win.skills_ui.save()
        win.items_ui.save()
        win.config_ui.save()
        # pob["PathOfBuilding"]["TreeView"] = self.tree_view
        # pob["PathOfBuilding"]["Items"] = self.items
        # pob["PathOfBuilding"]["Tree"] = self.tree
        for spec in self.specs:
            spec.save()
        # pob_file.write_xml_from_dict("builds/test.xml", pob)
        # # pob_file.write_xml_from_dict(self.filename, pob)

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

        # Temporarily write to a test file to not corrupt the original and make for easy compare
        pob_file.write_xml("builds/test.xml", self.build_xml_tree)
        # pob_file.write_xml(self.filename, self.build_xml_tree)

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
            node = self.current_tree.nodes.get(str(node_id), None)
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
        Process changing a tree inside a build

        :param tree_id: index into self.specs which comesfrom the data of combo_ManageTree
        :return: N/A
        """
        if tree_id is None:
            return
        self.activeSpec = tree_id
        self.current_spec = self.specs[tree_id]
        self.count_allocated_nodes()

    def move_spec(self, start, destination):
        """
        Move a spec entry. This is called by the manage tree dialog.

        :param start: int: the index of the spec to be moved
        :param destination: the index where to insert the moved spec
        :return:
        """
        spec = self.specs[start]
        xml_spec = spec.xml_spec
        print(type(xml_spec), xml_spec)
        if start < destination:
            # need to decrement dest by one as we are going to remove start first
            destination -= 1
        self.specs.remove(spec)
        self.specs.insert(destination, spec)
        self.tree.remove(xml_spec)
        self.tree.insert(destination, xml_spec)

    def new_spec(self, new_title):
        """
        Add a new empty tree/Spec

        :param new_title: str
        :return: Spec(): the newly created Spec()
        """
        # print("build.new_spec")
        spec = Spec(self.build, None)
        spec.title = new_title
        self.specs.append(spec)
        self.tree.append(spec.xml_spec)
        return spec

    def import_passive_tree_jewels_json(self, json_tree, json_character):
        """
        Import the tree (and later the jewels)

        :param json_tree: json import of tree and jewel data
        :param json_character: json import of the character information
        :return: N/A
            character={ ascendancyClass=1, class="Inquisitor", classId=5, experience=1028062232,
                league="Standard", level=82, name="Mirabel__Sentinel" },
        """
        # print(json_character)
        # print(json_tree)
        new_spec = Spec(self)
        self.specs.append(new_spec)
        new_spec.title = f"Imported {json_character.get('name', '')}"
        self.name = new_spec.title
        new_spec.classId = json_character.get("classId", 0)
        self.current_class = new_spec.classId
        new_spec.ascendancyClass = json_character.get("ascendancyClass", 0)
        self.ascendClassName = json_character.get("class", "")
        self.level = json_character.get("level", 1)

        # show tree
        self.win.tree_ui.combo_manage_tree.setCurrentIndex(int(self.tree.get("activeSpec", 1)) - 1)

    def check_socket_group_for_an_active_gem(self, _sg):
        """
        Check a socket group and if the first gem is not active gem, find an active gem in the group
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

    def import_gems_json(self, json_items):
        """
        Import skills from the json supplied by GGG.

        :param json_items: json import of the item data.
        :return: N/A
        """

        def get_property(_json_gem, _name, _default):
            """
            Get a property from a list of property tags. Not all properties appear mandatory.

            :param _json_gem: the gem reference from the json download
            :param _name: the name of the property
            :param _default: a default value to be used if the property is not listed
            :return:
            """
            for _prop in _json_gem.get("properties"):
                if _prop.get("name") == _name:
                    value = _prop.get("values")[0][0].replace(" (Max)", "").replace("+", "").replace("%", "")
                    return value
            return _default

        if len(json_items["items"]) <= 0:
            return
        json_character = json_items.get("character")
        # Make a new skill set
        skill_set = ET.fromstring(
            f'<SkillSet id="{len(self.skills)}" title="Imported {json_character.get("name", "")}" />'
        )
        self.skills.append(skill_set)

        # loop through all items and look for gems in socketedItems
        for item in json_items["items"]:
            if item.get("socketedItems", None) is not None:
                # setup tracking of socket group changes in one item
                current_socket_group = None
                current_socket_group_number = -1
                # ToDo: Checkout the 'sockets': attribute for how the sockets are grouped (group attr)
                for idx, json_gem in enumerate(item.get("socketedItems")):
                    # let's get the group # for this socket ...
                    this_group = item["sockets"][idx]["group"]
                    # ... so we can make a new one if needed
                    if this_group != current_socket_group_number:
                        self.check_socket_group_for_an_active_gem(current_socket_group)
                        current_socket_group_number = this_group
                        current_socket_group = ET.fromstring(empty_socket_group)
                        current_socket_group.set("slot", slot_map[item["inventoryId"]])
                        skill_set.append(current_socket_group)
                    xml_gem = ET.fromstring(empty_gem)
                    current_socket_group.append(xml_gem)
                    xml_gem.set("level", get_property(json_gem, "Level", "1"))
                    xml_gem.set("quality", get_property(json_gem, "Quality", "0"))

                    _name = json_gem["baseType"].replace(" Support", "")
                    xml_gem.set("nameSpec", _name)
                    xml_gem.set("skillId", self.gems_by_name_or_id[_name]["skillId"])

                    base_item = self.gems_by_name_or_id[_name]["base_item"]
                    xml_gem.set("gemId", base_item.get("id"))

                    match json_gem["typeLine"]:
                        case "Anomalous":
                            xml_gem.set("qualityId", "Alternate1")
                        case "Divergent":
                            xml_gem.set("qualityId", "Alternate2")
                        case "Phantasmal":
                            xml_gem.set("qualityId", "Alternate3")
                self.check_socket_group_for_an_active_gem(current_socket_group)

    def import_items_json(self, json_items):
        """
        Import items

        :param json_items: json import of the item data
        :return: N/A
        """
