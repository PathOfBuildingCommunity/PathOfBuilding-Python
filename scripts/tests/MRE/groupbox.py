# MRE test for QSS for QGroupBox title
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListWidget, QListWidgetItem, QMainWindow, QGroupBox

import sys

template = """
* {
    padding: 0;
    margin: 0;
    border: none;
    border-style: none;
    border-image: unset;
    outline: none;
}
QWidget {
    background: rgba( 32, 33, 36, 1.000 );
    color: rgba( 228, 231, 235, 1.000 );
    selection-color: rgba( 228, 231, 235, 1.000 );
    selection-background-color: rgba( 186, 191, 196, 0.200 );
    border-radius: 4px;
}

QListWidget,
QListView {
    border: 1px solid rgba( 63, 64, 66, 1.000 );
    selection-color: rgba( 228, 231, 235, 1.000 );
    selection-background-color: rgba( 186, 191, 196, 0.200 );
}

QListWidget:hover {
    border: 1px solid rgba( qss_hover_borders );
}

QListView,
QAbstractItemView {
	alternate-background-color: rgba( 96, 99, 108, 0.300 );
	padding: 0px;
	margin: 0px;
}

QListWidget::item {
    color: rgba( 255, 255, 255, 0.800 );
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        QApplication.instance().setStyleSheet("QGroupBox { color: red; font-weight: bold; }")
        # QApplication.instance().setStyleSheet(template)
        # QApplication.instance().setStyleSheet(template+sus_qss)
        self.setWindowTitle("My App")

        self.setFixedSize(QSize(400, 300))
        # list = QListWidget()
        # for idx in range(0,15):
        # lwi = QListWidgetItem(f"Item {idx}")
        # lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
        # list.addItem(lwi)
        # list.setAlternatingRowColors(True)
        # list.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)

        # Set the central widget of the Window.
        # self.setCentralWidget(list)

        gb = QGroupBox("My GroupBox")
        self.setCentralWidget(gb)


app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()

# Start the event loop.
app.exec()
