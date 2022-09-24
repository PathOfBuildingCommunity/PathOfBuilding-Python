"""
Path of Building UI class

Sets up and connects internal UI components
"""
import qdarktheme
from qdarktheme.qtpy.QtCore import QSize, QDir, QRect, Qt, Slot, QCoreApplication
from qdarktheme.qtpy.QtGui import QAction, QActionGroup, QFont, QIcon
from qdarktheme.qtpy.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from qdarktheme.util import get_qdarktheme_root_path
from qdarktheme.widget_gallery.ui.dock_ui import DockUI
from qdarktheme.widget_gallery.ui.frame_ui import FrameUI
from qdarktheme.widget_gallery.ui.widgets_ui import WidgetsUI

from pob_config import Config, color_codes
from build import Build


class RightPane:
    """The ui class of dock window."""

    def __init__(self, win: QTabWidget) -> None:
        super().__init__()
        """Set up ui."""
        # Tree tab
        self.tabTree = QWidget()
        win.addTab(
            self.tabTree, QCoreApplication.translate("MainWindow", "&Tree", None)
        )
        # Skills tab
        self.tabSkills = QWidget()
        win.addTab(
            self.tabSkills, QCoreApplication.translate("MainWindow", "&Skills", None)
        )
        # Items tab
        self.tabItems = QWidget()
        win.addTab(
            self.tabItems, QCoreApplication.translate("MainWindow", "&Items", None)
        )
        # Notes tab
        self.notes_text_edit = QTextEdit()
        self.notes_text_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.defaultTextColour = self.notes_text_edit.textColor()

        self.nt_widget = QWidget()
        self.nt_layout = QVBoxLayout()

        self.font_layout = QHBoxLayout()
        self.font_layout.setObjectName("font_layout")
        self.font_combo_box = QFontComboBox(self.nt_widget)
        self.font_combo_box.setObjectName("font_combo_box")
        self.font_combo_box.setMinimumSize(QSize(200, 0))
        self.font_combo_box.editable = False
        self.font_combo_box.setCurrentText("Times New Roman")
        self.font_layout.addWidget(self.font_combo_box)
        self.font_spin_box = QSpinBox(self.nt_widget)
        self.font_spin_box.setObjectName("spinBox")
        self.font_spin_box.setMinimumSize(QSize(35, 0))
        self.font_spin_box.setMaximum(50)
        self.font_spin_box.setMinimum(3)
        self.font_spin_box.setValue(10)
        self.font_layout.addWidget(self.font_spin_box)
        self.colour_combo_box = QComboBox(self.nt_widget)
        self.colour_combo_box.setObjectName("colourComboBox")
        self.colour_combo_box.setMinimumSize(QSize(140, 0))
        self.colour_combo_box.addItems(color_codes.keys())
        self.font_layout.addWidget(self.colour_combo_box)
        self.horizontal_spacer = QSpacerItem(
            88, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.font_layout.addItem(self.horizontal_spacer)
        self.nt_layout.addLayout(self.font_layout)

        self.nt_layout.addWidget(
            self.notes_text_edit, 0, Qt.AlignHCenter & Qt.AlignVCenter
        )
        self.nt_widget.setLayout(self.nt_layout)
        win.addTab(self.nt_widget, "&Notes")
        # RightPane


class LeftPane:
    def __init__(self, win: QFrame) -> None:
        """Set up ui."""
        super().__init__()
        # def __init__(self) -> None:
        # def setup_ui(self, win: QWidget) -> None:
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(0)
        win.setSizePolicy(size_policy)
        win.setMinimumSize(QSize(180, 600))
        win.setMaximumSize(QSize(400, 10000))
        win.setSizeIncrement(QSize(10, 0))
        win.setFrameShape(QFrame.StyledPanel)
        win.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(win)
        self.formLayout.setContentsMargins(0, 0, 0, 0)

        bandit_label = QLabel(win)
        bandit_label.setText(QCoreApplication.translate("MainWindow", "Bandits:", None))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, bandit_label)

        self.bandit_comboBox = QComboBox(win)
        self.bandit_comboBox.addItem("Item1")
        self.bandit_comboBox.addItem("Item2")
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.bandit_comboBox)

        major_god_label = QLabel(win)
        self.formLayout.setWidget(1, QFormLayout.LabelRole, major_god_label)
        major_god_label.setText(
            QCoreApplication.translate("MainWindow", "Major Gods:", None)
        )
        self.major_god_comboBox = QComboBox(win)
        self.major_god_comboBox.addItem("God1")
        self.major_god_comboBox.addItem("God2")
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.major_god_comboBox)

        # LeftPane


class PobUi:
    def __init__(self, main_win: QMainWindow, config: Config) -> None:
        super().__init__()
        """Set up ui."""
        self.build = None
        statusbar = QStatusBar()
        main_win.setStatusBar(statusbar)
        menubar = QMenuBar()
        # Remove the space that the icon reserves. If you want check boxes or icons, then delete this section
        menubar.setStyleSheet(
            "QMenu::item {"
            "padding: 2px 6px 2px 6px;"
            "}"
            "QMenu::item:selected {"
            "background-color: rgb(0, 85, 127);"
            "color: rgb(255, 255, 255);"
            "}"
        )

        # Builds Menu
        self.action_new = QAction("Ne&w")
        self.action_new.setShortcut("Ctrl+N")
        self.action_open = QAction("&Open ...")
        self.action_open.setShortcut("Ctrl+O")
        self.action_save = QAction("Sa&ve")
        self.action_save.setShortcut("Ctrl+S")
        self.action_exit = QAction("E&xit")
        self.action_exit.setShortcut("Ctrl+X")
        self.menu_builds = menubar.addMenu("&Builds")
        self.menu_builds.addActions(
            (self.action_new, self.action_open, self.action_save)
        )
        self.menu_builds.addSeparator()
        self.menu_builds.addAction(self.action_exit)
        self.menu_builds.addSeparator()
        self.actions_recent_builds = [
            QAction(rb, main_win)
            for rb in [
                "0",
                "1",
                "2",
                "3",
                "4",
            ]
        ]
        self.menu_builds.addActions(self.actions_recent_builds)
        self.set_recent_builds(config)
        # Room for "recent" builds
        # recents = config.recentBuilds()
        # for value in recents.values():
        #     print("value: %s" % value)
        #     if value != "":
        #         self.ui.menu_builds.addAction(value)

        # Theme Menu Actions
        self.actions_theme = [QAction(theme, main_win) for theme in ["dark", "light"]]
        menu_theme = menubar.addMenu("&Theme")
        menu_theme.addActions(self.actions_theme)
        menu_theme.addSeparator()
        # Tech Demo. Switch just one entry
        self.actions_theme_dark_light = QAction(
            "Light"
        )  # opposite of the default theme
        self.actions_theme_dark_light.setShortcut("Ctrl+0")
        menu_theme.addAction(self.actions_theme_dark_light)

        main_win.setMenuBar(menubar)

        # Main Window
        self.central_window = QMainWindow()

        h_splitter_1 = QSplitter(Qt.Orientation.Horizontal)
        h_splitter_1.setMinimumHeight(350)  # Fix bug layout crush

        # Layout
        container = QWidget()
        self.frame = QFrame(h_splitter_1)
        self.left_pane = LeftPane(self.frame)
        # container.setObjectName("Build Info")
        # self.left_pane = LeftPane(container)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(0)
        # self.frame.setSizePolicy(size_policy)
        # self.frame.setMinimumSize(QSize(180, 600))
        # self.frame.setMaximumSize(QSize(400, 0))
        # self.frame.setSizeIncrement(QSize(10, 0))
        # self.frame.setBaseSize(QSize(200, 0))
        # self.frame.setFrameShape(QFrame.StyledPanel)
        # self.frame.setFrameShadow(QFrame.Raised)

        # container.setSizePolicy(size_policy)
        # container.setMinimumSize(QSize(180, 600))
        # container.setMaximumSize(QSize(400, 0))
        # h_splitter_1.addWidget(container)

        self.tabs = QTabWidget()
        self.right_pane = RightPane(self.tabs)
        size_policy.setHorizontalStretch(2)
        self.tabs.setSizePolicy(size_policy)
        self.tabs.setMinimumSize(QSize(600, 500))
        h_splitter_1.addWidget(self.tabs)

        self.tabs.currentChanged.connect(self.set_tab_focus)

        # Notes Tab Actions
        self.right_pane.font_combo_box.currentFontChanged.connect(
            self.set_notes_font
        )  #
        self.right_pane.font_spin_box.valueChanged.connect(self.set_notes_font_size)  #
        self.right_pane.colour_combo_box.currentTextChanged.connect(
            self.set_notes_font_colour
        )  #
        # tab indexes are 0 based
        self.tab_focus = {
            0: self.right_pane.tabTree,
            1: self.right_pane.tabSkills,
            2: self.right_pane.tabItems,
            3: self.right_pane.notes_text_edit,
        }

        self.central_window.setCentralWidget(h_splitter_1)
        main_win.setCentralWidget(self.central_window)
        main_win.setMenuBar(menubar)
        main_win.setStatusBar(statusbar)
        # setup_ui

    def set_tab_focus(self, index):
        self.tab_focus.get(index).setFocus()

    def set_recent_builds(self, config: Config):
        recent_builds = config.recentBuilds()
        for x in range(5):
            action = self.actions_recent_builds[x]
            if recent := recent_builds[f"r{x}"]:
                action.setVisible(True)
                action.setText(recent)
            else:
                action.setVisible(False)

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_size(self, size):
        self.right_pane.notes_text_edit.setFontPointSize(size)
        self.right_pane.notes_text_edit.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_colour(self, colour_name):
        if colour_name == "NORMAL":
            self.right_pane.notes_text_edit.setTextColor(self.defaultTextColour)
        else:
            self.right_pane.notes_text_edit.setTextColor(color_codes[colour_name])
        self.right_pane.notes_text_edit.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font(self):
        # action = self.sender()
        self.right_pane.notes_text_edit.setCurrentFont(
            self.right_pane.font_combo_box.currentFont()
        )
        self.right_pane.notes_text_edit.setFocus()

    # PoB_UI
