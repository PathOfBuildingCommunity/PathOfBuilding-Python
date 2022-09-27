"""
Utilities for the UI that do not have dependencies on MainWindow
"""

from qdarktheme.qtpy.QtCore import Qt, QMargins, QPoint, QRect, QSize
from qdarktheme.qtpy.QtGui import QAbstractTextDocumentLayout, QTextDocument
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QLayout,
    QMessageBox,
    QSizePolicy,
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
)

from pob_config import _debug
from constants import ColourCodes


def yes_no_dialog(win, title, text):
    """Return true if the user selects Yes."""
    return QMessageBox.question(win, title, text, QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes


def ok_dialog(win, title, text, btn_text="OK"):
    """Notify the user of some information."""
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Information)
    dlg.exec_()


def critical_dialog(win, title, text, btn_text="Close"):
    """Notify the user of some critical? information."""
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Critical)
    dlg.exec_()


def html_colour_text(colour, text):
    """
    Put text into html span tags.

    :param colour: string: the #colour to be used or ColourCodes name
    :param text: the text to be coloured
    :return: str:
    """
    c = colour[0] == "#" and colour or ColourCodes[colour.upper()].value
    return f'<span style="color:{c};">{text}</span>'


def set_combo_index_by_data(_combo: QComboBox, _data):
    """
    Set a combo box current index based on it's data field.

    :param _combo: the combo box.
    :param _data: the data. There is no type to this, so the passed in type should match what the combo has.
    :return: int: the index of the combobox or -1 if not found.
    """
    if _data is None:
        _data = "None"
    # print_call_stack()
    for i in range(_combo.count()):
        if _combo.itemData(i) == _data:
            _combo.setCurrentIndex(i)
            return i
    return -1


def set_combo_index_by_text(_combo: QComboBox, _text):
    """
    Set a combo box current index based on it's text field.

    :param _combo: the combo box.
    :param _text: string: the text.
    :return: int: the index of the combobox or -1 if not found.
    """
    if _text is None:
        _text = "None"
    # print_call_stack()
    for i in range(_combo.count()):
        if _combo.itemText(i) == _text:
            _combo.setCurrentIndex(i)
            return i
    return -1


# https://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt
class HTMLDelegate(QStyledItemDelegate):
    def __init__(self) -> None:
        super().__init__()
        # the list of WidgetItems from a QListView
        self._list = None

    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        style = QApplication.style() if options.widget is None else options.widget.style()

        doc = QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(text_rect.topLeft())
        painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """Inherited function to return the max width of all text items"""
        doc = QTextDocument()
        w = 0
        for row in range(self._list.count()):
            doc.setHtml(self._list.item(row).text())
            w = max(w, doc.idealWidth())
        return QSize(w + 20, doc.size().height())
