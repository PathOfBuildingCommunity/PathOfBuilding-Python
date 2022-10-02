"""
TreeItem Class

This class represents a graphical instance of one visual element of a Passive Tree for a given tree version.

"""
from qdarktheme.qtpy.QtGui import QPixmap
from qdarktheme.qtpy.QtWidgets import QGraphicsPixmapItem

from pob_config import Config


class TreeGraphicsItem(QGraphicsPixmapItem):
    def __init__(
        self,
        _config: Config,
        _image: str,
        z_value=0,
        selectable=False,
    ) -> None:
        super(TreeGraphicsItem, self).__init__()
        self.config = _config
        self.filename = ""
        self.data = ""
        self.node_id = 0
        self.node_sd = ""
        self.node_name = ""
        self.node_isoverlay = False
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
        self.tool_tip = self.node_name and f"{self.node_name}, {self.node_id}" or f"{self.node_id}"
        self.tool_tip += self.filename and f"{self.filename}, " or ""
        self.tool_tip += self.data and f"{self.data}, " or ""

        # turn all those data's into properties ?

    # Inherited, don't change definition
    def setScale(self, scale: int = 1):
        super(TreeGraphicsItem, self).setScale(scale)
        self.width *= scale
        self.height *= scale

    # Inherited, don't change definition
    def hoverEnterEvent(self, event):
        # this will be text associated with the node
        self.setToolTip(self.tool_tip)

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
