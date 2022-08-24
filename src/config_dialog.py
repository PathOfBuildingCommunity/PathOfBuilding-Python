from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from dlg_Export import Ui_Dialog


class ExportDlg(Ui_Dialog, QDialog):
    """Employee dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Run the .setupUi() method to show the GUI
        self.setupUi(self)
