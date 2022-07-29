"""
Utilities for the UI that do not have dependencies on MainWindow
"""
from pprint import pprint

from qdarktheme.qtpy.QtCore import Qt, QMargins, QPoint, QRect, QSize
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QColorDialog,
    QDialogButtonBox,
    QFileDialog,
    QFontDialog,
    QLabel,
    QLayout,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QWidget,
)


# ui_utils.yes_no_dialog(self, app.tr("Save build"), app.tr("build name goes here"))
# ui_utils.critical_dialog(self, app.tr("Save build"), app.tr("build name goes here"), app.tr("Close"))
# ui_utils.ok_dialog(self, app.tr("Save build"), app.tr("build name goes here"))

#
def yes_no_dialog(win, title, text):
    return (
        QMessageBox.question(win, title, text, QMessageBox.Yes, QMessageBox.No)
        == QMessageBox.Yes
    )


def ok_dialog(win, title, text, btn_text="OK"):
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Information)
    dlg.exec_()


def critical_dialog(win, title, text, btn_text="Close"):
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Critical)
    dlg.exec_()


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        """
        Initialize layout
        """
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
        """
        Internal delete function
        :return: N/A
        """
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """
        Adds a widget to the layout
        :return: N/A
        """
        self.itemList.append(item)

    def count(self):
        """
        Count.
        :return: Integer: Number of widgets in layout
        """
        return len(self.itemList)

    def itemAt(self, index):
        """
        Return a reference to a widget in the layout
        :return: Return a reference to a widget in the layout, or None
        """
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        """
        Remove a widget
        :return: Return a reference to a widget in the layout, or None
        """
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        """
        Actually set parents geometry based on out version of doLayout
        :return: N/A
        """
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        """
        Ask the layout if there is a valid heightForWidth() function
        :return: Booean: True
        """
        return True

    def heightForWidth(self, width):
        """
        Test doLayout and return what the height will be.
        :return: Integer: Expected height of the parent
        """
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """
        Actually set parents geometry based on out version of doLayout
        :return: N/A
        """
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        """
        Return the maximum value of all the widget's minimum size
        :return: QSize
        """
        return self.minimumSize()

    def minimumSize(self):
        """
        Return the maximum value of all the widget's minimum size
        :return: QSize
        """
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.margin, 2 * self.margin)
        return size

    def doLayout(self, rect, testOnly):
        """
        Process each visible widget's width, and decide how many rows will be occupied.
        Also sets the location of the widgets
         sizeHint() knows if the item is visble or not
        :param rect: size of parent.
        :param testOnly: processes everything but will not alter the position of widgets.
        :return: integer: The height that the parent should be
        """
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            nextX = x + item.sizeHint().width() + self.spaceX
            if nextX - self.spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + self.spaceY
                nextX = x + item.sizeHint().width() + self.spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
