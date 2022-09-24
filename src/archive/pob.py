import atexit

from PySide6 import QtWidgets, QtCore
import qdarktheme

from pob_config import Config, color_codes
from pob_main_ui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def exit_handler(self):
        self.config.write()
        # Logic for checking we need to save and save if needed, goes here...
        # filePtr = open("edit.html", "w")
        # try:
        #     filePtr.write(self.notes_text_edit.toHtml())
        # finally:
        #     filePtr.close()

    def close_app(self):
        self.close()

    def build_open(self):
        # Logic for checking we need to save and save if needed, goes here...
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("Builds (*.xml)")
        dialog.setDirectory(self.config.build_path)
        if dialog.exec():
            filename = dialog.selectedFiles()
            print(f"filenames: {filename}")
            # open the file

    def build_save_as(self):
        # Logic for checking we need to save and save if needed, goes here...
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("Builds (*.xml)")
        dialog.setDirectory(self.config.build_path)
        dialog.setDefaultSuffix("xml")
        if dialog.exec():
            filename = dialog.selectedFiles()
            print(f"filename: {filename}")
            # write the file

    def set_theme(self, _action):
        action = self.sender()
        text = action.whatsThis()
        print(text)
        if text in ["light", "dark"]:
            app.setStyleSheet(qdarktheme.load_stylesheet(text))
        elif text:
            app.setStyle(text)
        else:
            app.setStyleSheet("")
            app.setStyle("Fusion")

    # don't use native signals/slot, so focus can be set back to edit box
    def set_notes_font_size(self, size):
        self.notes_text_edit.setFontPointSize(size)
        self.notes_text_edit.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    def set_notes_font_colour(self, colour_name):
        if colour_name == "NORMAL":
            self.notes_text_edit.setTextColor(self.defaultTextColour)
        else:
            self.notes_text_edit.setTextColor(color_codes[colour_name])
        self.notes_text_edit.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    def set_notes_font(self):
        action = self.sender()
        self.notes_text_edit.setCurrentFont(action.currentFont())
        self.notes_text_edit.setFocus()

    def build_notes_tab(self):
        # notes_text_edit needs to be globally accessible
        self.notes_text_edit = QtWidgets.QTextEdit(self.tabWidget)
        self.notes_text_edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tabWidget)

        font_layout = QtWidgets.QHBoxLayout()
        font_layout.setObjectName("font_layout")
        self.font_combo_box = QtWidgets.QFontComboBox()
        self.font_combo_box.setObjectName("font_combo_box")
        self.font_combo_box.setMinimumSize(QtCore.QSize(200, 0))
        self.font_combo_box.editable = False
        self.font_combo_box.setCurrentText("Times New Roman")
        font_layout.addWidget(self.font_combo_box)
        font_spin_box = QtWidgets.QSpinBox()
        font_spin_box.setObjectName("spinBox")
        font_spin_box.setMinimumSize(QtCore.QSize(35, 0))
        font_spin_box.setMaximum(50)
        font_spin_box.setMinimum(3)
        font_spin_box.setValue(10)
        font_layout.addWidget(font_spin_box)
        self.colour_combo_box = QtWidgets.QComboBox()
        self.colour_combo_box.setObjectName("colourComboBox")
        self.colour_combo_box.setMinimumSize(QtCore.QSize(140, 0))
        self.colour_combo_box.addItems(color_codes.keys())
        font_layout.addWidget(self.colour_combo_box)
        horizontal_spacer = QtWidgets.QSpacerItem(
            88, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        font_layout.addItem(horizontal_spacer)
        layout.addLayout(font_layout)

        layout.addWidget(
            self.notes_text_edit, 0, QtCore.Qt.AlignHCenter & QtCore.Qt.AlignVCenter
        )
        widget.setLayout(layout)
        self.tabWidget.addTab(widget, "&Notes")

        self.font_combo_box.currentFontChanged.connect(self.set_notes_font)  #
        font_spin_box.valueChanged.connect(self.set_notes_font_size)  #
        self.colour_combo_box.currentTextChanged.connect(self.set_notes_font_colour)  #
        # tab indexes are 0 based
        self.tab_focus = {
            0: self.tabWidget,
            1: self.tabWidget,
            2: self.tabWidget,
            3: self.notes_text_edit,
        }
        # build_notes_tab

    def set_tab_focus(self, index):
        self.tab_focus.get(index).setFocus()

    def __init__(self) -> None:
        super().__init__()
        self.font_combo_box = None
        self.colour_combo_box = None
        self.tab_focus = None
        self.notes_text_edit = None
        self.setupUi(self)
        self.config = Config()
        self.config.read()
        atexit.register(self.exit_handler)

        # Now do all things that QT Designer can't do
        self.actionExit.triggered.connect(self.close_app)
        self.actionOpen.triggered.connect(self.build_open)
        self.actionLight.triggered.connect(self.set_theme)
        self.actionDark.triggered.connect(self.set_theme)
        self.actionDarcula.triggered.connect(self.set_theme)
        self.actionStandard.triggered.connect(self.set_theme)
        self.tabWidget.currentChanged.connect(self.set_tab_focus)

        # QT Designer can't add a layout as a tab
        self.build_notes_tab()
        self.defaultTextColour = self.notes_text_edit.textColor()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
