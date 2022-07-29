"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

import re
from pathlib import Path

from pob_config import *
from pob_config import _VERSION
import pob_file
import ui_utils
from tree import Tree
from PoB_Main_Window import Ui_MainWindow


class Build:
    def __init__(self, _config: Config) -> None:
        self.pob_config = _config
        self._name = "Default"
        self.ui: Ui_MainWindow = self.pob_config.win
        # self.player = player.Player()
        self.filename = ""
        self.ui = None
        self.need_saving = True
        self.current_tab = "TREE"
        self.trees = {_VERSION: Tree(self.pob_config)}
        self.current_tree = self.trees.get(_VERSION)
        self.specs = []
        self.activeSpec = 1
        self.current_spec = None

        # variables from the xml
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

        # Now fill out everything above out with a new build
        self.new(empty_build)

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
        # self.ui.combo_classes.setCurrentIndex(new_class.value)

    def new(self, _build):
        self.name = "Default"
        self.build = _build["PathOfBuilding"]["Build"]
        self.import_field = _build["PathOfBuilding"]["Import"]
        self.calcs = _build["PathOfBuilding"]["Calcs"]
        self.skills = _build["PathOfBuilding"]["Skills"]
        self.notes = _build["PathOfBuilding"]["Notes"]
        self.notes_html = _build["PathOfBuilding"].get("NotesHTML", None)
        self.tree_view = _build["PathOfBuilding"]["TreeView"]
        self.items = _build["PathOfBuilding"]["Items"]
        self.config = _build["PathOfBuilding"]["Items"]
        self.tree = _build["PathOfBuilding"]["Tree"]
        self.specs.clear()

        # Get Specs.
        # One Spec appears as a dictionary, but multiple appear as a list
        if type(self.tree["Spec"]) == list:
            for spec in self.tree["Spec"][:]:
                self.specs.append(Spec(spec))
        else:
            self.specs.append(Spec(self.tree["Spec"]))
        # In the xml, is 1 based, but python indexes are 0 based, so we subtract 1
        self.activeSpec = int(self.tree.get("@activeSpec", 1)) - 1
        self.current_spec = self.specs[self.activeSpec]

    def load(self, filename):
        """
        Load a build
        :param filename: str() XML file to load
        :return: N/A
        """
        _build_pob = pob_file.read_xml(filename)
        if _build_pob is None:
            tr = self.pob_config.app
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

    def save(self):
        """
        Save the build to the filename recorded in the build Class
        :return: N/A
        """
        pob_file.write_xml(self.filename, self.build)

    def save_as(self, filename):
        """
        Save the build to a new name
        :param filename:
        :return: N/A
        """
        self.filename = filename
        pob_file.write_xml(filename, self.build)

    def ask_for_save_if_modified(self):
        """
        Check if the build has been modified and if so, prompt for saving.
        :return: True if build saved
        :return: False if build save was refused by the user
        """
        return True

    def change_tree(self, tree_id):
        if tree_id is None:
            return
        self.activeSpec = tree_id
        self.current_spec = self.specs[tree_id]

    @property
    def className(self):
        return self.build["@className"]

    @className.setter
    def className(self, new_name):
        self.build["@className"] = new_name

    @property
    def ascendClassName(self):
        return self.build["@ascendClassName"]

    @ascendClassName.setter
    def ascendClassName(self, new_name):
        self.build["@ascendClassName"] = new_name

    @property
    def level(self):
        return int(self.build["@level"])

    @level.setter
    def level(self, new_level):
        self.build["@level"] = f"{new_level}"

    @property
    def bandit(self):
        return self.build["@bandit"]

    @bandit.setter
    def bandit(self, new_name):
        self.build["@bandit"] = new_name

    @property
    def mainSocketGroup(self):
        return self.build["@mainSocketGroup"]

    @mainSocketGroup.setter
    def mainSocketGroup(self, new_name):
        self.build["@mainSocketGroup"] = new_name

    @property
    def pantheonMajorGod(self):
        return self.build["@pantheonMajorGod"]

    @pantheonMajorGod.setter
    def pantheonMajorGod(self, new_name):
        self.build["@pantheonMajorGod"] = new_name

    @property
    def pantheonMinorGod(self):
        return self.build["@pantheonMinorGod"]

    @pantheonMinorGod.setter
    def pantheonMinorGod(self, new_name):
        self.build["@pantheonMinorGod"] = new_name

    @property
    def targetVersion(self):
        return self.build["@targetVersion"]

    @targetVersion.setter
    def targetVersion(self, new_name):
        self.build["@targetVersion"] = new_name

    @property
    def viewMode(self):
        return self.build["@viewMode"]

    @viewMode.setter
    def viewMode(self, curr_tab):
        self.build["@viewMode"] = curr_tab.upper

    # @property
    # def (self):
    #     return self.build[""]
    #
    # @.setter
    # def (self, new_name):
    #     self.build[""] = new_name


class Spec:
    def __init__(self, _spec) -> None:
        self.title = _spec.get("@title", "Default")
        self.ascendClassId = _spec.get("@ascendClassId", 0)
        self.masteryEffects = _spec.get("@masteryEffects", None)
        # ToDo this includes ascendancy nodes (grrr)
        self.nodes = {}
        str_nodes = _spec.get('@nodes', '0')
        if str_nodes:
            self.nodes = str_nodes.split(',')
        self.treeVersion = _spec.get("@treeVersion", re.sub("\.", "_", str(_VERSION)))
        self.classId = PlayerClasses(int(_spec.get("@classId", PlayerClasses.SCION)))
        self.EditedNodes = _spec.get("EditedNodes", None)
        self.URL = _spec.get(
            "", "https://www.pathofexile.com/passive-skill-tree/AAAABgAAAAAA"
        )
        self.Sockets = _spec.get("", 1)
