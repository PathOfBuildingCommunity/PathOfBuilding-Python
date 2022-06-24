import sys, atexit, qdarktheme
from PySide6 import QtWidgets, QtCore, QtGui
import PoB_config, notesTab

# pyside6-uic PoB.ui -o PoB_UI.py
from PoB_UI import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def exit_handler(self):
        PoB_config.writeConfig()
        # Logic for checking we need to save and save if needed, goes here...

    def closeApp(self):
        self.close()

    def buildOpen(self):
        # Logic for checking we need to save and save if needed, goes here...
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("Builds (*.xml)")
        dialog.setDirectory(PoB_config.buildPath)
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            print("filenames: %s" % fileNames)
        # open the file

    def buildSaveAs(self):
        # Logic for checking we need to save and save if needed, goes here...
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("Builds (*.xml)")
        dialog.setDirectory(PoB_config.buildPath)
        dialog.setDefaultSuffix("xml")
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            print("filenames: %s" % fileNames)
        # write the file

    def setTheme(self, _action):
        action = self.sender()
        text = action.whatsThis()
        print(text)
        if text == "":
            app.setStyleSheet("")
        elif text == "light" or text == "dark":
            app.setStyleSheet(qdarktheme.load_stylesheet(text))
        else:
            app.setStyleSheet(text)

    # don't use native signals/slot so focus can be set back to edit box
    def setNotesFontSize(self, size):
        self.notesTextEdit.setFontPointSize(size)
        self.notesTextEdit.setFocus()

    # don't use native signals/slot so focus can be set back to edit box
    def setNotesFont(self):
        self.notesTextEdit.setCurrentFont(self.fontComboBox.currentFont())
        self.notesTextEdit.setFocus()

    def buildNotesTab(self):
        # notesTextEdit needs to be globally accessible
        self.notesTextEdit = QtWidgets.QTextEdit(self.tabWidget)
        self.notesTextEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tabWidget)

        fontLayout = QtWidgets.QHBoxLayout()
        fontLayout.setObjectName(u"fontLayout")
        self.fontComboBox = QtWidgets.QFontComboBox()
        self.fontComboBox.setObjectName(u"fontComboBox")
        self.fontComboBox.setMinimumSize(QtCore.QSize(154, 0))
        self.fontComboBox.editable = False
        self.fontComboBox.setCurrentText("Times New Roman")
        fontLayout.addWidget(self.fontComboBox)
        fontSpinBox = QtWidgets.QSpinBox()
        fontSpinBox.setObjectName(u"spinBox")
        fontSpinBox.setMinimumSize(QtCore.QSize(33, 0))
        fontSpinBox.setValue(10)
        fontLayout.addWidget(fontSpinBox)
        horizontalSpacer = QtWidgets.QSpacerItem(288, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        fontLayout.addItem(horizontalSpacer)
        layout.addLayout(fontLayout)

        layout.addWidget(self.notesTextEdit, 0, QtCore.Qt.AlignHCenter & QtCore.Qt.AlignVCenter)
        widget.setLayout(layout)
        self.tabWidget.addTab(widget, "&Notes")

        # fontComboBox.currentFontChanged.connect(self.notesTextEdit.setCurrentFont)
        self.fontComboBox.currentFontChanged.connect(self.setNotesFont)
        fontSpinBox.valueChanged.connect(self.setNotesFontSize)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        PoB_config.readConfig()
        atexit.register(self.exit_handler)

        # Now do all things that QT Designer can't do
        self.actionExit.triggered.connect(self.closeApp)
        self.actionOpen.triggered.connect(self.buildOpen)
        self.actionLight.triggered.connect(self.setTheme)
        self.actionDark.triggered.connect(self.setTheme)
        self.actionNotes.triggered.connect(self.setTheme)
        self.actionStandard.triggered.connect(self.setTheme)

        # QT Designer can't add a layout as a tab
        self.buildNotesTab()


app = QtWidgets.QApplication(sys.argv)
# app.setStyleSheet(qdarktheme.load_stylesheet())  # "light" "dark" "Fusion" "qwindowsvistastyle"
# app.setStyleSheet(qdarktheme.load_stylesheet("light"))  # "light" "dark" "Fusion" "qwindowsvistastyle"

window = MainWindow()
window.show()
app.exec()
