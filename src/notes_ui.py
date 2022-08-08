"""
This Class manages all the elements and owns some elements of the "NOTES" tab
"""


from PoB_Main_Window import Ui_MainWindow
from pob_config import *
from constants import _VERSION


class NotesUI:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.pob_config = _config
        self.win = _win
        self.modified = False

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, _notes_html, _notes):
        """
        Load internal structures from the build object
        If there are no HTML notes, then get the Text based ones
        :param _notes_html: String: HTML version of notes. Is None if not in the source XML
        :param _notes: String: Plain text version of notes
        :return: N/A
        """
        if _notes_html:
            self.win.textedit_Notes.setHtml(_notes_html.strip())
        else:
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


# def test() -> None:
#     notes_ui = NotesUI()
#     print(notes_ui)
#
#
# if __name__ == "__main__":
#     test()
