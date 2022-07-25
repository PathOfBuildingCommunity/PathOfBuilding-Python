"""
Utilities for the UI that do not have dependencies on MainWindow
"""
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

"""This doesn't work and needs fixing"""
# class FlowLayout(QLayout):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         if parent is not None:
#             self.setContentsMargins(QMargins(0, 0, 0, 0))
#
#         self._item_list = []
#
#     def __del__(self):
#         item = self.takeAt(0)
#         while item:
#             item = self.takeAt(0)
#
#     def addItem(self, item):
#         self._item_list.append(item)
#
#     def count(self):
#         return len(self._item_list)
#
#     def itemAt(self, index):
#         if 0 <= index < len(self._item_list):
#             return self._item_list[index]
#
#         return None
#
#     def takeAt(self, index):
#         if 0 <= index < len(self._item_list):
#             return self._item_list.pop(index)
#
#         return None
#
#     def expandingDirections(self):
#         return Qt.Orientation(0)
#
#     def hasHeightForWidth(self):
#         return True
#
#     def heightForWidth(self, width):
#         height = self._do_layout(QRect(0, 0, width, 0), True)
#         return height
#
#     def setGeometry(self, rect):
#         super(FlowLayout, self).setGeometry(rect)
#         self._do_layout(rect, False)
#
#     def sizeHint(self):
#         return self.minimumSize()
#
#     def minimumSize(self):
#         size = QSize()
#
#         for item in self._item_list:
#             size = size.expandedTo(item.minimumSize())
#
#         size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
#         return size
#
#     def _do_layout(self, rect, test_only):
#         x = rect.x()
#         y = rect.y()
#         line_height = 0
#         spacing = self.spacing()
#
#         for item in self._item_list:
#             style = item.widget().style()
#             layout_spacing_x = style.layoutSpacing(
#                 QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
#             )
#             layout_spacing_y = style.layoutSpacing(
#                 QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
#             )
#             space_x = spacing + layout_spacing_x
#             space_y = spacing + layout_spacing_y
#             next_x = x + item.sizeHint().width() + space_x
#             if next_x - space_x > rect.right() and line_height > 0:
#                 x = rect.x()
#                 y = y + line_height + space_y
#                 next_x = x + item.sizeHint().width() + space_x
#                 line_height = 0
#
#             if not test_only:
#                 item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
#
#             x = next_x
#             line_height = max(line_height, item.sizeHint().height())
#
#         return y + line_height - rect.y()
