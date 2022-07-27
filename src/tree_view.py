"""
TreeView Class

This class represents an instance of the Passive Tree for a given Build.
Multiple Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemizations, etc.)

A Tree instance is tied to a Version of the Tree as released by GGG and thus older Trees
need to be supported for backwards compatibility reason.

"""
import os, re, json
from pprint import pprint
from pathlib import Path
from qdarktheme.qtpy.QtCore import (
    QSize,
    QDir,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    Qt,
    Slot,
    QCoreApplication,
)
from qdarktheme.qtpy.QtGui import (
    QAction,
    QActionGroup,
    QBrush,
    QColor,
    QCursor,
    QDrag,
    QFont,
    QIcon,
    QImage,
    QMouseEvent,
    QPen,
    QPixmap,
    QPainter,
)
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import pob_file, ui_utils
from pob_config import *

# from pob_config import (
#     Config,
#     ColourCodes,
#     PlayerClasses,
#     class_backgrounds,
#     global_scale_factor,
# )
from tree import Tree
from tree_graphics_item import TreeGraphicsItem
from build import Build


class TreeView(QGraphicsView):
    def __init__(self, _config: Config, _build: Build) -> None:
        super(TreeView, self).__init__()
        self.config = _config
        self.build = _build

        self.ui = None
        self._scene = QGraphicsScene(self.build.current_tree.size)

        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self._char_class_bkgnd_image = None
        self.add_tree_images()
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.drag = False
        self.start_pos = None
        self.fitInView(True, 0.1)

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
    def mousePressEvent(self, event) -> None:
        """
        Hack to allow a normal mouse pointer until the mouse is held down
        This allows drag
        :param event: Std param
        :return: N/A
        """
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        # print("TreeView.mousePressEvent")
        super(TreeView, self).mousePressEvent(event)
        if self.itemAt(event.pos()) is None:
            # self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.ClosedHandCursor)
            self.drag = True
            self.start_pos = event.pos()

    # Inherited, don't change definition
    def mouseMoveEvent(self, event) -> None:
        """
        Drag the scene (aka pan)
        limit the amount it moves to stop zoom "creep" (speeding up of zoom the longer it happens)
        :param event:
        :return:
        """
        if self.start_pos is not None:
            delta = self.start_pos - event.pos()
            rect = self.scene().sceneRect()
            # limit the amount it moves.
            # !!!! This might need adjusting to account for zoom (0.08 = out, 0.5 = in)
            # x = delta.x()
            # y = delta.y()
            # # print(f"a: {delta}, {x}, {y}")
            # if x >= 0:
            #     x = min(x, 20)
            # else:
            #     x = max(x, -20)
            # if y >= 0:
            #     y = min(y, 20)
            # else:
            #     y = max(y, -20)
            # delta = QPoint(x, y)
            # print(f"b: {delta}, {x}, {y}")

            # adjust the viewing rectangle
            rect.setTopLeft(rect.topLeft() + delta)
            rect.setBottomRight(rect.bottomRight() + delta)
            self.scene().setSceneRect(rect)
            self.updateSceneRect(rect)
        # else:
        super(TreeView, self).mouseMoveEvent(event)

    # Inherited, don't change definition
    def mouseReleaseEvent(self, event) -> None:
        """
        Hack to allow a normal mouse pointer until the mouse is held down
        This releases drag
        :param event: Std param
        :return: N/A
        """
        # print("TreeView.mouseReleaseEvent")
        if self.itemAt(event.pos()) is None:
            # self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.ArrowCursor)
            self.drag = False
            self.start_pos = None
        super(TreeView, self).mouseReleaseEvent(event)

    def fitInView(self, scale=True, factor=None):
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        if factor is None:
            self.scale(1 / unity.width(), 1 / unity.height())
        else:
            self.scale(factor, factor)

    def add_picture(self, pixmap, x, y, z=0, selectable=False):
        """
        Add a picture or pixmap
        :param pixmap: string or pixmap to be added
        :param x, y: it's position in the scene
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
        self.add_tree_images()

    def switch_tree(self):
        """
        Changes for this Class() to deal with a PoB tree change
        :param  N/A
        :return: N/A
        """
        self.add_tree_images()

    def add_tree_images(self):
        """
        Used when swapping tree's in a build.
        It will remove all assets, including selected nodes and connecting lines and present an empty tree
        It is expected another function will be called to created selected nodes and connecting lines
        :return:
        """
        if self.build.current_tree is None:
            return

        tree = self.build.current_tree

        def renderGroup(self, _group, g):
            _image = None
            scale = 1
            if _group.get("ascendancyName", None) is not None:
                _name = _group["ascendancyName"]
                # ToDo: Accommodate a bug that makes Chieftain disappear
                if _name == "Chieftain":
                    _group["isAscendancyStart"] = True
                if _group.get("isAscendancyStart", False):
                    # This is the ascendancy circles around the outside of the tree
                    # Ascendant position in the json is good, everyone is need hard coding
                    if _name == "Ascendant":
                        _x, _y = _group["x"], _group["y"]
                    else:
                        _x, _y = (
                            ascendancy_positions[_name]["x"],
                            ascendancy_positions[_name]["y"],
                        )

                    # add the picture and shift it by half itself to line up with the nodes
                    _image = self.add_picture(
                        tree.spriteMap[f"Classes{_name}"]["handle"],
                        _x,
                        _y,
                        Layers.backgrounds,
                    )
                    _image.setScale(2.5 / global_scale_factor)
                    _image.setPos(
                        _x - (_image.width / 2),
                        _y - (_image.height / 2),
                    )
                    _image.filename = f"Classes{_name}"
                    # Add a circle if this Ascendancy is the chosen one
                    # ToDo: find a way to darken and lighten images
                    if _name == self.build.ascendClassName:
                        _circle = QGraphicsEllipseItem(
                            _image.pos().x() - 10,
                            _image.pos().y() - 10,
                            _image.width + 10,
                            _image.height + 10,
                        )
                        _circle.setPen(QPen(QColor(Qt.darkGreen), 15, Qt.SolidLine))
                        _circle.setZValue(Layers.group)
                        self._scene.addItem(_circle)

            elif _group["oo"].get(3, False):
                _image = self.add_picture(
                    tree.spriteMap["GroupBackgroundLargeHalfAlt"]["handle"],
                    _group["x"],
                    _group["y"],
                    Layers.group,
                )
                _image.filename = f"{g} GroupBackgroundLargeHalfAlt"
                _image.setScale(1.9 / global_scale_factor)
                _image.setPos(
                    _group["x"] - (_image.width / 2), _group["y"] - (_image.height / 2)
                )
            elif _group["oo"].get(2, False):
                _image = self.add_picture(
                    tree.spriteMap["GroupBackgroundMediumAlt"]["handle"],
                    _group["x"],
                    _group["y"],
                    Layers.group,
                )
                _image.filename = f"{g} GroupBackgroundMediumAlt"
                _image.setScale(1.9 / global_scale_factor)
                _image.setPos(
                    _group["x"] - (_image.width / 2), _group["y"] - (_image.height / 2)
                )
            elif group["oo"].get(1, False):
                _image = self.add_picture(
                    tree.spriteMap["GroupBackgroundSmallAlt"]["handle"],
                    _group["x"],
                    _group["y"],
                    Layers.group,
                )
                _image.filename = f"{g} GroupBackgroundSmallAlt"
                _image.setScale(1.9 / global_scale_factor)
                _image.setPos(
                    _group["x"] - (_image.width / 2), _group["y"] - (_image.height / 2)
                )

        self._scene.clear()
        # ToDo: Only clear items if we change tree versions
        #  else wise just remove the selected nodes/connectors and readd new ones (separate function)
        # for item in self.items():
        #     self._scene.removeItem(item)
        # print("tree.graphics_items", len(tree.graphics_items))
        # ToDo: all this needs to be moved to the tree Class, so then this line will work
        for image in tree.graphics_items:
            self._scene.addItem(image)

        # Hack to draw class background art, the position data doesn't seem to be in the tree JSON yet
        image = None
        if self.build.current_class != PlayerClasses.SCION:
            print(self.build.current_class, type(self.build.current_class))
            bkgnd = class_backgrounds[self.build.current_class]
            print(bkgnd)
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
            # print(n)
            node = tree.nodes[n]
            # Skip nodes with no group id. They appear to be clusters at the moment (2022-07-24)
            if node.g < 1:
                continue
            group = tree.groups[str(node.g)]
            _type = (
                node.type
            )  # eg: keystoneActive, mastery, normalActive, notableActive
            # print(f"{n}: {_type}: {node.sprites}")
            # ToDo: temporary
            hoverNode = None
            state = "unalloc"  # could also be Alloc and Path

            # ToDo: temporary
            isAlloc = False
            if self.build.current_spec.nodes is not None:
                isAlloc = n in self.build.current_spec.nodes

            overlay = ""
            base = None
            if _type == "ClassStart":
                overlay = isAlloc and node.startArt or "PSStartNodeBackgroundInactive"
                # node.x, node.y = group["x"], group["y"]
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
                    else:
                        base = node.sprites["mastery"]
                        node.x = group["x"]
                        node.y = group["y"]
                else:
                    # Normal node (includes keystones and notables)
                    base = node.sprites.get(
                        f"{_type.lower()}{(isAlloc and 'Active' or 'Inactive')}", None
                    )
                    overlay = node.overlay.get(
                        f"{state}{node.ascendancyName and 'Ascend' or ''}{node.isBlighted and 'Blighted' or ''}",
                        "",
                    )

            if base is not None:
                if n == "24704":
                    print(n, node)
                # print(f"{n}: {_type}: {base}")
                pixmap = base.get("handle", None)
                if pixmap is not None:
                    image = self.add_picture(
                        pixmap, node.x, node.y, Layers.inactive, True
                    )
                    image.filename = f"{n}, {node.name}"
                    image.data = base["name"]

            """'overlay': {'alloc': 'AscendancyFrameLargeAllocated',
                        'artWidth': '65',
                        'path': 'AscendancyFrameLargeCanAllocate',
                        'rsq': 7473.602500000001,
                        'size': 86.45,
                        'unalloc': 'AscendancyFrameLargeNormal'},"""
            if overlay != "":
                # print(f"{n}: {_type}: {node.name}: {overlay}")
                _overlay = tree.spriteMap.get(overlay, None)
                _layer = (
                    _type == "Notable" and Layers.key_overlays or Layers.small_overlays
                )
                if _overlay is not None:
                    pixmap = _overlay.get("handle", None)
                    if pixmap is not None:
                        image = self.add_picture(pixmap, node.x - 8, node.y - 8, _layer)
                        image.filename = node.name
                        image.data = overlay

    # add_tree_images
