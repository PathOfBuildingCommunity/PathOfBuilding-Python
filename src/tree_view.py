"""
TreeView Class

This class represents an instance of the Passive Tree for a given Build.
Multiple Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemizations, etc.)

A Tree instance is tied to a Version of the Tree as released by GGG and thus older Trees
need to be supported for backwards compatibility reason.

"""
from qdarktheme.qtpy.QtCore import QRectF, Qt
from qdarktheme.qtpy.QtGui import QColor, QPen, QPainter
from qdarktheme.qtpy.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
)

# from constants import *
# from constants import _VERSION
from pob_config import *

from tree_graphics_item import TreeGraphicsItem
from build import Build


class TreeView(QGraphicsView):
    def __init__(self, _config: Config, _build: Build) -> None:
        super(TreeView, self).__init__()
        self.config = _config
        self.build = _build

        self.ui = None
        self._scene = QGraphicsScene()

        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self._char_class_bkgnd_image = None
        self.add_tree_images()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.drag = False
        self.start_pos = None
        self.fitInView(True, 0.1)

        self.viewport().setCursor(Qt.ArrowCursor)
        # add a margin to make panning the view seem more comfortable
        rect = self.sceneRect()
        rect.adjust(-1000.0, -1000.0, 1000.0, 1000.0)
        self.setSceneRect(rect)

    # Inherited, don't change definition
    def wheelEvent(self, event):
        """
        Zoom in and out. Attempt to limit zoom
        :param event:
        :return:
        """
        if event.angleDelta().y() > 0:
            factor = 1.25
        else:
            factor = 0.8
        self.fitInView(True, factor)
        event.accept()

    # Inherited, don't change definition
    def enterEvent(self, event) -> None:
        """
        Override the GraphicsView drag cursor
        :param event: Internal event matrix
        :return: N/A
        """
        super(TreeView, self).enterEvent(event)
        self.viewport().setCursor(Qt.ArrowCursor)

    # Inherited, don't change definition
    def mousePressEvent(self, event) -> None:
        """
        Override the GraphicsView drag cursor
        :param event: Internal event matrix
        :return: N/A
        """
        super(TreeView, self).mousePressEvent(event)
        # ToDo : Do we want to allow the grap cursor or just keep the arrow ?
        # self.viewport().setCursor(Qt.ArrowCursor)
        _item: TreeGraphicsItem = self.itemAt(event.pos())
        if _item:
            print("tree_view: mouseReleaseEvent", _item.node_id, _item.filename)
        if _item and _item.node_id != 0:
            print(self.build.current_spec.nodes)
            if _item.node_id in self.build.current_spec.nodes:
                self.build.current_spec.nodes.remove(_item.node_id)
            else:
                self.build.current_spec.nodes.append(_item.node_id)
            self.add_tree_images()

    # Inherited, don't change definition
    def mouseReleaseEvent(self, event) -> None:
        """
        Override the GraphicsView drag cursor
        :param event: Internal event matrix
        :return: N/A
        """
        print("tree_view: mouseReleaseEvent")
        super(TreeView, self).mouseReleaseEvent(event)
        self.viewport().setCursor(Qt.ArrowCursor)

    # Function Overridden
    def fitInView(self, scale=True, factor=None):
        """
        Part of the zoom facility
        :param scale: Not used.
        :param factor: Scale factor.
        :return: N/A
        """
        current_scale_factor = self.transform().m11()
        # Limit Zoom by reversing the factor if needed
        if current_scale_factor > 1.0:
            factor = 0.8
        if current_scale_factor < 0.08:
            factor = 1.25
        if factor is None:
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
        else:
            self.scale(factor, factor)

    def add_picture(self, pixmap, x, y, z=0, selectable=False):
        """
        Add a picture or pixmap
        :param pixmap: string or pixmap to be added
        :param x: it's position in the scene
        :param y: it's position in the scene
        :param z: which layer to use:  -2: background, -1: connectors, 0: inactive,
                                        1: sprite overlay
                                        1: active (overwriting its inactive equivalent ???)
        :param selectable: Can the user select this.
        :return: ptr to the created TreeGraphicsItem
        """
        if pixmap is None or pixmap == "":
            print(
                f"tree_view.add_picture called with information. pixmap: {pixmap},  x:{x}, y: {y}"
            )
            return None
        image = TreeGraphicsItem(self.config, pixmap, z, selectable)
        image.setPos(x, y)
        self._scene.addItem(image)
        return image

    def switch_class(self, _class):
        """
        Changes for this Class() to deal with a PoB class change
        :param _class:
        :return: N/A
        """
        # if self.build.current_tree.char_class != _class
        # Alert for wiping your tree
        # self.build.current_tree.char_class = _class
        # self.build.current_class = _class
        return True

    def switch_tree(self):
        """
        Changes for this Class() to deal with a PoB tree change
        :param:  N/A
        :return: N/A
        """
        self.add_tree_images()

    def add_tree_images(self):
        """
        Used when swapping tree's in a build.
        It will remove all assets, including selected nodes and connecting lines and present an empty tree
        It is expected another function will be called to created selected nodes and connecting lines
        :return: N/A
        """

        def add_circle(_image: TreeGraphicsItem, colour, z_value, line_width=15):
            _circle = QGraphicsEllipseItem(
                _image.pos().x() - 10,
                _image.pos().y() - 10,
                _image.width + 25,
                _image.height + 25,
            )
            _circle.setPen(QPen(QColor(colour), line_width, Qt.SolidLine))
            _circle.setZValue(z_value)
            return _circle

        if self.build.current_tree is None:
            return

        tree = self.build.current_tree

        def renderGroup(self, _group, g):
            __image = None
            scale = 1
            if _group.get("ascendancyName") != "":
                _name = _group["ascendancyName"]
                # ToDo: Accommodate a bug that makes Chieftain disappear
                if _name == "Chieftain":
                    _group["isAscendancyStart"] = True
                if _group.get("isAscendancyStart", False):
                    # This is the ascendancy circles around the outside of the tree
                    # Ascendant position in the json is good, everyone else needs hard coding
                    if _name == "Ascendant":
                        _x, _y = _group["x"], _group["y"]
                    else:
                        _x = ascendancy_positions[_name]["x"]
                        _y = ascendancy_positions[_name]["y"]

                    # add the picture and shift it by half itself to line up with the nodes
                    __image = self.add_picture(
                        tree.spriteMap[f"Classes{_name}"]["handle"],
                        _x,
                        _y,
                        Layers.backgrounds,
                    )
                    __image.setScale(2.5 / global_scale_factor)
                    __image.setPos(
                        _x - (__image.width / 2),
                        _y - (__image.height / 2),
                    )
                    __image.filename = f"Classes{_name}"
                    # Darken if this Ascendancy is not the chosen one
                    #  Chieftain is brigher than the rest
                    if _name != self.build.ascendClassName:
                        __image.setOpacity(_name == "Chieftain" and 0.2 or 0.4)

            # Large background
            elif _group["oo"].get(3, False):
                __image = self.add_picture(
                    tree.spriteMap["GroupBackgroundLargeHalfAlt"]["handle"],
                    _group["x"],
                    _group["y"],
                    Layers.group,
                )
                __image.filename = f"{g} GroupBackgroundLargeHalfAlt"
                __image.setScale(1.9 / global_scale_factor)
                _group["x1"] = (
                    _group["x"] - (__image.width / 2) + (34 / global_scale_factor)
                )
                _group["y1"] = (
                    _group["y"] - (__image.height / 2) + (34 / global_scale_factor)
                )
                __image.setPos(_group["x1"], _group["y1"])

            # Medium background
            elif _group["oo"].get(2, False):
                __image = self.add_picture(
                    tree.spriteMap["GroupBackgroundMediumAlt"]["handle"],
                    _group["x"],
                    _group["y"],
                    Layers.group,
                )
                __image.filename = f"{g} GroupBackgroundMediumAlt"
                __image.setScale(1.9 / global_scale_factor)
                _group["x1"] = (
                    _group["x"] - (__image.width / 2) + (32 / global_scale_factor)
                )
                _group["y1"] = (
                    _group["y"] - (__image.height / 2) + (32 / global_scale_factor)
                )
                __image.setPos(_group["x1"], _group["y1"])

            # Small background
            elif group["oo"].get(1, False):
                __image = self.add_picture(
                    tree.spriteMap["GroupBackgroundSmallAlt"]["handle"],
                    _group["x"],
                    _group["y"],
                    Layers.group,
                )
                __image.filename = f"{g} GroupBackgroundSmallAlt"
                __image.setScale(1.9 / global_scale_factor)
                _group["x1"] = (
                    _group["x"] - (__image.width / 2) + (44 / global_scale_factor)
                )
                _group["y1"] = (
                    _group["y"] - (__image.height / 2) + (44 / global_scale_factor)
                )
                __image.setPos(_group["x1"], _group["y1"])

        self._scene.clear()
        # ToDo: Only clear items if we change tree versions
        #  else wise just remove the selected nodes/connectors and readd new ones (separate function)
        # for item in self.items():
        #     self._scene.removeItem(item)
        # ToDo: all this needs to be moved to the tree Class, so then this line will work
        for image in tree.graphics_items:
            self._scene.addItem(image)

        # Hack to draw class background art, the position data doesn't seem to be in the tree JSON yet
        if self.build.current_class != PlayerClasses.SCION:
            bkgnd = class_backgrounds[self.build.current_class]
            self._char_class_bkgnd_image = self.add_picture(
                tree.spriteMap[bkgnd["n"]]["handle"],
                bkgnd["x"],
                bkgnd["y"],
                Layers.backgrounds,
            )
            self._char_class_bkgnd_image.filename = bkgnd["n"]

        # Add the group backgrounds
        for g in tree.groups:
            group = tree.groups[g]
            if not group.get("isProxy", False):
                renderGroup(self, group, g)

        for n in tree.nodes:
            node = tree.nodes[n]
            # Skip nodes with no group id. They appear to be clusters at the moment (2022-07-24)
            if node.g < 1:
                continue
            group = tree.groups[str(node.g)]
            _type = (
                node.type
            )  # eg: keystoneActive, mastery, normalActive, notableActive
            # ToDo: temporary
            hoverNode = None
            state = "unalloc"  # could also be Alloc and Path
            # ToDo: temporary

            isAlloc = False
            if self.build.current_spec.nodes:
                isAlloc = n in self.build.current_spec.nodes

            overlay = ""
            base = None
            if _type == "ClassStart":
                overlay = isAlloc and node.startArt or "PSStartNodeBackgroundInactive"
                node.x = class_centres[PlayerClasses(node.classStartIndex)]["x"]
                node.y = class_centres[PlayerClasses(node.classStartIndex)]["y"]
            elif _type == "AscendClassStart":
                overlay = "AscendancyMiddle"
            else:
                if _type == "Socket":
                    # ToDo: Sockets
                    pass
                elif _type == "Mastery":
                    # This is the icon that appears in the center of many groups
                    if node.masteryEffects:
                        if isAlloc:
                            base = node.masterySprites["activeIcon"][
                                "masteryActiveSelected"
                            ]
                            effect = node.masterySprites["activeEffectImage"][
                                "masteryActiveEffect"
                            ]
                        elif node == hoverNode:
                            base = node.masterySprites["inactiveIcon"][
                                "masteryConnected"
                            ]
                        else:
                            base = node.masterySprites["inactiveIcon"][
                                "masteryInactive"
                            ]
                        node.x = group["x"] - (54 / global_scale_factor)
                        node.y = group["y"] - (54 / global_scale_factor)
                    else:
                        base = node.sprites["mastery"]
                        node.x = group["x"] - (54 / global_scale_factor)
                        node.y = group["y"] - (54 / global_scale_factor)
                else:
                    # Normal node (includes keystones and notables)
                    base = node.sprites.get(
                        f"{_type.lower()}{(isAlloc and 'Active' or 'Inactive')}", None
                    )
                    overlay = node.overlay.get(
                        f"{state}{node.ascendancyName and 'Ascend' or ''}{node.isBlighted and 'Blighted' or ''}",
                        "",
                    )

            if base:
                pixmap = base.get("handle", None)
                if pixmap is not None:
                    _image = self.add_picture(
                        pixmap, node.x, node.y, Layers.inactive, True
                    )
                    _image.filename = node.name
                    _image.data = node.sd
                    _image.node_id = n
                    # Search indicator
                    if self.build.search_text and (
                        self.build.search_text in node.name
                        or self.build.search_text in node.sd
                    ):
                        self._scene.addItem(add_circle(_image, Qt.darkRed, 10, 8))

            """'overlay': {'alloc': 'AscendancyFrameLargeAllocated',
                        'artWidth': '65',
                        'path': 'AscendancyFrameLargeCanAllocate',
                        'rsq': 7473.602500000001,
                        'size': 86.45,
                        'unalloc': 'AscendancyFrameLargeNormal'},"""
            if overlay != "":
                _overlay = tree.spriteMap.get(overlay, None)
                _layer = (
                    _type == "Notable" and Layers.key_overlays or Layers.small_overlays
                )
                if _overlay is not None:
                    pixmap = _overlay.get("handle", None)
                    if pixmap is not None:
                        # image = self.add_picture(pixmap, node.x, node.y, _layer)
                        image = self.add_picture(pixmap, node.x - 7, node.y - 7, _layer)
                        image.filename = node.name
                        # Add the node id to the overlay as it sometimes get's clciked instead of the centre graphic
                        image.node_id = n

    # add_tree_images
