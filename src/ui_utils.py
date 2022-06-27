"""
Utilities for the UI that do not have dependencies on MainWindow

"""
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QColorDialog,
    QDialogButtonBox,
    QFileDialog,
    QFontDialog,
    QLabel,
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
    button = QMessageBox.question(win, title, text, QMessageBox.Yes, QMessageBox.No)
    if button == QMessageBox.Yes:
        return True
    else:
        return False


def ok_dialog(win, title, text, btn_text = "OK"):
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Information)
    dlg.exec_()


def critical_dialog(win, title, text, btn_text = "Close"):
    dlg = QMessageBox(win)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.addButton(btn_text, QMessageBox.YesRole)
    dlg.setIcon(QMessageBox.Critical)
    dlg.exec_()
