"""
TreeView Class

This class represents an instance of the Passive Tree for a given Build.
Multiple Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemizations, etc.)

A Tree instance is tied to a Version of the Tree as released by GGG and thus older Trees
need to be supported for backwards compatibility reason.

"""
from qdarktheme.qtpy.QtCore import QRectF, Qt
from qdarktheme.qtpy.QtGui import QBrush, QColor, QPen, QPainter, QPixmap
from qdarktheme.qtpy.QtWidgets import QFrame, QGraphicsEllipseItem, QGraphicsScene, QGraphicsView

from constants import PlayerClasses, class_backgrounds, Layers
from pob_config import Config, _debug

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
        # set a background of black this stops the tree looking ugly when 'light' theme is selected
        self.setBackgroundBrush(QBrush(Qt.black, Qt.SolidPattern))

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
        # if _item:
        #     _debug("tree_view: mousePressEvent1", _item.node_id, _item.filename)
        if _item and _item.node_id != 0:
            # _debug("tree_view: mousePressEvent2", self.build.current_spec.nodes)
            if _item.node_id in self.build.current_spec.nodes:
                self.build.current_spec.nodes.remove(_item.node_id)
            else:
                self.build.current_spec.nodes.append(_item.node_id)
            # _debug("tree_view: mousePressEvent3", self.build.current_spec.nodes)
            self.add_tree_images()

    # Inherited, don't change definition
    def mouseReleaseEvent(self, event) -> None:
        """
        Override the GraphicsView drag cursor
        :param event: Internal event matrix
        :return: N/A
        """
        # _debug("tree_view: mouseReleaseEvent")
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
            print(f"tree_view.add_picture called with information. pixmap: {pixmap},  x:{x}, y: {y}")
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

        def add_circle(_image: TreeGraphicsItem, colour, line_width=10, z_value=10):
            """
            Draw a circle around an overlay image
            :param _image: TreegraphicsItem
            :param colour: yep
            :param z_value: which layer shall we draw it
            :param line_width: yep
            :return: a reference to the circle
            """
            _circle = QGraphicsEllipseItem(
                _image.pos().x() + _image.offset().x() - line_width / 2,
                _image.pos().y() + _image.offset().y() - line_width / 2,
                _image.width + line_width,
                _image.height + line_width,
            )
            _circle.setPen(QPen(QColor(colour), line_width, Qt.SolidLine))
            _circle.setZValue(z_value)
            return _circle

        # leave the print in till we have everything working.
        # It is what tells us how often the assets are being redrawn.
        _debug("add_tree_images")
        if self.build.current_tree is None:
            return

        tree = self.build.current_tree

        # ToDo: Only remove items if we change tree versions
        #  else wise just remove the selected nodes/connectors and readd new ones (separate function)
        # do not use self.clear as it deletes the graphics assets from memory
        for item in self.items():
            self._scene.removeItem(item)

        # isAlloc = False
        for node_id in tree.nodes:
            n = tree.nodes[str(node_id)]

        for node_id in self.build.current_spec.nodes:
            n = tree.nodes.get(str(node_id), None)
            if n is not None and n.active_image is not None:
                self._scene.addItem(n.active_image)
                self._scene.addItem(n.active_overlay_image)

        for image in tree.graphics_items:
            self._scene.addItem(image)
            # Search indicator
            if (
                self.build.search_text
                and image.node_isoverlay
                and (self.build.search_text in image.node_name or self.build.search_text in image.node_sd)
            ):
                self._scene.addItem(add_circle(image, Qt.yellow, 12))

        # Hack to draw class background art, the position data doesn't seem to be in the tree JSON yet
        if self.build.current_class != PlayerClasses.SCION:
            bkgnd = class_backgrounds[self.build.current_class]
            self._char_class_bkgnd_image = self.add_picture(
                QPixmap(f":/Art/TreeData/{bkgnd['n']}"),
                bkgnd["x"],
                bkgnd["y"],
                Layers.backgrounds,
            )
            self._char_class_bkgnd_image.filename = bkgnd["n"]

    # add_tree_images
