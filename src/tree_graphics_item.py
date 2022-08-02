"""
TreeItem Class

This class represents a graphical instance of one visual element of a Passive Tree for a given tree version.

"""
from qdarktheme.qtpy.QtCore import Qt
from qdarktheme.qtpy.QtGui import QPixmap
from qdarktheme.qtpy.QtWidgets import QGraphicsPixmapItem, QGraphicsItem

from pob_config import *

"""
Example data
    "skill": 57560,
    "name": "Rite of Ruin",
    "icon": "Art/2DArt/SkillIcons/passives/Berserker/RiteOfRuin.png",
    "isNotable": true,
    "ascendancyName": "Berserker",
    "stats": [
        "Lose 0.1% of Life per second per Rage while you are not losing Rage",
        "Inherent effects from having Rage are Tripled",
        "Cannot be Stunned while you have at least 25 Rage"
    ],
    "reminderText": [
        "(Inherent effects from having Rage are:",
        "1% increased Attack Damage per 1 Rage",
        "1% increased Attack Speed per 2 Rage",
        "1% increased Movement Speed per 5 Rage)"
    ],
    "group": 1,
    "orbit": 4,
    "orbitIndex": 10,
    "out": [
        "42861"
    ],
    "in": []
"""


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

        # turn all those data's into properties ?

    # Inherited, don't change definition
    def setScale(self, scale: int = 1):
        super(TreeGraphicsItem, self).setScale(scale)
        self.width *= scale
        self.height *= scale

    # Inherited, don't change definition
    def hoverEnterEvent(self, event):
        # this will be text associated with the node
        if self.filename != "":
            self.setToolTip(f"{self.filename}, {self.node_id}\n{self.data}")

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
