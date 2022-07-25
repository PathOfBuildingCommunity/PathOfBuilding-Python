"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

from pathlib import Path
from bs4 import BeautifulSoup as soup

from pob_config import (
    Config,
    ColourCodes,
    program_title,
    PlayerClasses,
    _VERSION,
    empty_build,
)
import pob_file
import ui_utils
from tree import Tree
from PoB_Main_Window import Ui_MainWindow


class Build:
    def __init__(self, _config: Config, __name: str = "New") -> None:
        self.pob_config = _config
        self._name = __name
        self.ui: Ui_MainWindow = self.pob_config.win
        # self.player = player.Player()
        self.filename = ""
        self.current_tab = "Tree"
        self.trees = {_VERSION: Tree(self.pob_config)}
        self.current_tree = self.trees.get(_VERSION)
        self.ui = None
        self.need_saving = False

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
        return self.current_tree.char_class

    @current_class.setter
    def current_class(self, new_class):
        """
        Actions required for changing classes
        :param new_class: Integer representing the PlayerClasses enumerations
        :return:
        """
        self.current_tree.char_class = new_class
        self.ui.classes_combobox.setCurrentIndex(new_class)

    def new(self, _build):
        self.name = "New"
        self.build = _build["PathOfBuilding"]["Build"]
        self.import_field = _build["PathOfBuilding"]["Import"]
        self.calcs = _build["PathOfBuilding"]["Calcs"]
        self.skills = _build["PathOfBuilding"]["Skills"]
        self.tree = _build["PathOfBuilding"]["Tree"]
        self.notes = _build["PathOfBuilding"]["Notes"]
        self.notes_html = _build["PathOfBuilding"].get("NotesHTML", None)
        self.tree_view = _build["PathOfBuilding"]["TreeView"]
        self.items = _build["PathOfBuilding"]["Items"]
        self.config = _build["PathOfBuilding"]["Items"]

    def load(self, filename):
        """
        Load a build
        :param filename: str() XML file to load
        :return: N/A
        """
        _name = "New"
        _build_pob = pob_file.read_xml(filename)
        # print(_build_pob)
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

    @property
    def ascendClassName(self):
        return self.build["@ascendClassName"]

    @ascendClassName.setter
    def ascendClassName(self, new_name):
        self.build["@ascendClassName"] = new_name

    @property
    def bandit(self):
        return self.build["@bandit"]

    @bandit.setter
    def bandit(self, new_name):
        self.build["@bandit"] = new_name

    @property
    def className(self):
        return self.build["@className"]

    @className.setter
    def className(self, new_name):
        self.build["@className"] = new_name

    @property
    def level(self):
        return int(self.build["@level"])

    @level.setter
    def level(self, new_level):
        self.build["@level"] = f"{new_level}"

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
