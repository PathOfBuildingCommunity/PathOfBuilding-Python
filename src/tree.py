"""
Tree Class

This class represents an instance of the Passive Tree for **ONE** tree version.
Multiple versions of Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemisations, etc.), so there could be multiple instantiations of this class.

A Tree instance is tied to a Version of the Tree as released by GGG (eg: 3.18).

This holds in memory a copy of the tree data and doesn't know about any actively selected nodes.
  That's the Build class' job.

It is referenced by the TreeView class to display the tree
"""
import re
import math
from pprint import pprint
from qdarktheme.qtpy.QtCore import QRect, Qt
from qdarktheme.qtpy.QtGui import QPixmap, QImage, QPainter


import ui_utils
from pob_config import *
from constants import _VERSION
from pob_file import *

# import pob_config
from tree_graphics_item import TreeGraphicsItem
from node import Node


# fmt: off
def calc_orbit_angles(nodes_in_orbit):
    orbit_angles = {}
    if nodes_in_orbit == 16:
        # Every 30 and 45 degrees, per https://github.com/grindinggear/skilltree-export/blob/3.17.0/README.md
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
    def __init__(self, _config: Config, _version: str = _VERSION) -> None:
        # declare variables that are set in functions
        self.config = _config
        self.version = _version

        self.name = "Default"
        # self._char_class = PlayerClasses.SCION.value  # can't use class here
        self.ui = None
        self.allocated_nodes = set()
        self.assets = {}
        self.classes = {}
        self.groups = {}
        self.nodes = {}
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.size = QRect(self.min_x, self.min_y, self.max_x, self.max_y)
        self.graphics_items = []
        self.total_points = 0
        self.ascendancy_points = 8
        self.skillsPerOrbit = {}
        self.orbitRadii = {}
        self.orbit_anglesByOrbit = {}

        self.ascendancyMap = {}
        self.clusterNodeMap = {}
        self.constants = {}
        self.keystoneMap = {}
        self.masteryEffects = {}
        self.notableMap = {}
        self.sockets = {}
        # Should this be a dict of GraphicItems
        self.spriteMap = {}

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
        self.tree_version_path = Path(
            self.config.tree_data_path, re.sub("\.", "_", str(new_vers))
        )
        self.json_file_path = Path(self.tree_version_path, "tree.json")
        self.legion_path = Path(self.config.tree_data_path, "legion")

    def add_picture(self, name, x, y, z=0):
        """
        Add a picture
        :param name: string or pixmap to be added
        :param x, y: it's position in the scene
        :param z: which layer to use:  -2: background, -1: connectors, 0: inactive,
                                        1: active (overwriting it's equivalent ???)
        :return: ptr to the created TreeGraphicsItem
        """
        # if pixmap and not pixmap.isNull():
        image = TreeGraphicsItem(self.config, name, z, False)
        image.setPos(x, y)
        image.setZValue(z)
        self.graphics_items.append(image)
        return image

    def load(self, vers=_VERSION):
        """
        Load the tree json of a given version and process it
        :param vers: The version of the tree to load
        :return:
        """
        print(f"Loading Tree: {vers}")
        json_dict = OrderedDict(pob_file.read_json(self.json_file_path))
        if json_dict is None:
            tr = self.config.app.tr
            ui_utils.critical_dialog(
                self.config.win,
                f"{tr('Load Tree')}: v{self.version}",
                f"{tr('An error occurred to trying load')}:\n{self.json_file_path}",
                tr("Close"),
            )
            return

        self._version = vers
        self.min_x = json_dict["min_x"] / global_scale_factor
        self.min_y = json_dict["min_y"] / global_scale_factor
        self.max_x = json_dict["max_x"] / global_scale_factor
        self.max_y = json_dict["max_y"] / global_scale_factor
        self.total_points = json_dict["points"]["totalPoints"]
        self.ascendancy_points = json_dict["points"]["ascendancyPoints"]
        # and now split the file into dicts
        self.assets = json_dict["assets"]
        self.classes = json_dict["classes"]
        self.constants = json_dict["constants"]
        self.groups = json_dict["groups"]
        self.nodes = json_dict["nodes"]
        # this information is moved into self.spriteMap
        skill_sprites = json_dict["skillSprites"]

        # -1 one as the dictionaries are 0 based indexes
        num_zoom_levels = len(json_dict["imageZoomLevels"]) - 1

        self.skillsPerOrbit = self.constants["skillsPerOrbit"]
        self.orbitRadii = self.constants["orbitRadii"]
        self.orbitRadii = [
            i / global_scale_factor for i in self.constants["orbitRadii"]
        ]

        self.orbit_anglesByOrbit = {}
        for orbit, skillsInOrbit in enumerate(self.skillsPerOrbit):
            self.orbit_anglesByOrbit[orbit] = calc_orbit_angles(skillsInOrbit)

        """Build maps of class name -> class table"""
        ascend_name_map = {}
        class_notables = {}
        # loop though each class
        for class_id, _class in enumerate(self.classes):
            # create the first entry as "0" = None
            _class.update({0: {"name": "None"}})
            for ascend_class_id, _ascend_class in enumerate(
                _class.get("ascendancies", None)
            ):
                ascend_name_map[_ascend_class.get("name")] = {
                    "classId": class_id,
                    "class": _class,
                    "ascendClassId": ascend_class_id,
                    "ascendClass": _ascend_class,
                }

        """ The sprite_sheets variable is a way of tracking what we've downloaded.
            might have thought the presence of the file would have done that."""
        sprite_sheets = {}
        # Process a sprite map list for loading the image (downloading it too later)
        self.process_sprite_map(
            skill_sprites, sprite_sheets, self.tree_version_path, num_zoom_levels
        )

        """Now do the legion sprite import"""
        legion_sprites = pob_file.read_json(Path(self.legion_path, "tree-legion.json"))
        if not legion_sprites:
            ui_utils.critical_dialog(
                self.config.win,
                "f{self.config.app.tr('Load File')}",
                "f{self.config.app.tr('An error occurred to trying load')}:\n{self.legion_file_path}",
                self.config.app.tr("Close"),
            )
        else:
            # Process a sprite map list for loading the image (downloading it too later)
            self.process_sprite_map(
                legion_sprites["legionSprites"], sprite_sheets, self.legion_path, 0
            )

        """Now do the other asset's import"""
        self.process_assets(self.assets)

        """ Migrate groups to old format. To be evaluated if this is needed
            also scale x,y"""
        for g in self.groups:
            group = self.groups[g]
            group["n"] = group["nodes"]
            group["x"] = group["x"] / global_scale_factor
            group["y"] = group["y"] / global_scale_factor
            group["oo"] = {}
            for orbit in group["orbits"]:
                group["oo"][orbit] = True

        """ Create a dictionary list of nodes of class Node()
            self.nodes = dictionary from the json"""
        # make the root node go away
        del self.nodes["root"]
        for n in self.nodes:
            node = Node(self.nodes[n])
            self.nodes[n] = node

            # Find the node's type
            self.set_node_type(node, ascend_name_map, class_notables)

            # Find the node's group
            if node.group_id >= 0:
                group = self.groups.get(str(node.group_id), None)
                if group is not None:
                    group["ascendancyName"] = node.ascendancyName
                    group["isAscendancyStart"] = node.isAscendancyStart
                    group["classStartIndex"] = node.classStartIndex
                    node.group = group
            elif node.type == "Notable" or node.type == "Keystone":
                self.clusterNodeMap[node.dn] = node

            # Finally the node will get an x,y value. Now we can show it.
            self.process_node(node)

            # ToDo: Temporary code for data checking purposes
            # ToDo: Leave in place until all coding, including calcs are complete
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
        # Assign node artwork assets
        if node.type == "Mastery" and node.masteryEffects:
            node.masterySprites = {
                "activeIcon": self.spriteMap[node.activeIcon],
                "inactiveIcon": self.spriteMap[node.inactiveIcon],
                "activeEffectImage": self.spriteMap[node.activeEffectImage],
            }
        else:
            node.sprites = self.spriteMap[node.icon]
        # setting this to "if node.sprites is not None:" makes the sprites disappear
        #       if x is not None # which works only on None
        if not node.sprites:
            node.sprites = self.spriteMap[
                "Art/2DArt/SkillIcons/passives/MasteryBlank.png"
            ]
        node.overlay = nodeOverlay.get(node.type, None)
        if node.overlay:
            node.rsq = node.overlay["rsq"]
            node.size = node.overlay["size"]

        # Derive the true position of the node
        if node.group:
            """orbit_radius, x and y have already been scaled"""
            node.angle = self.orbit_anglesByOrbit[node.o][node.oidx]
            orbit_radius = self.orbitRadii[node.o]

            """ Move all Ascendancy nodes to the correct location"""
            # Ascendant position in the json is good ...
            _a_name = node.ascendancyName
            if _a_name == "" or _a_name == "Ascendant":
                node.x = node.group["x"] + math.sin(node.angle) * orbit_radius
                node.y = node.group["y"] - math.cos(node.angle) * orbit_radius
            else:
                # ... everyone else needs hard coding
                node.x = (
                    ascendancy_positions[_a_name]["x"]
                    + math.sin(node.angle) * orbit_radius
                )
                node.y = (
                    ascendancy_positions[_a_name]["y"]
                    - math.cos(node.angle) * orbit_radius
                )

    # process_node

    def set_node_type(self, node: Node, ascend_name_map, class_notables):
        """
        Decide and assign a type value to a node
        :param node: The target node
        :param ascend_name_map: Dictionary for the Ascendancies
        :param class_notables: Dictionary for the Class Notables
        :return:
        """
        if node.classStartIndex >= 0:
            node.type = "ClassStart"
            node.startArt = f"center{PlayerClasses(node.classStartIndex).name.lower()}"
            _class = self.classes[node.classStartIndex]
            _class["startNodeId"] = node.id
        elif node.isAscendancyStart:
            node.type = "AscendClassStart"
            ascend_name_map[node.ascendancyName]["ascendClass"]["startNodeId"] = node.id
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
            if node.ascendancyName == "":
                # Some nodes have duplicate names in the tree data for some reason, even though they're not on the tree
                # Only add them if they're actually part of a group (i.e. in the tree)
                # Add everything otherwise, because cluster jewel notables don't have a group
                if self.notableMap.get(node.dn.lower(), None) is None:
                    self.notableMap[node.dn.lower()] = node
                elif node.g >= 0:
                    self.notableMap[node.dn.lower()] = node
            else:
                self.ascendancyMap[node.dn.lower()] = node
                if (
                    class_notables.get(
                        ascend_name_map[node.ascendancyName]["class"]["name"], None
                    )
                    is None
                ):
                    class_notables[
                        ascend_name_map[node.ascendancyName]["class"]["name"]
                    ] = {}
                if ascend_name_map[node.ascendancyName]["class"]["name"] != "Scion":
                    class_notables[
                        ascend_name_map[node.ascendancyName]["class"]["name"]
                    ] = node.dn
        else:
            node.type = "Normal"
            # Add all notables in the Scion Ascendancy, by excluding all the little nodes
            if (
                node.ascendancyName == "Ascendant"
                and "Dexterity" not in node.dn
                and "Intelligence" not in node.dn
                and "Strength" not in node.dn
                and "Passive" not in node.dn
            ):
                self.ascendancyMap[node.dn.lower()] = node
                if (
                    class_notables.get(
                        ascend_name_map[node.ascendancyName]["class"]["name"], None
                    )
                    is None
                ):
                    class_notables[
                        ascend_name_map[node.ascendancyName]["class"]["name"]
                    ] = {}
                class_notables[
                    ascend_name_map[node.ascendancyName]["class"]["name"]
                ] = node.dn

    # set_node_type

    def process_sprite_map(self, sprite_list, sprite_map, sprite_path, index):
        """
        Process a sprite map list for loading the image (downloading it too later)
          and updating self.spriteMap (should these be a list of graphic items (using setOffset) ?
        :param sprite_list: Incoming Dictionary from a json file
        :param sprite_map: Dictionary to stop duplicate loading of a GraphicItem, to be shared between instantiations
        :param sprite_path: The path where the images are stored
        :param index: A number describing which set of values to use
        :return: N/A
        """
        # _type will be like normalActive, normalInactive
        for _type in sprite_list:
            _data = sprite_list[_type][index]
            # remap skill_sprites' filename attribute to a valid runtime filename
            filename = Path(re.sub("(\?.*)$", "", _data["filename"])).name
            filename = Path(sprite_path, filename)
            _data["filename"] = filename
            pixmap = sprite_map.get(filename, None)
            if pixmap is None:
                # As the source is a sprite sheet, x,y can be 0 as it won't be seen on screen as itself.
                pixmap = QPixmap(filename)
                sprite_map[filename] = pixmap
            for name in _data["coords"]:
                if self.spriteMap.get(name, None) is None:
                    self.spriteMap[name] = {}
                coord = _data["coords"][name]
                w = int(coord["w"])
                h = int(coord["h"])
                x = int(coord["x"])
                y = int(coord["y"])
                # Get a copy of the original image, cropped to coords()
                image = pixmap.copy(x, y, w, h)
                # ToDo: How much of this is needed.
                # 1..4 was tcLeft, tcTop, tcRight, tcBottom in lua's DrawImage
                self.spriteMap[name][_type] = {
                    "handle": image,
                    "name": name,
                    "width": w,
                    "height": h,
                    "ox": x,
                    "oy": y,
                    "1": x / w,
                    "2": y / h,
                    "3": (x + w) / w,
                    "4": (y + h) / h,
                }

    # process_sprite_map

    def process_assets(self, sprite_list):
        """
        remap assets' contents into internal resource ids
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
                _result.height()
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

        # with open("temp/spriteMap.txt", "a") as f_out:
        #     pprint(self.spriteMap, f_out)

    # process_assets


def test(config: Config) -> None:
    tree = Tree(config)
    print(tree.version)


if __name__ == "__test__":
    test(Config(None, None))
