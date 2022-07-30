"""
This Class manages all the elements and owns some elements of the "SKILLS" tab
"""

from qdarktheme.qtpy.QtCore import (
    QCoreApplication,
    QDir,
    QRect,
    QRectF,
    QSize,
    Qt,
    Slot,
)
from qdarktheme.qtpy.QtGui import (
    QAction,
    QActionGroup,
    QFont,
    QIcon,
    QPixmap,
    QBrush,
    QColor,
    QPainter,
)
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from PoB_Main_Window import Ui_MainWindow
from pob_config import *
from pob_config import _VERSION


class SkillsUI:
    def __init__(self, _config: Config) -> None:
        self.pob_config = _config
        self.win = self.pob_config.win
        self.build = self.win.build

    def __repr__(self) -> str:
        return (
            f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
            if self.ascendancy.value is not None
            else "\n"
        )

    def load(self):
        """
        Load internal structures from the build object
        """
        pass

    def save(self):
        """
        Save internal structures back to the build object
        """
        pass


def test() -> None:
    skills_ui = SkillsUI()
    print(skills_ui)


if __name__ == "__main__":
    test()
