"""
TreeView Class

This class represents an instance of the Passive Tree for a given Build.
Multiple Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemizations, etc.)

A Tree instance is tied to a Version of the Tree as released by GGG and thus older Trees
need to be supported for backwards compatibility reason.

"""
from qdarktheme.qtpy.QtCore import QLineF, QRectF, Qt
from qdarktheme.qtpy.QtGui import QBrush, QColor, QPen, QPainter, QPixmap
from qdarktheme.qtpy.QtWidgets import QFrame, QGraphicsEllipseItem, QGraphicsScene, QGraphicsView

from constants import ColourCodes, class_backgrounds, Layers, PlayerClasses
from pob_config import Config, _debug

from tree_graphics_item import TreeGraphicsItem
from build import Build


class TreeView(QGraphicsView):
    def __init__(self, _win, _config: Config, _build: Build) -> None:
        """
        Initialize Treeview

        :param _win: pointer to MainWindow()
        :param _config: pointer to Config()
        :param _build: pointer to build()
        """
        super(TreeView, self).__init__()
        self.win = _win
        self.config = _config
        self.build = _build

        self.search_rings = []
        self.active_nodes = []
        self.active_lines = []

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
        # self.setBackgroundBrush(QBrush("#181818", Qt.SolidPattern))

        self._char_class_bkgnd_image = None
        self.fitInView(True, 0.1)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # Stop the drag icon being the default, which the above line would do
        self.viewport().setCursor(Qt.ArrowCursor)

        # add_tree_images needs to be before adding a margin
        self.add_tree_images(True)
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
        # _debug("tree_view: mousePressEvent")
        super(TreeView, self).mousePressEvent(event)
        # Stop hand cursor
        self.viewport().setCursor(Qt.ArrowCursor)

    # Inherited, don't change definition
    def mouseReleaseEvent(self, event) -> None:
        """
        Turn on or off a node if one is clicked on. Update node count appropriately.

        :param event: Internal event matrix.
        :return: N/A
        """
        # _debug("tree_view: mouseReleaseEvent")
        super(TreeView, self).mouseReleaseEvent(event)
        # Ensure hand cursor is gone (it's sneaky)
        self.viewport().setCursor(Qt.ArrowCursor)
        _item: TreeGraphicsItem = self.itemAt(event.pos())
        if _item and type(_item) == TreeGraphicsItem and _item.node_id != 0:
            if _item.node_id in self.build.current_spec.nodes:
                self.build.current_spec.nodes.remove(_item.node_id)
            else:
                self.build.current_spec.nodes.append(_item.node_id)
            self.add_tree_images()
            # count the new nodes ...
            self.build.count_allocated_nodes()
            # ... and display them
            self.win.display_number_node_points(-1)

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
        Changes for this Class() to deal with a PoB tree change.

        :param:  N/A
        :return: N/A
        """
        self.add_tree_images()
        self.refresh_search_rings()

    def refresh_search_rings(self):
        """
        clear and redraw search rings around nodes.

        :return: N/A
        """

        def add_circle(_image: TreeGraphicsItem, colour, line_width=10, z_value=10):
            """
            Draw a circle around an overlay image
            :param _image: TreegraphicsItem: The image to have a circle drawn around it.
            :param colour: ColourCodes.value: yep.
            :param z_value: Layers: which layer shall we draw it.
            :param line_width: int: yep.
            :return: a reference to the circle.
            """
            _circle = QGraphicsEllipseItem(
                _image.pos().x() + _image.offset().x() - line_width / 2,
                _image.pos().y() + _image.offset().y() - line_width / 2,
                _image.width + line_width,
                _image.height + line_width,
            )
            _circle.setPen(QPen(QColor(colour), line_width, Qt.SolidLine))
            _circle.setZValue(z_value)
            _circle.setStartAngle(90 * 16)
            _circle.setSpanAngle(90 * 16)

            return _circle
            # add_circle

        # print(f"refresh_search_rings: '{self.build.search_text}', {len(self.search_rings)}, {len(self._scene.items())}")
        for item in self.search_rings:
            self._scene.removeItem(item)
            del item
        self.search_rings.clear()
        if self.build.search_text == "":
            return
        # We only put search rings around a node's overlay, not the node itself.
        # The stops the ring appearing under or over the node's overlay.
        for image in self.build.current_tree.graphics_items:
            if image.node_isoverlay and self.build.search_text in image.build_tooltip():
                _circle = add_circle(image, Qt.yellow, 12)
                self.search_rings.append(_circle)
                self._scene.addItem(_circle)

    def add_tree_images(self, full_clear=False):
        """
        Used when swapping tree's in a build.
        It will remove all assets, including selected nodes and connecting lines and present an empty tree.
        It is expected another function will be called to created selected nodes and connecting lines.
        :param: full_clear: bool: If set, delete the tree images also. If not set, only delete the active images
        :return: N/A
        """

        # leave the print in till we have everything working.
        # It is what tells us how often the assets are being redrawn.
        _debug(f"add_tree_images, full_clear={full_clear}")
        if self.build.current_tree is None:
            return

        tree = self.build.current_tree
        # do not use self.clear as it deletes the graphics assets from memory
        if full_clear:
            for item in self.items():
                self._scene.removeItem(item)
            # inactive tree assets
            for image in tree.graphics_items:
                self._scene.addItem(image)

            # inactive tree lines
            for line in tree.lines:
                self._scene.addItem(line)

            # Hack to draw class background art, the position data doesn't seem to be in the tree JSON yet.
            if self.build.current_class != PlayerClasses.SCION:
                bkgnd = class_backgrounds[self.build.current_class]
                self._char_class_bkgnd_image = self.add_picture(
                    QPixmap(f":/Art/TreeData/{bkgnd['n']}"),
                    bkgnd["x"],
                    bkgnd["y"],
                    Layers.backgrounds,
                )
                self._char_class_bkgnd_image.filename = bkgnd["n"]
        else:
            # don't delete the images for the nodes as they are owned by the relevant Tree() class.
            for item in self.active_nodes:
                self._scene.removeItem(item)
            for item in self.active_lines:
                self._scene.removeItem(item)
                del item
        self.active_nodes.clear()
        self.active_lines.clear()

        # loop though active nodes and add them and their connecting lines
        active_nodes = self.build.current_spec.nodes
        for node_id in active_nodes:
            node = tree.nodes.get(node_id, None)
            if node is not None:
                if node.active_image is not None:
                    self.active_nodes.append(node.active_image)
                    self.active_nodes.append(node.active_overlay_image)
                    self._scene.addItem(node.active_image)
                    self._scene.addItem(node.active_overlay_image)
                if node.masteryEffects:
                    print(node.id, node.activeEffectImage)
                    print(node.id, node.active_image)
                    # image = node.masterySprites["activeEffectImage"]
                    self.active_nodes.append(node.activeEffectImage)
                    self._scene.addItem(node.activeEffectImage)

                # Draw active lines
                if node.type not in ("ClassStart", "Mastery"):
                    in_out_nodes = []
                    for other_node_id in set(node.nodes_out + node.nodes_in) & set(active_nodes):
                        other_node = tree.nodes.get(other_node_id, None)
                        if (
                            other_node is not None
                            and other_node.type not in ("ClassStart", "Mastery")
                            # This stops lines crossing out of the Ascendency circles
                            and node.ascendancyName == other_node.ascendancyName
                        ):
                            in_out_nodes.append(other_node)

                    for other_node in in_out_nodes:
                        line = self.scene().addLine(
                            node.x,
                            node.y,
                            other_node.x,
                            other_node.y,
                            QPen(QColor(ColourCodes.CURRENCY.value), 4),
                        )
                        line.setAcceptTouchEvents(False)
                        line.setAcceptHoverEvents(False)
                        line.setZValue(Layers.connectors)
                        self.active_lines.append(line)

        # Darken Ascendancy backgrouds.
        current_ascendancy = f"Classes{self.build.ascendClassName}"
        for item in tree.ascendancy_group_list:
            # Chieftain is brighter than the rest
            dim = item.filename == "ClassesChieftain" and 0.3 or 0.5
            if current_ascendancy == item.filename:
                item.setOpacity(1.0)
            else:
                item.setOpacity(dim)
        # add_tree_images
