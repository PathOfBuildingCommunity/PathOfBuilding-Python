"""
Node Class

This class represents one node of the Passive Tree.

It is referenced by the Tree class
"""
from pob_config import _VERSION


class Node:
    def __init__(self, _node, _version: str = _VERSION) -> None:
        # declare variables that are set in functions
        self.version = _version
        self._active = False

        # calculated values
        self.conquered = False
        self.linkedId = {}
        self.modKey = ""
        self.modList = {}
        self.mods = {}
        self.overlay = {}
        self.size = {}
        self.sprites = {}
        self.x = 0
        self.y = 0
        self._type = None
        self.startArt = None
        self._reminderText = ""  # Do not use None
        self.masterySprites = {}
        self.group = {}
        self.isBlighted = False

        # values from the passed in dictionary
        self.name = _node.get("name", None)
        self.dn = _node.get("name", None)
        self._id = _node.get("skill", 0)
        self.group_id = _node.get("group", -1)
        self.g = _node.get("group", -1)
        self.orbit = _node.get("orbit", 0)
        self.o = _node.get("orbit", 0)
        self.orbitIndex = _node.get("orbitIndex", 0)
        self.oidx = _node.get("orbitIndex", 0)
        self.passivePointsGranted = _node.get("passivePointsGranted", 0)
        self.stats = _node.get("stats", None)
        self.sd = _node.get("stats", None)
        self.reminderText = _node.get("reminderText", None)
        self.ascendancyName = _node.get("ascendancyName", None)
        self.icon = _node.get("icon", None)
        self.nodes_in = _node.get("in", None)
        self.nodes_out = _node.get("out", None)
        self.recipe = _node.get("recipe", None)
        self.classStartIndex = _node.get("classStartIndex", None)
        self.isNotable = _node.get("isNotable", False)
        self.isAscendancyStart = _node.get("isAscendancyStart", False)
        self.isMastery = _node.get("isMastery", False)
        self.inactiveIcon = _node.get("inactiveIcon", None)
        self.activeIcon = _node.get("activeIcon", None)
        self.activeEffectImage = _node.get("activeEffectImage", None)
        self.masteryEffects = _node.get("masteryEffects", None)
        self.isJewelSocket = _node.get("isJewelSocket", False)
        self.expansionJewel = _node.get("expansionJewel", None)
        self.isProxy = _node.get("isProxy", False)
        self.isKeystone = _node.get("isKeystone", False)
        self.flavourText = _node.get("flavourText", None)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def active(self):
        """
        Used for determining the right
        :return:
        """
        if self._active:
            return "Active"
        else:
            return "Inactive"

    @active.setter
    def active(self, new_state: bool):
        self._active = new_state

    @active.setter
    def active(self, new_state: str):
        self._active = new_state == "Active"

    @property
    def reminderText(self):
        return self._reminderText

    @reminderText.setter
    def reminderText(self, new_text):
        self._reminderText = ""
        if new_text is None:
            return
        for line in new_text:
            self._reminderText = f"{self._reminderText}{line}\n"
        self._reminderText = self._reminderText.strip()

    @property
    # def ntype(self, lower_case=False):
    def type(self):
        # if lower_case:
        #     return self._type.lower
        # else:
        return self._type

    @type.setter
    def type(self, new_type):
        self._type = new_type
