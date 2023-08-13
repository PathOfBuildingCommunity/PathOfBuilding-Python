"""
TreeItem Class

This class represents a graphical instance of one visual element of a Passive Tree for a given tree version.

"""
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem

from PoB.pob_config import Config
from widgets.ui_utils import html_colour_text


class TreeGraphicsItem(QGraphicsPixmapItem):
    def __init__(self, _config: Config, _image: str, node, z_value=0, selectable=False) -> None:
        super(TreeGraphicsItem, self).__init__()
        self.config = _config
        self.win = self.config.win
        self.filename = ""
        self.data = ""
        self.setPixmap(_image)
        if not type(_image) == QPixmap:
            self.filename = str(_image)
        self.width = self.pixmap().size().width()
        self.height = self.pixmap().size().height()
        self.setZValue(z_value)

        # ToDo: Do we need selectable ?
        # self.setFlag(QGraphicsItem.ItemIsSelectable, selectable)
        self.setAcceptTouchEvents(selectable)
        # ToDo: Temporary
        self.setAcceptHoverEvents(True)
        # self.setAcceptHoverEvents(selectable)

        # these are to have a fast way for a graphic item to identify its owner node's params. Used by mouse events
        # Maybe have just the node reference ?
        self.node_id = 0
        self.node_tooltip = ""
        self.node_sd = ""
        self.node_name = ""
        self.node_type = ""
        self.node_reminder = ""
        self.node_isoverlay = False
        self.node_classStartIndex = -1
        self.node_isAscendancyStart = False
        if node is not None:
            self.node_id = node.id
            self.node_sd = node.sd
            self.node_name = node.name
            self.node_type = node.type
            self.node_reminder = node.reminderText
            self.node_classStartIndex = node.classStartIndex
            self.node_isAscendancyStart = node.isAscendancyStart

    # Inherited, don't change definition
    def setScale(self, scale: int = 1):
        super(TreeGraphicsItem, self).setScale(scale)
        self.width *= scale
        self.height *= scale

    # Inherited, don't change definition
    def hoverEnterEvent(self, event):
        self.setToolTip(self.build_tooltip())

    def build_tooltip(self):
        """
        Build a tooltip from the node information and damage data (later).

        :return: str: the tooltip
        """
        tool_tip = self.node_name and f"{self.node_name}, {self.node_id}" or f"{self.node_id}"
        tool_tip += self.data and f", {self.data}" or ""
        if self.node_sd != "":
            for line in self.node_sd:
                tool_tip += f"\n{line}"
        tool_tip += self.node_reminder and f"\n{self.node_reminder}" or ""
        tool_tip += self.filename and f"\n{self.filename}" or ""
        return html_colour_text(self.win.qss_default_text, tool_tip)

    # not sure if this is needed
    # def hoverLeaveEvent(self, event):
    #     pass

    # Inherited, don't change definition
    # def mousePressEvent(self, event) -> None:
    #     print(f"TreeGraphicsItem.mousePressEvent: {self.filename}, {self.data}, {self.node_id}")
    #     # AltModifier (altKey), ControlModifier(crtlKey)
    #     event.accept()

    # Inherited, don't change definition
    # def mouseReleaseEvent(self, event) -> None:
    #     print(f"TreeGraphicsItem.mouseReleaseEvent: {self.filename}, {self.node_id}")
    #     # AltModifier (altKey), ControlModifier(crtlKey)
    #     event.accept()
