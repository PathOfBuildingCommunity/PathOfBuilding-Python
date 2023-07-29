"""
Pob implementation of QlistWidget

Currently only needed .
"""


from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Qt

# from qdarktheme.qtpy.QtWidgets import QListWidget
# from qdarktheme.qtpy.QtCore import Qt
from widgets.ui_utils import HTMLDelegate


class ListBox(QListWidget):
    """PoB UI ListBox"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Respond to key presses if desired
        self.key_press_handler = None

        # Allow us to print in colour
        self.delegate = HTMLDelegate()
        self.delegate._list = self

    # Overridden function
    def keyReleaseEvent(self, event):
        """

        :param: QKeyEvent. The event matrix
        :return: N/A
        """
        # print("ListBox", event)
        ctrl_pressed = event.keyCombination().keyboardModifiers() == Qt.ControlModifier
        alt_pressed = event.keyCombination().keyboardModifiers() == Qt.AltModifier
        shift_pressed = event.keyCombination().keyboardModifiers() == Qt.ShiftModifier
        if self.key_press_handler:
            self.key_press_handler(event.key(), ctrl_pressed, alt_pressed, shift_pressed, event)
        else:
            event.ignore()
        super(ListBox, self).keyPressEvent(event)

    def set_delegate(self):
        """Set the HTML delegate after the UI has initialized. Allows for listboxes to not have to display colour"""
        self.setItemDelegate(self.delegate)
