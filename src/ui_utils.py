"""Utilities for the UI that do not have dependencies on MainWindow."""

from qdarktheme.qtpy.QtWidgets import QMessageBox


def yes_no_dialog(win, title, text):
    button = QMessageBox.question(win, title, text, QMessageBox.Yes, QMessageBox.No)
    return button == QMessageBox.Yes


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
