# MRE test for faulty QSS in Qlinedit through QListWidget

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListWidget, QListWidgetItem, QMainWindow

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

sus_qss = """
QComboBox,
/* QLineEdit, */
QPushButton {
    border: 1px solid rgba( 63, 64, 66, 1.000 );
    padding: 4px 8px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # QApplication.instance().setStyleSheet(template)
        QApplication.instance().setStyleSheet(template + sus_qss)
        self.setWindowTitle("My App")

        self.setFixedSize(QSize(400, 300))
        _list = QListWidget()
        for idx in range(0, 15):
            lwi = QListWidgetItem(f"Item {idx}")
            lwi.setFlags(lwi.flags() | Qt.ItemIsEditable)
            # lwi.setSizeHint(QSize(-1, 40))
            # print(lwi.sizeHint())
            _list.addItem(lwi)
        _list.setAlternatingRowColors(True)
        _list.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        # Set the central widget of the Window.
        self.setCentralWidget(_list)


app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()

# Start the event loop.
app.exec()
