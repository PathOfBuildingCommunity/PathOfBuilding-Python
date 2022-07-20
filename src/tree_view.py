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
    QMouseEvent,
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
from pob_config import Config, ColourCodes, PlayerClasses, class_backgrounds, global_scale_factor
from tree import Tree
from tree_graphics_item import TreeGraphicsItem


class TreeView(QGraphicsView):
    def __init__(self, _config: Config, _tree: Tree) -> None:
        super(TreeView, self).__init__()
        self.config = _config
        self.tree = _tree

        self.ui = None
        self._scene = QGraphicsScene(self.tree.size)
        # self._scene = QGraphicsScene(
        #     self, self.tree.min_x, self.tree.min_y, self.tree.max_x, self.tree.max_y
        # )

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
            # # limit the amount it moves.
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
        else:
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

    def add_picture(self, pixmap, x, y, z=0, selectable=True):
        """
        Add a picture represented. If a pixmap, then ox,oy must be used
        :param pixmap: string or pixmap to be added
        :param x, y: it's position in the scene
        :param z: which layer to use:  -2: background, -1: connectors, 0: inactive,
                                        1: active (overwriting its inactive equivalent ???)
        :param selectable: Can the user select this.
        :return: ptr to the created TreeGraphicsItem
        """
        image = TreeGraphicsItem(self.config, pixmap, z, selectable)
        image.setPos(x, y)
        self._scene.addItem(image)
        return image

    def switch_class(self, _class):
        # if self.tree.char_class != _class
        # Alert for wiping your tree
        self.tree.char_class = _class
        self.add_tree_images()

    def add_tree_images(self):
        """
        Used when swapping tree's in a build.
        It will remove all assets, including selected nodes and connecting lines and present an empty tree
        It is expected another function will be called to created selected nodes and connecting lines
        :return:
        """
        if self.tree is None:
            return

        def renderGroup(self, group):
            if group.get("ascendancyName", None) is not None:
                if group.get("isAscendancyStart", None) is not None:
                    # This is the ascendancy circles around the outside of the tree
                    # print(group["ascendancyName"])
                    name=f"center{group['ascendancyName']}"
                    self.add_picture(
                        self.tree.assets[f"Classes{group['ascendancyName']}"],
                        group["x"],
                        group["y"],
                        -2,
                        False,
                    )
            elif group["oo"].get(3, None) is not None:
                self.add_picture(
                    self.tree.assets["GroupBackgroundLargeHalfAlt"],
                    group["x"],
                    group["y"],
                    -2,
                    False,
                )
            elif group["oo"].get(2, None) is not None:
                self.add_picture(
                    self.tree.assets["GroupBackgroundMediumAlt"],
                    group["x"],
                    group["y"],
                    -2,
                    False,
                )
            elif group["oo"].get(1, None) is not None:
                self.add_picture(
                    self.tree.assets["GroupBackgroundSmallAlt"],
                    group["x"],
                    group["y"],
                    -2,
                    False,
                )

        for item in self.items():
            self._scene.removeItem(item)

        # Hack to draw class background art, the position data doesn't seem to be in the tree JSON yet
        image = None
        if self.tree.char_class != PlayerClasses.SCION:
            c = class_backgrounds[self.tree.char_class]
            self._char_class_bkgnd_image = self.add_picture(
                self.tree.assets[c["n"]], c["x"], c["y"], -2, False
            )

        # Draw the group backgrounds
        for g in self.tree.groups:
            group = self.tree.groups[g]
            is_proxy = group.get("isProxy", False)
            is_ascendancy_start = group.get("isAscendancyStart", False)
            ascendancy_name = group.get("ascendancyName", None)
            # if not is_proxy and is_ascendancy_start and ascendancy_name is not None:
            if not group.get("isProxy", False):
                renderGroup(self, group)

        for image in self.tree.graphics_items:
            self._scene.addItem(image)

        for n in self.tree.nodes:
            # print(n)
            node = self.tree.nodes[n]
            _type = node.type
            # keystoneActive, mastery, normalActive, notableActive
            # print(f"{n}: {_type}: {node.sprites}")
            # temporary
            hoverNode = None
            # isAlloc = True
            isAlloc = False
            state = "unalloc" # could also be Alloc and Path
            overlay = ""
            base = None
            if _type == "ClassStart":
                overlay = isAlloc and node.startArt or "PSStartNodeBackgroundInactive"
                # print(f"{n}: {_type}: {overlay}")
            elif _type == "AscendClassStart":
                overlay = "AscendancyMiddle"
            else:
                if _type == "Socket":
                    pass
                elif _type == "Mastery":
                    # This is the icon that appears in the center of many groups
                    if node.masteryEffects:
                        if isAlloc:
                            base = node.masterySprites["activeIcon"]["masteryActiveSelected"]
                            effect = node.masterySprites["activeEffectImage"]["masteryActiveEffect"]
                        elif node == hoverNode:
                            base = node.masterySprites["inactiveIcon"]["masteryConnected"]
                        else:
                            base = node.masterySprites["inactiveIcon"]["masteryInactive"]
                    else:
                        base = node.sprites["mastery"]
                else:
                    # Normal node (includes keystones and notables)
                    base = node.sprites[f"{_type.lower()}{(isAlloc and 'Active' or 'Inactive')}"]
                    overlay = node.overlay[f"{state}{node.ascendancyName and 'Ascend' or ''}{node.isBlighted and 'Blighted' or ''}"]
            # print(f"base: {base}")
            # print(f"overlay: {overlay}")

            if base is not None:
                # print(f"{n}: {_type}: {base}")
                pixmap = base.get("handle", None)
                if pixmap is not None:
                    image = self.add_picture(pixmap, node.x, node.y, 1, True)
                    image.width = base["width"]
                    image.height = base["height"]
                    image.filename = node.name
                    # image.filename = base["name"]
                    image.data = base["name"]
