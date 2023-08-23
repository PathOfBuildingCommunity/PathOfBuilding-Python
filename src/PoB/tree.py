"""
Tree Class

This class represents an instance of the Passive Tree for **ONE** tree version.
Multiple versions of Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemisations, etc.), so there could be multiple instantiations of this class.

A Tree() instance is tied to a Version of the Tree as released by GGG (eg: 3.18).

This holds, in memory, a copy of the tree data and doesn't know about any actively selected nodes.
  That's the Build class' job.

It is referenced by the TreeView class to display the tree
"""

import re
import math
from collections import OrderedDict
from pathlib import Path
import pprint

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PySide6.QtWidgets import QGraphicsLineItem

from dialogs.popup_dialogs import critical_dialog
from PoB.pob_config import Config
from PoB.constants import (
    ColourCodes,
    Layers,
    PlayerClasses,
    _VERSION_str,
    ascendancy_positions,
    global_scale_factor,
    tree_versions,
)
from PoB.pob_file import read_json
from PoB.node import Node
from widgets.tree_graphics_item import TreeGraphicsItem
from widgets.ui_utils import _debug

nodeOverlay = {
    "Normal": {
        "artWidth": "40",
        "alloc": "PSSkillFrameActive",
        "path": "PSSkillFrameHighlighted",
        "unalloc": "PSSkillFrame",
        "allocAscend": "AscendancyFrameSmallAllocated",
        "pathAscend": "AscendancyFrameSmallCanAllocate",
        "unallocAscend": "AscendancyFrameSmallNormal",
    },
    "Notable": {
        "artWidth": "58",
        "alloc": "NotableFrameAllocated",
        "path": "NotableFrameCanAllocate",
        "unalloc": "NotableFrameUnallocated",
        "allocAscend": "AscendancyFrameLargeAllocated",
        "pathAscend": "AscendancyFrameLargeCanAllocate",
        "unallocAscend": "AscendancyFrameLargeNormal",
        "allocBlighted": "BlightedNotableFrameAllocated",
        "pathBlighted": "BlightedNotableFrameCanAllocate",
        "unallocBlighted": "BlightedNotableFrameUnallocated",
    },
    "Keystone": {
        "artWidth": "84",
        "alloc": "KeystoneFrameAllocated",
        "path": "KeystoneFrameCanAllocate",
        "unalloc": "KeystoneFrameUnallocated",
    },
    "Socket": {
        "artWidth": "58",
        "alloc": "JewelFrameAllocated",
        "path": "JewelFrameCanAllocate",
        "unalloc": "JewelFrameUnallocated",
        "allocAlt": "JewelSocketAltActive",
        "pathAlt": "JewelSocketAltCanAllocate",
        "unallocAlt": "JewelSocketAltNormal",
    },
    "Mastery": {
        "artWidth": "65",
        "alloc": "AscendancyFrameLargeAllocated",
        "path": "AscendancyFrameLargeCanAllocate",
        "unalloc": "AscendancyFrameLargeNormal",
    },
}
for _type in nodeOverlay:
    """
    From PassiveTree.lua file. Setting as the same scope as the 'constant'
    """
    data = nodeOverlay[_type]
    size = int(data["artWidth"]) * 1.33
    data["size"] = size
    data["rsq"] = size * size


# fmt: off
# Formatting makes a mess of these structures (unreadable)
def calc_orbit_angles(nodes_in_orbit):
    orbit_angles = {}
    if nodes_in_orbit == 16:
        # Every 30 and 45 degrees, per https://github.com/grindinggear/skilltree-export
        orbit_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
    elif nodes_in_orbit == 40:
        # Every 10 and 45 degrees
        orbit_angles = [0, 10, 20, 30, 40, 45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 135, 140, 150, 160, 170, 180,
                        190, 200, 210, 220, 225, 230, 240, 250, 260, 270, 280, 290, 300, 310, 315, 320, 330, 340,
                        350]
    else:
        # Uniformly spaced
        orbit_angles[0] = 0
        for i in range(nodes_in_orbit):
            orbit_angles[i + 1] = 360 * i / nodes_in_orbit

    for i in range(len(orbit_angles)):
        orbit_angles[i] = math.radians(orbit_angles[i])

    return orbit_angles
    # calc_orbit_angles
# fmt: on


class Tree:
    def __init__(self, _config: Config, _version: str = _VERSION_str) -> None:
        # declare variables that are set in functions
        self.config = _config
        self.version = _version

        self.name = "Default"
        self.ui = None
        # self.assets = {}
        self.classes = {}
        self.groups = {}
        self.nodes = {}
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.size = QRect(self.min_x, self.min_y, self.max_x, self.max_y)
        # list of graphic items in no specific order
        self.graphics_items = []
        # lines are separate as they do not have the same properties as TreeGraphicsItem's
        self.lines = []
        self.total_points = 0
        self.ascendancy_points = 8
        self.skillsPerOrbit = {}
        self.orbitRadii = {}
        self.orbit_anglesByOrbit = {}

        # sprite_sheets is a way of tracking what we've loaded. it is referenced by all Art loading procedures
        self.sprite_sheets = {}
        self.ascendancyMap = {}
        self.clusterNodeMap = {}
        self.constants = {}
        self.keystoneMap = {}
        self.masteryEffects = {}
        self.notableMap = {}
        self.sockets = {}
        # Should this be a dict of GraphicItems
        self.spriteMap = {}
        # A List of non cluster jewel sprites
        self.jewel_sprites = {}
        # A List of cluster jewel sprites
        self.cluster_sprites = {}
        self.assets = {}
        # list of images for the ascendancy circles
        self.ascendancy_group_list = []
        # dictionary, by name, of node start ids for each ascendancy
        self.ascendancy_start_nodes = {}
        # dictionary of a list of nodes in a given mastery group, eg: "Life Mastery"
        self.mastery_effects_nodes = {}

        self.load()

    def __repr__(self) -> str:
        ret_str = f"[TREE]: version '{self.version}'\n"
        return ret_str

    # @property
    # def char_class(self):
    #     return self._char_class
    #
    # @char_class.setter
    # def char_class(self, new_class):
    #     self._char_class = new_class

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, new_vers):
        self._version = new_vers
        self.tree_version_path = Path(self.config.data_dir, re.sub(r"\.", "_", str(new_vers)))
        self.json_file_path = Path(self.tree_version_path, "tree.json")
        self.legion_path = Path(self.config.data_dir, "legion")

    def add_picture(self, name, x, y, ox, oy, _layer=Layers.inactive, node=None):
        """
        Add a picture
        :param name: string or pixmap to be added
        :param x: it's position in the scene
        :param y: it's position in the scene
        :param ox: it's position in the scene
        :param oy: it's position in the scene
        :param _layer: Layers: which layer to use:
        :param node: Node: The associated node, so we can load up TreeGraphicsItem variables
        :return: ptr to the created TreeGraphicsItem
        """
        image = TreeGraphicsItem(self.config, name, node, _layer, True)
        image.setPos(x, y)
        image.setOffset(ox, oy)
        if _layer not in [Layers.active, Layers.active_effect]:
            # if nonactive:
            self.graphics_items.append(image)
        return image

    def add_line(self, x1, y1, x2, y2, z=Layers.connectors):
        """
        Add a line
        :param x1: it's start position in the scene
        :param y1: it's start position in the scene
        :param x2: it's end position in the scene
        :param y2: it's end position in the scene
        :param z: Layers: which layer to use:
        :return: ptr to the created TreeGraphicsItem
        """
        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setAcceptTouchEvents(False)
        line.setAcceptHoverEvents(False)
        line.setZValue(z)
        line.setPen(QPen(QColor(ColourCodes.CURRENCY.value), 1, Qt.SolidLine))
        if z != Layers.active:
            self.lines.append(line)
        return line

    def load(self):
        """
        Load the tree json of this Tree()'s version and process it

        :return:
        """
        print(f"Loading Tree: {tree_versions[self.version]}")
        try:
            json_dict = OrderedDict(read_json(self.json_file_path))
        except TypeError:
            json_dict = None
        if json_dict is None:
            tr = self.config.app.tr
            critical_dialog(
                self.config.win,
                f"{tr('Load Tree')}: v{self.version}",
                f"{tr('An error occurred to trying load')}:\n{self.json_file_path}",
                tr("Close"),
            )
            return

        self.min_x = json_dict["min_x"] / global_scale_factor
        self.min_y = json_dict["min_y"] / global_scale_factor
        self.max_x = json_dict["max_x"] / global_scale_factor
        self.max_y = json_dict["max_y"] / global_scale_factor
        self.total_points = json_dict["points"]["totalPoints"]
        self.ascendancy_points = json_dict["points"]["ascendancyPoints"]
        # and now split the file into dicts
        if float(tree_versions[self.version]) < 3.18:
            self.assets = json_dict["assets"]
            # this information is moved into self.spriteMap
            skill_sprites = json_dict["skillSprites"]
        else:
            skill_sprites = json_dict["sprites"]
            self.assets = self.spriteMap
        self.classes = json_dict["classes"]
        self.constants = json_dict["constants"]

        # add group indexes as int's not string
        groups = json_dict["groups"]
        for group_id in groups:
            self.groups[int(group_id)] = groups[group_id]

        # add node indexes as int's not string
        nodes = json_dict["nodes"]
        del nodes["root"]  # make the root node go away
        for node_id in nodes:
            self.nodes[int(node_id)] = nodes[node_id]

        # Get last entry (highest zoom factor)
        zoom_text = f'{json_dict["imageZoomLevels"][-1]}'

        self.skillsPerOrbit = self.constants["skillsPerOrbit"]
        self.orbitRadii = self.constants["orbitRadii"]
        self.orbitRadii = [i / global_scale_factor for i in self.constants["orbitRadii"]]

        self.orbit_anglesByOrbit = {}
        for orbit, skillsInOrbit in enumerate(self.skillsPerOrbit):
            self.orbit_anglesByOrbit[orbit] = calc_orbit_angles(skillsInOrbit)

        """ Build maps of class name -> class table """
        ascend_name_map = {}
        class_notables = {}
        # loop through each class
        for class_id, _class in enumerate(self.classes):
            # create the first ascendancy for each class as; "0" = None
            _class.update({0: {"name": "None"}})
            for ascend_class_id, _ascend_class in enumerate(_class.get("ascendancies", None)):
                ascend_name_map[_ascend_class.get("name")] = {
                    "classId": class_id,
                    "class": _class,
                    "ascendClassId": ascend_class_id,
                    "ascendClass": _ascend_class,
                }

        # Process a sprite map list for loading the image
        self.process_sprite_map(skill_sprites, self.sprite_sheets, self.tree_version_path, zoom_text)

        # """Now do the legion sprite import"""
        # legion_sprites = read_json(Path(self.legion_path, "tree-legion.json"))
        # if not legion_sprites:
        #     critical_dialog(
        #         self.config.win,
        #         "f{self.config.app.tr('Load File')}",
        #         "f{self.config.app.tr('An error occurred to trying load')}:\n{self.legion_file_path}",
        #         self.config.app.tr("Close"),
        #     )
        # else:
        #     # Process a sprite map list for loading the image (downloading it too later)
        #     self.process_sprite_map(
        #         legion_sprites["legionSprites"], self.sprite_sheets, self.legion_path, 0
        #     )
        #
        # """Now do the other asset's import"""
        # if self._version < 3.18:
        #   self.process_assets(self.assets)
        #
        """ Migrate groups to old format. ToDo: To be evaluated if this is needed
            also scale x,y"""
        for g in self.groups:
            group = self.groups[g]
            group["n"] = group["nodes"]
            group["x"] = group["x"] / global_scale_factor
            group["y"] = group["y"] / global_scale_factor
            group["oo"] = {}
            for orbit in group["orbits"]:
                group["oo"][orbit] = True

        # """ Create a dictionary list of nodes of class Node()
        #     self.nodes = dictionary from the json"""
        for node_id in self.nodes:
            # Overwrite the json node definition with our class definition
            node = Node(self.nodes[node_id])
            self.nodes[node_id] = node

            # Find the node's type
            self.set_node_type(node, ascend_name_map, class_notables)

            # Find the node's group
            if node.group_id >= 0:
                group = self.groups.get(node.group_id, None)
                if group is not None:
                    group["ascendancyName"] = node.ascendancyName
                    group["isAscendancyStart"] = node.isAscendancyStart
                    group["classStartIndex"] = node.classStartIndex
                    node.group = group
            elif node.type == "Notable" or node.type == "Keystone":
                self.clusterNodeMap[node.dn] = node

            # Finally the node will get an x,y value. Now we can show it.
            self.process_node(node)

        # Add background lines
        lines_db = {}
        for node_id in self.nodes:
            node = self.nodes[node_id]
            if node.type not in ("ClassStart", "Mastery"):
                in_out_nodes = []
                # for other_node_id in node.nodes_out + node.nodes_in:
                for other_node_id in node.nodes_out.union(node.nodes_in):
                    other_node = self.nodes.get(other_node_id, None)
                    if (
                        other_node is not None
                        and other_node.type not in ("ClassStart", "Mastery")
                        # This stops lines crossing out of the Ascendancy circles
                        and node.ascendancyName == other_node.ascendancyName
                    ):
                        in_out_nodes.append(other_node)

                for other_node in in_out_nodes:
                    # check if we have this line already
                    ids = sorted([node.id, other_node.id])
                    index = f"{ids[0]}_{ids[1]}"
                    if not lines_db.get(index, False):
                        lines_db[index] = True
                        self.add_line(node.x, node.y, other_node.x, other_node.y)

        # Add the group backgrounds
        # DO NOT join this 'for g' loop with the one above. It makes the backgrounds disappear
        for g in self.groups:
            group = self.groups[g]
            if not group.get("isProxy", False):
                self.render_group_background(group, g)

        # ToDo: Temporary code for data checking purposes
        # ToDo: Leave in place until all coding, including calcs are complete
        # from pprint import pprint
        # _path = Path("temp")
        # if not _path.exists():
        #     _path.mkdir()
        # with open(f"{_path}/{node.id}.txt", "w") as fout:
        #     # pprint(vars(node), fout)
        #     pprint(
        #         dict(
        #             (name, getattr(node, name))
        #             for name in dir(node)
        #             if not name.startswith("__")
        #         ),
        #         fout,
        #     )

        # load

    def process_node(self, node: Node):
        """

        :param node:
        :return:
        """

        def add_sprite(_sprite, _node, _layer=Layers.inactive):
            """
            add a sprite to our graphics list
            :param _sprite: the inactive sprite or overlay to be added
            :param _layer: the layer this sprite is to be added in
            :param _node: the node
            :return: a reference to the tree graphic image added
            """
            sprite = self.add_picture(_sprite["handle"], _node.x, _node.y, _sprite["ox"], _sprite["oy"], _layer, _node)
            sprite.name = _sprite["name"]
            sprite.node_id = _node.id
            sprite.filename = _node.icon
            sprite.node_sd = _node.sd
            sprite.node_name = _node.name
            sprite.node_type = _node.type
            sprite.node_reminder = _node.reminderText
            # sprite.node_tooltip = node.tooltip

            return sprite

        node.inactive_sprite = None
        # Assign node artwork assets
        if node.type == "Mastery":
            # This is the icon that appears in the center of many groups
            this_nodes_effect_list = self.mastery_effects_nodes.setdefault(node.name, [])
            if node.id not in this_nodes_effect_list:
                this_nodes_effect_list.append(node.id)
            if node.masteryEffects:
                node.masterySprites = {
                    "activeIcon": self.spriteMap[node.activeIcon]["masteryActiveSelected"],
                    "inactiveIcon": self.spriteMap[node.inactiveIcon]["masteryInactive"],
                    "activeEffectImage": self.spriteMap[node.activeEffectImage]["masteryActiveEffect"],
                }
                node.inactive_sprite = self.spriteMap[node.inactiveIcon]["masteryInactive"]
                node.active_sprite = self.spriteMap[node.activeIcon]["masteryActiveSelected"]
                node.activeEffectImage = self.spriteMap[node.activeEffectImage]["masteryActiveEffect"]
            else:
                # No active image
                node.sprites = self.spriteMap[node.icon]["mastery"]
                node.inactive_sprite = node.sprites
        elif node.type == "Socket":
            if node.expansionJewel:
                node.active_sprite = self.spriteMap["JewelSocketAltActive"]
                node.sprites = self.cluster_sprites
            else:
                node.active_sprite = self.spriteMap[f"JewelFrameAllocated"]
                node.sprites = self.jewel_sprites
        elif node.type == "ClassStart":
            # This is the pretty icon over the class start; with the red, blue and green dots.
            node.inactive_sprite = self.spriteMap[node.startArt]["startNode"]
            node.active_sprite = self.spriteMap[node.startArt]["startNode"]
        else:
            node.sprites = self.spriteMap[node.icon]
            node.inactive_sprite = node.sprites[f"{node.type.lower()}Inactive"]
            node.active_sprite = node.sprites[f"{node.type.lower()}Active"]

        # setting this to "if node.sprites is not None:" makes the sprites disappear
        #       if x is not None # which works only on None
        if not node.sprites and not node.masterySprites:
            # No active image
            node.sprites = self.spriteMap["Art/2DArt/SkillIcons/passives/MasteryBlank.png"]["normalInactive"]
            node.inactive_sprite = node.sprites

        # Derive the true position of the node
        if node.group:
            """orbit_radius, x and y have already been scaled"""
            node.angle = self.orbit_anglesByOrbit[node.o][node.oidx]
            orbit_radius = self.orbitRadii[node.o]

            """ Move all nodes to the correct location"""
            # _a_name == "" means this a non ascendancy node
            _a_name = node.ascendancyName
            # Ascendant position in the json is good ...
            if _a_name == "" or _a_name == "Ascendant":
                node.x = node.group["x"] + math.sin(node.angle) * orbit_radius
                node.y = node.group["y"] - math.cos(node.angle) * orbit_radius
            else:
                # ... all other ascendancies else needs hard coding
                # Chieftain has two groups (3 and 7) with different start positions
                if _a_name == "Chieftain" and node.g == 3:
                    _a_name = "Chieftain_g3"
                node.x = ascendancy_positions[_a_name]["x"] + math.sin(node.angle) * orbit_radius
                node.y = ascendancy_positions[_a_name]["y"] - math.cos(node.angle) * orbit_radius

            if node.inactive_sprite and node.inactive_sprite.get("handle", None) is not None:
                node.inactive_image = add_sprite(node.inactive_sprite, node)
            if node.active_sprite and node.active_sprite.get("handle", None) is not None:
                node.active_image = add_sprite(node.active_sprite, node, Layers.active)
            if node.activeEffectImage and node.activeEffectImage.get("handle", None) is not None:
                node.activeEffectImage = add_sprite(node.activeEffectImage, node, Layers.active_effect)

            # "ClassStart" might belong in treeView still depending on the size of the active asset
            if node.type == "ClassStart":
                # No active image
                node.inactiveOverlay = self.spriteMap["PSStartNodeBackgroundInactive"]["startNode"]
                add_sprite(node.inactiveOverlay, node)
            elif node.type == "AscendClassStart":
                # No active image
                node.inactiveOverlay = self.spriteMap["AscendancyMiddle"]["ascendancy"]
                add_sprite(node.inactiveOverlay, node)
            else:
                node.overlay = nodeOverlay.get(node.type, None)
                if node.overlay:
                    node.rsq = node.overlay["rsq"]
                    node.size = node.overlay["size"]
                    _layer = node.type in ("Notable", "Socket") and Layers.key_overlays or Layers.small_overlays

                    # inactive overlay image
                    if node.type == "Socket":
                        inactive_overlay_name = node.overlay.get(
                            f"unalloc{node.expansionJewel and 'Alt' or ''}",
                            "",
                        )
                    else:
                        inactive_overlay_name = node.overlay.get(
                            f"unalloc{node.ascendancyName and 'Ascend' or ''}{node.isBlighted and 'Blighted' or ''}",
                            "",
                        )
                    overlay_type = f"{'Ascendancy' in inactive_overlay_name and 'ascendancy' or 'frame'}"
                    node.inactiveOverlay = self.spriteMap[inactive_overlay_name][overlay_type]
                    node.inactive_overlay_image = add_sprite(node.inactiveOverlay, node, _layer)
                    node.inactive_overlay_image.node_isoverlay = True
                    # active overlay image
                    if node.type == "Socket":
                        active_overlay_name = node.overlay.get(
                            f"alloc{node.expansionJewel and 'Alt' or ''}",
                            "",
                        )
                    else:
                        active_overlay_name = node.overlay.get(
                            f"alloc{node.ascendancyName and 'Ascend' or ''}{node.isBlighted and 'Blighted' or ''}",
                            "",
                        )
                    node.activeOverlay = self.spriteMap[active_overlay_name][overlay_type]
                    node.active_overlay_image = add_sprite(node.activeOverlay, node, Layers.active)
                    node.active_overlay_image.node_isoverlay = True
        # process_node

    def set_node_type(self, node: Node, ascend_name_map, class_notables):
        """
        Decide and assign a type value to a node
        :param node: The target node
        :param ascend_name_map: Dictionary for the Ascendancies
        :param class_notables: Dictionary for the Class Notables
        :return:
        """
        # Default node.type is "Normal", so we are looking for exceptions or nodes that need more processing
        if node.classStartIndex >= 0:
            node.type = "ClassStart"
            node.startArt = f"center{PlayerClasses(node.classStartIndex).name.lower()}"
            _class = self.classes[node.classStartIndex]
            _class["startNodeId"] = node.id
        elif node.isAscendancyStart:
            # node.type = "AscendClassStart"  # Can't use this as there is no "ascendclassstartInactive" sprite
            ascend_name_map[node.ascendancyName]["ascendClass"]["startNodeId"] = node.id
            self.ascendancy_start_nodes[node.ascendancyName] = node.id
        elif node.isMastery:
            node.type = "Mastery"
            if node.masteryEffects:
                for effect in node.masteryEffects:
                    _id = str(effect["effect"])
                    if self.masteryEffects.get(_id, None) is not None:
                        self.masteryEffects[_id] = {"id": _id, "sd": effect["stats"]}
                        # self.ProcessStats(self.masteryEffects[_id])
        elif node.isJewelSocket:
            node.type = "Socket"
            self.sockets[node.id] = node
        elif node.isKeystone:
            node.type = "Keystone"
            self.keystoneMap[node.dn] = node
            self.keystoneMap[node.dn.lower()] = node
        elif node.isNotable:
            node.type = "Notable"
            # Some nodes have duplicate names in the tree data for some reason, even though they're not on the tree
            # Only add them if they're actually part of a group (i.e. in the tree)
            # Add everything otherwise, because cluster jewel notables don't have a group
            if self.notableMap.get(node.dn.lower(), None) is None:
                self.notableMap[node.dn.lower()] = node
            elif node.g >= 0:
                self.notableMap[node.dn.lower()] = node

        # get all the Ascendancy nodes in separate lists
        if node.ascendancyName != "" and not node.isAscendancyStart:
            if self.ascendancyMap.get(node.ascendancyName, None) is None:
                self.ascendancyMap[node.ascendancyName] = []
            self.ascendancyMap[node.ascendancyName].append(node.id)

        # ToDo: What is class_notables for ? Copied from lua
        # if class_notables.get(ascend_name_map[node.ascendancyName]["class"]["name"], None) is None:
        #     class_notables[ascend_name_map[node.ascendancyName]["class"]["name"]] = {}
        # if ascend_name_map[node.ascendancyName]["class"]["name"] != "Scion":
        #     class_notables[ascend_name_map[node.ascendancyName]["class"]["name"]] = node.dn

        # set_node_type

    def process_sprite_map(self, sprite_list, sprite_map, sprite_path, index):
        """
        Process a sprite map list for loading the image (downloading it too later)
          and updating self.spriteMap (should these be a list of graphic items (using setOffset) ?

        :param sprite_list: Incoming Dictionary from a json file
        :param sprite_map: Dictionary to stop duplicate loading of a GraphicItem, to be shared between instantiations
        :param sprite_path: The path where the images are stored
        :param index: str: The string repesenting the highest zoom level
        :return: N/A
        """

        def mirror_image(_image):
            """
            Mirror an image. Specifically GroupBackgroundLargeHalfAlt.

            :param: _source: the image to be mirrored
            :return: the mirrored image
            """
            _source = _image.toImage()
            _result = QPixmap(_source.width(), _source.height() * 2)
            _result.fill(Qt.transparent)
            painter = QPainter()
            painter.begin(_result)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawImage(0, 0, _source)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawImage(0, _source.height(), _source.mirrored())
            painter.end()
            return _result

        def add_jewel_sprite(_name):
            """
            add a sprite to our graphics list
            :param _name: the jewel sprite name
            :return: a reference to the tree graphic image added
            """
            sprite = TreeGraphicsItem(self.config, self.spriteMap[_name]["jewel"]["handle"], None, Layers.active, True)
            sprite.name = _name
            return sprite

            # _type will be like normalActive, normalInactive, background

        for _type in sprite_list:
            # We don't use a background tile
            if _type == "background":
                continue
            _data = sprite_list[_type].get(index, None) or sprite_list[_type].get("1", None)
            if _data is None:
                continue
            # overwrite skill_sprites' filename attribute to a valid runtime filename
            filename = Path(re.sub(r"(\?.*)$", "", _data["filename"])).name
            filename = Path(sprite_path, filename)
            _data["filename"] = filename
            pixmap = sprite_map.get(filename, None)
            if pixmap is None:
                pixmap = QPixmap(filename)
                sprite_map[filename] = pixmap
            # name could be "Art/2DArt/SkillIcons/passives/2handeddamage.png", "ClassesAscendant"
            for name in _data["coords"]:
                if self.spriteMap.get(name, None) is None:
                    self.spriteMap[name] = {}
                coord = _data["coords"][name]
                # these are coordinates into the sprite map, not the screen
                x = int(coord["x"])
                y = int(coord["y"])
                w = int(coord["w"])
                h = int(coord["h"])
                # Get a copy of the original image, cropped to coords()
                image = pixmap.copy(x, y, w, h)
                if name == "GroupBackgroundLargeHalfAlt" or name == "PSGroupBackground3":
                    image = mirror_image(image)
                    h *= 2
                self.spriteMap[name][_type] = {
                    "handle": image,
                    "name": name,
                    "width": w,
                    "height": h,
                    "ox": -w / 2,
                    "oy": -h / 2,
                }

        # Basic jewels for all sockets
        self.jewel_sprites["Viridian Jewel"] = self.spriteMap["JewelSocketActiveGreen"]["jewel"]
        self.jewel_sprites["Crimson Jewel"] = self.spriteMap["JewelSocketActiveRed"]["jewel"]
        self.jewel_sprites["Cobalt Jewel"] = self.spriteMap["JewelSocketActiveBlue"]["jewel"]
        self.jewel_sprites["Prismatic Jewel"] = self.spriteMap["JewelSocketActivePrismatic"]["jewel"]
        self.jewel_sprites["Timeless Jewel"] = self.spriteMap["JewelSocketActiveLegion"]["jewel"]
        self.jewel_sprites["Abyss Jewel"] = self.spriteMap["JewelSocketActiveAbyss"]["jewel"]

        self.cluster_sprites["Viridian Jewel"] = self.spriteMap["JewelSocketActiveGreenAlt"]["jewel"]
        self.cluster_sprites["Crimson Jewel"] = self.spriteMap["JewelSocketActiveRedAlt"]["jewel"]
        self.cluster_sprites["Cobalt Jewel"] = self.spriteMap["JewelSocketActiveBlueAlt"]["jewel"]
        self.cluster_sprites["Prismatic Jewel"] = self.spriteMap["JewelSocketActivePrismaticAlt"]["jewel"]
        self.cluster_sprites["Timeless Jewel"] = self.spriteMap["JewelSocketActiveLegionAlt"]["jewel"]
        self.cluster_sprites["Abyss Jewel"] = self.spriteMap["JewelSocketActiveAbyssAlt"]["jewel"]
        self.cluster_sprites["Small Cluster Jewel"] = self.spriteMap["JewelSocketActiveAltRed"]["jewel"]
        self.cluster_sprites["Medium Cluster Jewel"] = self.spriteMap["JewelSocketActiveAltBlue"]["jewel"]
        self.cluster_sprites["Large Cluster Jewel"] = self.spriteMap["JewelSocketActiveAltPurple"]["jewel"]

        # with open("temp/spriteMap.txt", "a") as f_out:
        #     pprint(self.spriteMap, f_out)
        # process_sprite_map

    def process_assets(self, sprite_list):
        """
        remap assets' contents into internal resource ids.

        :param sprite_list: Incoming Dictionary from a json file
        :return: N/A
        """
        # ToDo: remap these assets into locations and add them to self.graphics_items with x,y coords
        for name in sprite_list:
            self.spriteMap[name] = {}
            if name == "GroupBackgroundLargeHalfAlt":
                # This needs to mirrored.
                _source = QImage(f":/Art/TreeData/{name}.png")
                _result = QPixmap(_source.width(), _source.height() * 2)
                _result.fill(Qt.transparent)
                painter = QPainter()
                painter.begin(_result)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.drawImage(0, 0, _source)
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.drawImage(0, _source.height(), _source.mirrored())
                painter.end()
            else:
                _result = QPixmap(f":/Art/TreeData/{name}.png")
            self.spriteMap[name] = {
                "handle": _result,
                "name": name,
                "width": _result.width,
                "height": _result.height,
            }
        # with open("spriteMap.txt", "w") as f_out:
        #     pprint(self.spriteMap, f_out)

        # process_assets

    def render_group_background(self, _group, g, is_expansion=False):
        __image = None
        # scale = 1
        if _group.get("ascendancyName", "") != "":
            a_name = _group["ascendancyName"]
            # ToDo: Accommodate a bug that makes Chieftain disappear
            if a_name == "Chieftain":
                _group["isAscendancyStart"] = True
            if _group.get("isAscendancyStart", False):
                # This is the ascendancy circles around the outside of the tree
                # Ascendant position in the json is good, everyone else needs hard coding
                if a_name == "Ascendant":
                    _x, _y = _group["x"], _group["y"]
                else:
                    _x, _y = (
                        ascendancy_positions[a_name]["x"],
                        ascendancy_positions[a_name]["y"],
                    )

                # add the picture and shift it by half itself to line up with the nodes
                sprite = self.spriteMap[f"Classes{a_name}"]["ascendancyBackground"]
                __image = self.add_picture(
                    sprite["handle"],
                    _x,
                    _y,
                    sprite["ox"],
                    sprite["oy"],
                    Layers.backgrounds,
                )
                __image.setScale(2.5 / global_scale_factor)
                __image.filename = f"Classes{a_name}"
                # Store these images for tree_view to darken as it needs
                self.ascendancy_group_list.append(__image)

        # Large background
        elif _group["oo"].get(3, False):
            sprite = self.spriteMap[is_expansion and "GroupBackgroundLargeHalfAlt" or "PSGroupBackground3"][
                "groupBackground"
            ]
            __image = self.add_picture(
                sprite["handle"],
                _group["x"],
                _group["y"],
                sprite["ox"],
                sprite["oy"],
                Layers.group,
            )
            __image.filename = f"{g} GroupBackgroundLargeHalfAlt"
            __image.setScale(2 / global_scale_factor)

        # Medium background
        elif _group["oo"].get(2, False):
            sprite = self.spriteMap[is_expansion and "GroupBackgroundMediumAlt" or "PSGroupBackground2"][
                "groupBackground"
            ]
            __image = self.add_picture(
                sprite["handle"],
                _group["x"],
                _group["y"],
                sprite["ox"],
                sprite["oy"],
                Layers.group,
            )
            __image.filename = f"{g} GroupBackgroundMediumAlt"
            __image.setScale(2 / global_scale_factor)

        # Small background
        elif _group["oo"].get(1, False):
            sprite = self.spriteMap[is_expansion and "GroupBackgroundSmallAlt" or "PSGroupBackground1"][
                "groupBackground"
            ]
            __image = self.add_picture(
                sprite["handle"],
                _group["x"],
                _group["y"],
                sprite["ox"],
                sprite["oy"],
                Layers.group,
            )
            __image.filename = f"{g} GroupBackgroundSmallAlt"
            __image.setScale(2.5 / global_scale_factor)

    # render_group_background


def test(config: Config) -> None:
    tree = Tree(config)
    print(tree.version)


if __name__ == "__test__":
    test(Config(None, None))
