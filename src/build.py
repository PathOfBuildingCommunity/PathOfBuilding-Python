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
from pathlib import Path

from constants import _VERSION, empty_build, program_title, default_spec, PlayerClasses
from pob_config import _debug, Config
import pob_file
import ui_utils
from tree import Tree
from PoB_Main_Window import Ui_MainWindow


class Build:
    def __init__(self, _config: Config) -> None:
        self.pob_config = _config
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
    def bandit(self):
        return self.build.get("bandit", "None")

    @bandit.setter
    def bandit(self, new_name):
        self.build.set("bandit", new_name)

    @property
    def mainSocketGroup(self):
        return self.build.get("mainSocketGroup")

    @mainSocketGroup.setter
    def mainSocketGroup(self, new_name):
        self.build.set("mainSocketGroup", new_name)

    @property
    def pantheonMajorGod(self):
        return self.build.get("pantheonMajorGod")

    @pantheonMajorGod.setter
    def pantheonMajorGod(self, new_name):
        self.build.set("pantheonMajorGod", new_name)

    @property
    def pantheonMinorGod(self):
        return self.build.get("pantheonMinorGod")

    @pantheonMinorGod.setter
    def pantheonMinorGod(self, new_name):
        self.build.set("pantheonMinorGod", new_name)

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
        self.build.set("viewMode", curr_tab.upper)

    @property
    def current_spec(self):
        """
        Manage the currently chosen spec in the config class so it can be used by many other classes
        :return:
        """
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
            self.specs.append(Spec(spec))
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
            # print(self.build["PlayerStat"][:])
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
        # pob["PathOfBuilding"]["Notes"] = self.notes
        # pob["PathOfBuilding"]["NotesHTML"] = self.notes_html
        # pob["PathOfBuilding"]["TreeView"] = self.tree_view
        # pob["PathOfBuilding"]["Items"] = self.items
        # pob["PathOfBuilding"]["Config"] = self.config
        # pob["PathOfBuilding"]["Tree"] = self.tree
        # pob_file.write_xml_from_dict("builds/test.xml", pob)
        # # pob_file.write_xml_from_dict(self.filename, pob)

        """Debug Please leave until build is mostly complete"""
        # print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.build, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.import_field, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.calcs, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.skills, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.tree, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.notes, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.notes_html, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.tree_view, encoding='utf8').decode('utf8'))
        # print(ET.tostring(self.items, encoding='utf8').decode('utf8'))
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


class Spec:
    def __init__(self, _spec=None) -> None:
        def_spec = ET.fromstring(default_spec)
        if _spec is None:
            _spec = def_spec

        self.title = _spec.get("title", def_spec.get("title"))
        self.classId = PlayerClasses(int(_spec.get("classId", PlayerClasses.SCION)))
        self.ascendClassId = int(_spec.get("ascendClassId", 0))
        self.treeVersion = _spec.get("treeVersion", def_spec.get("treeVersion"))
        self.masteryEffects = _spec.get("masteryEffects", None)

        # ToDo this includes ascendancy nodes (grrr)
        self.nodes = {}
        str_nodes = _spec.get("nodes", "0")
        if str_nodes:
            self.nodes = str_nodes.split(",")

        self.EditedNodes = _spec.find("EditedNodes")
        if self.EditedNodes is None:
            self.EditedNodes = def_spec.find("EditedNodes")
        self.URL = _spec.find("URL")
        if self.URL is None:
            self.URL = def_spec.find("URL")
        self.Sockets = _spec.find("Sockets")
        if self.Sockets is None:
            self.Sockets = def_spec.find("Sockets")
