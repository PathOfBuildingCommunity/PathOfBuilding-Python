"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

from qdarktheme.qtpy.QtCore import Slot

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
        self.win: Ui_MainWindow = self.pob_config.win
        # self.player = player.Player()
        self.filename = ""
        self.search_text = ""
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
        # self.win.combo_classes.setCurrentIndex(new_class.value)

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

    @property
    def current_spec(self):
        """
        Manage the currently chosen spec in the config class so it can be used by many other classes
        :return:
        """
        return self.pob_config.current_spec

    @current_spec.setter
    def current_spec(self, new_spec):
        self.pob_config.current_spec = new_spec

    # @property
    # def (self):
    #     return self.build[""]

    # @.setter
    # def (self, new_name):
    #     self.build[""] = new_name

    def new(self, _build):
        """
        common function to load internal variables from the dictionary
        :param _build: Dictionary fromloading the source XML or the default one
        :return: N/A
        """
        self.name = "Default"
        pob = _build.get("PathOfBuilding", None)
        if pob:
            self.build = pob["Build"]
            self.import_field = pob["Import"]
            self.calcs = pob["Calcs"]
            self.skills = pob["Skills"]
            self.notes = pob.get("Notes", "")
            self.notes_html = pob.get("NotesHTML", None)
            self.tree_view = pob["TreeView"]
            self.items = pob["Items"]
            self.config = pob["Config"]
            self.tree = pob["Tree"]
            self.specs.clear()

            # Get Specs.
            # One Spec appears as a dictionary, but multiple appear as a list
            if type(self.tree["Spec"]) == list:
                for spec in self.tree["Spec"][:]:
                    self.specs.append(Spec(spec))
            else:
                self.specs.append(Spec(self.tree["Spec"]))
            # In the xml, activeSpec is 1 based, but python indexes are 0 based, so we subtract 1
            self.activeSpec = int(self.tree.get("@activeSpec", 1)) - 1
            self.current_spec = self.specs[self.activeSpec]

    # new

    def load(self, filename):
        """
        Load a build. Use new() as a common function
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
            self.win.notes_ui.load(self.notes_html, self.notes)

    def save(self):
        """
        Save the build to the filename recorded in the build Class
        :return: N/A
        """
        pob = {'PathOfBuilding': {}}
        pob["PathOfBuilding"]["Build"] = self.build
        pob["PathOfBuilding"]["Import"] = self.import_field
        pob["PathOfBuilding"]["Calcs"] = self.calcs
        pob["PathOfBuilding"]["Skills"] = self.skills
        self.notes, self.notes_html = self.win.notes_ui.save()
        pob["PathOfBuilding"]["Notes"] = self.notes
        pob["PathOfBuilding"]["NotesHTML"] = self.notes_html
        pob["PathOfBuilding"]["TreeView"] = self.tree_view
        pob["PathOfBuilding"]["Items"] = self.items
        pob["PathOfBuilding"]["Config"] = self.config
        pob["PathOfBuilding"]["Tree"] = self.tree
        pob_file.write_xml('builds/test.xml', pob)
        # pob_file.write_xml(self.filename, pob)

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
        def_spec = empty_build["PathOfBuilding"]["Tree"]["Spec"]
        if _spec is None:
            _spec = def_spec

        self.title = _spec.get("@title", def_spec["@title"])

        self.classId = PlayerClasses(int(_spec.get("@classId", PlayerClasses.SCION)))
        self.ascendClassId = int(_spec.get("@ascendClassId", 0))

        self.masteryEffects = _spec.get("@masteryEffects", None)
        # ToDo this includes ascendancy nodes (grrr)
        # self.nodes = _spec.get("@nodes", "0")
        self.nodes = {}
        str_nodes = _spec.get("@nodes", "0")
        if str_nodes:
            self.nodes = str_nodes.split(",")
        self.treeVersion = _spec.get("@treeVersion", def_spec["@treeVersion"])
        self.EditedNodes = _spec.get("EditedNodes", None)
        self.URL = _spec.get("URL", def_spec["URL"])

        self.Sockets = _spec.get("Sockets", 1)
