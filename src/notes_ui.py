"""
This Class manages all the elements and owns some elements of the "NOTES" tab
"""

import re

from qdarktheme.qtpy.QtCore import Slot, Qt
from qdarktheme.qtpy.QtGui import QColor, QBrush

from PoB_Main_Window import Ui_MainWindow
from pob_config import Config
from constants import ColourCodes

colorEscape = [
    ColourCodes.BLACK,  # ^0
    ColourCodes.RED,  # ^1
    ColourCodes.GREEN,  # ^2
    ColourCodes.BLUE,  # ^3
    ColourCodes.YELLOW,  # ^4
    ColourCodes.PURPLE,  # ^5
    ColourCodes.AQUA,  # ^6
    ColourCodes.WHITE,  # ^7
    ColourCodes.GRAY,  # ^8
    ColourCodes.DARKGRAY,  # ^9
]


class NotesUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self.modified = False

        # Add content to Colour ComboBox
        self.win.combo_Notes_Colour.addItems([colour.name.title() for colour in ColourCodes])
        for index in range(self.win.combo_Notes_Colour.count()):
            colour = ColourCodes[self.win.combo_Notes_Colour.itemText(index).upper()].value
            self.win.combo_Notes_Colour.setItemData(index, QBrush(colour), Qt.ForegroundRole)

        self.win.btn_ConvertToText.setVisible(False)
        self.win.btn_ConvertToText.clicked.connect(self.convert_to_text)
        self.win.combo_Notes_Font.currentFontChanged.connect(self.set_notes_font)
        self.win.spin_Notes_FontSize.valueChanged.connect(self.set_notes_font_size)
        self.win.combo_Notes_Colour.currentTextChanged.connect(self.set_notes_font_colour)

    def load(self, _notes_html, _notes):
        """
        Load internal structures from the build object
        If there are no HTML notes, then get the Text based ones

        :param _notes_html: String: HTML version of notes. Is None if not in the source XML
        :param _notes: String: Plain text version of notes
        :return: N/A
        """
        if _notes_html is not None:
            self.win.btn_ConvertToText.setVisible(False)
            self.win.textedit_Notes.setHtml(_notes_html.strip())
        else:
            if _notes is not None:
                self.win.btn_ConvertToText.setVisible(True)
                self.win.textedit_Notes.setPlainText(_notes.strip())

    def save(self):
        """
        Save internal structures back to the build object

        :return: two strings represnting the plain text and the html text
        """
        _notes_html = self.win.textedit_Notes.document().toHtml()
        _notes = self.win.textedit_Notes.document().toPlainText()
        self.modified = False
        return _notes, _notes_html

    def convert_to_text(self):
        """
        Convert the lua colour codes to html and sets the Notes control with the new html text

        :return: N/A
        """
        text = self.win.textedit_Notes.document().toPlainText()
        # remove all obvious duplicate colours (mainly ^7^7)
        for idx in range(10):
            while f"^{idx}^{idx}" in text:
                text = text.replace(f"^{idx}^{idx}", f"^{idx}")
        # remove single charactor colours for their full versions
        for idx in range(10):
            while f"^{idx}" in text:
                text = text.replace(f"^{idx}", f"^{colorEscape[idx].value.replace('#', 'x')}")

        # search for the lua colour codes and replace them with span tags
        m = re.search(r"(\^x[0-9A-Fa-f]{6})", text)
        while m is not None:
            # get the colour from the match
            c = re.search(r"([0-9A-Fa-f]{6})", m.group(1))
            text = text.replace(m.group(1), f'</span><span style="color:#{c.group(1)};">')
            m = re.search(r"(\^x[0-9A-Fa-f]{6})", text)

        # check for a leading closing span tag
        f = re.match("</span>", text)
        if f is not None:
            text = text[7:]
        # check for no leading span tag
        f = re.match("<span ", text)
        if f is None:
            text = f'<span style="color:{ColourCodes.NORMAL.value};">{text}'
        # replace newlines
        text = text.replace("\n", "<br>")

        self.win.textedit_Notes.setFontPointSize(self.win.spin_Notes_FontSize.value())
        self.win.textedit_Notes.setCurrentFont(self.win.combo_Notes_Font.currentText())
        self.win.textedit_Notes.setHtml(text)
        self.win.btn_ConvertToText.setVisible(False)
        self.win.textedit_Notes.setFocus()

    # don't use native signal/slot connection, so we can set focus back to edit box
    @Slot()
    def set_notes_font_size(self, _size):
        """
        Actions required for changing the TextEdit font size. Ensure that the TextEdit gets the focus back.

        :return: N/A
        """
        self.win.textedit_Notes.setFontPointSize(_size)
        self.win.textedit_Notes.setFocus()

    # don't use native signal/slot connection, so we can set focus back to edit box
    @Slot()
    def set_notes_font_colour(self, colour_name):
        """
        Actions required for changing TextEdit font colour. Ensure that the TextEdit gets the focus back.

        :param colour_name: String of the selected text
        :return: N/A
        """
        self.win.textedit_Notes.setTextColor(ColourCodes[colour_name.upper()].value)
        self.win.textedit_Notes.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font(self):
        """
        Actions required for changing the TextEdit font. Ensure that the TextEdit gets the focus back.

        :return: N/A
        """
        self.win.textedit_Notes.setCurrentFont(self.win.combo_Notes_Font.currentText())
        self.win.textedit_Notes.setFocus()


# def test() -> None:
#     notes_ui = NotesUI()
#     print(notes_ui)
#
#
# if __name__ == "__main__":
#     test()
