"""
A layout to autoorganise widgets according the the size of the window around them.
This is a compilation of many examples on the internet and PoB original content.
"""

import warnings

from qdarktheme.qtpy.QtCore import Qt, QMargins, QPoint, QRect, QSize
from qdarktheme.qtpy.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        """Initialize layout."""
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.margin = margin

        # spaces between each item
        self.spaceX = 5
        self.spaceY = 5

        # Internal list of contained widgets
        self.itemList = []

    def __del__(self):
        """Internal delete function."""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    # Inherited Function. Don't change name
    def addItem(self, item):
        """
        Adds a widget to the layout.

        :param: Widget: The item item to add.
        :return: N/A
        """
        self.itemList.append(item)

    def insertItem(self, index, item):
        """
        Adds a widget to the layout.

        :param: Widget: The item item to add.
        :return: N/A
        """
        self.itemList.insert(index, item)

    def count(self):
        """
        I love to Count !!!
        :return: Integer: Number of widgets in layout
        """
        return len(self.itemList)

    # Inherited Function. Don't change name
    def itemAt(self, index):
        """
        Return a reference to a widget in the layout.

        :return: Return a reference to a widget in the layout, or None
        """
        """
        Python throws a RuntimeWarning warning about Groupbox. Disable Runtime warnings.
        RuntimeWarning: Invalid return value in function QLayout.itemAt, expected PySide6.QtWidgets.QLayoutItem, 
            got PySide6.QtWidgets.QGroupBox
        """
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    # Inherited Function. Don't change name
    def takeAt(self, index):
        """
        Remove a widget.

        :return: Return a reference to a widget in the layout, or None
        """
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    # Inherited Function. Don't change name
    def expandingDirections(self):
        """
        Actually set parents geometry based on our version of do_layout.

        :return: Size information
        """
        return Qt.Orientations(Qt.Orientation(0))

    # Inherited Function. Don't change name
    def hasHeightForWidth(self):
        """
        Ask the layout if there is a valid heightForWidth() function.

        :return: Boolean: True
        """
        return True

    # Inherited Function. Don't change name
    def heightForWidth(self, width):
        """
        Test do_layout and return what the height will be.

        :return: Integer: Expected height of the parent
        """
        height = self.do_layout(QRect(0, 0, width, 0), True)
        return height

    # Inherited Function. Don't change name
    def setGeometry(self, rect):
        """
        Actually set parents geometry based on our version of do_layout.

        :return: N/A
        """
        super(FlowLayout, self).setGeometry(rect)
        self.do_layout(rect, False)

    # Inherited Function. Don't change name
    def sizeHint(self):
        """
        Return the maximum value of all the widget's minimum size.

        :return: QSize
        """
        return self.minimumSize()

    # Inherited Function. Don't change name
    def minimumSize(self):
        """
        Return the maximum value of all the widget's minimum size.

        :return: QSize
        """
        _size = QSize()

        for item in self.itemList:
            _size = _size.expandedTo(item.minimumSize())

        _size += QSize(2 * self.margin, 2 * self.margin)
        return _size

    def do_layout(self, rect, test_only):
        """
        Process each *visible* widget's width, and decide how many rows will be occupied.
        Also sets the location of the widgets.
          !!! Note the visible word. sizeHint() knows if the item is visble or not.

        :param rect: QRect: size of parent.
        :param test_only: boolean: processes everything but will not alter the position of widgets.
        :return: integer: The height that the parent should be.
        """
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self.itemList:
            try:
                # GroupBoxes don't have sizeHint(), so just use their dimensions
                # Our Groupboxes are marked as 'Fixed'.
                # Some wighets don't have SizePolicy(), so we wrap this in a try/except
                if item.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed:
                    width = item.width()
                    height = item.height()
                else:
                    width = item.sizeHint().width()
                    height = item.sizeHint().height()
            except AttributeError:
                width = item.sizeHint().width()
                height = item.sizeHint().height()
            next_x = x + width + self.spaceX
            if next_x - self.spaceX > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + self.spaceY
                next_x = x + width + self.spaceX
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, height)

        return y + line_height - rect.y()
