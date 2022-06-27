"""
Path of Building UI class

Sets up and connects UI components
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


class DockUI:
    """The ui class of dock window."""

    def setup_ui(self, win: QWidget) -> None:
        """Set up ui."""
        # Widgets
        left_dock = QDockWidget("Left dock")
        right_dock = QDockWidget("Right dock")
        top_dock = QDockWidget("Top dock")
        bottom_dock = QDockWidget("Bottom dock")

        # Setup widgets
        left_dock.setWidget(QTextEdit("This is the left widget."))
        right_dock.setWidget(QTextEdit("This is the right widget."))
        top_dock.setWidget(QTextEdit("This is the top widget."))
        bottom_dock.setWidget(QTextEdit("This is the bottom widget."))
        for dock in (left_dock, right_dock, top_dock, bottom_dock):
            dock.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea
                | Qt.DockWidgetArea.RightDockWidgetArea
                | Qt.DockWidgetArea.BottomDockWidgetArea
                | Qt.DockWidgetArea.TopDockWidgetArea
            )

        # Layout
        main_win = QMainWindow()
        main_win.setCentralWidget(QTextEdit("This is the central widget."))
        main_win.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)
        main_win.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
        main_win.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, top_dock)
        main_win.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

        layout = QVBoxLayout()
        layout.addWidget(main_win)
        layout.setContentsMargins(0, 0, 0, 0)


class RightPane:
    """The ui class of dock window."""

    def __init__(self, win: QTabWidget) -> None:

        # def setup_ui(self, win: QTabWidget) -> None:
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

        self.font_combo_box.currentFontChanged.connect(self.set_notes_font)
        self.font_spin_box.valueChanged.connect(self.set_notes_font_size)
        self.colour_combo_box.currentTextChanged.connect(self.set_notes_font_colour)
        # tab indexes are 0 based
        self.tab_focus = {
            0: self.tabTree,
            1: self.tabSkills,
            2: self.tabItems,
            3: self.notes_text_edit,
        }

    # build_notes_tab

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_size(self, size):
        self.notes_text_edit.setFontPointSize(size)
        self.notes_text_edit.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font_colour(self, colour_name):
        if colour_name == "NORMAL":
            self.notes_text_edit.setTextColor(self.defaultTextColour)
        else:
            self.notes_text_edit.setTextColor(color_codes[colour_name])
        self.notes_text_edit.setFocus()

    # don't use native signals/slot, so focus can be set back to edit box
    @Slot()
    def set_notes_font(self):
        action = self.sender()
        self.notes_text_edit.setCurrentFont(action.currentFont())
        self.notes_text_edit.setFocus()


class LeftPane:
    # def __init__(self) -> None:
    #     super().__init__("Build Info")
    def setup_ui(self, win: QWidget) -> None:
        # Widgets
        toolbox = QToolBox()
        # self.groupBox = QGroupBox(win)
        # self.groupBox.setGeometry(QRect(50, 70, 271, 80))
        label = QLabel()
        label.setGeometry(QRect(10, 30, 42, 22))
        toolbox.addItem(label, "Bandits:")
        comboBox = QComboBox()
        comboBox.setGeometry(QRect(60, 30, 150, 22))
        comboBox.setMinimumSize(QSize(350, 0))
        toolbox.addItem(comboBox, "Bandits comboBox")

        # slider = QSlider(Qt.Orientation.Horizontal)
        # dial_ticks = QDial()
        # progressbar = QProgressBar()
        # lcd_number = QLCDNumber()
        #
        # # Setup widgets
        # self.setCheckable(True)
        # toolbox.addItem(slider, "Slider")
        # toolbox.addItem(dial_ticks, "Dial")
        # toolbox.addItem(progressbar, "Progress Bar")
        # toolbox.addItem(lcd_number, "LCD Number")
        # slider.setValue(50)
        # dial_ticks.setNotchesVisible(True)
        # progressbar.setValue(50)
        # lcd_number.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        # lcd_number.display(123)
        #
        # # Layout
        # v_layout = QVBoxLayout(self)
        # v_layout.addWidget(toolbox)


class PoB_UI:
    def setup_ui(self, main_win: QMainWindow, config: Config):
        # ######################  STATUS BAR  ######################
        statusbar = QStatusBar()
        main_win.setStatusBar(statusbar)

        # ######################  MENU BAR  ######################
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

        # Next menu

        self.central_window = QMainWindow()

        h_splitter_1 = QSplitter(Qt.Orientation.Horizontal)
        h_splitter_1.setMinimumHeight(350)  # Fix bug layout crush

        # Layout
        container = QWidget()
        left_pane = LeftPane()
        left_pane.setup_ui(container)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        container.setSizePolicy(sizePolicy)
        container.setMinimumSize(QSize(180, 600))
        container.setMaximumSize(QSize(400, 0))
        h_splitter_1.addWidget(container)

        container = QTabWidget()
        right_pane = RightPane(container)
        # right_pane.setup_ui(container)
        sizePolicy.setHorizontalStretch(2)
        container.setSizePolicy(sizePolicy)
        container.setMinimumSize(QSize(600, 500))
        h_splitter_1.addWidget(container)

        # Notes Tab Actions
        # right_pane.font_combo_box.currentFontChanged.connect(
        #     right_pane.set_notes_font
        # )  #
        # right_pane.font_spin_box.valueChanged.connect(right_pane.set_notes_font_size)  #
        # right_pane.colour_combo_box.currentTextChanged.connect(
        #     right_pane.set_notes_font_colour
        # )  #
        # # tab indexes are 0 based
        # right_pane.tab_focus = {
        #     0: right_pane.tabTree,
        #     1: right_pane.tabSkills,
        #     2: right_pane.tabItems,
        #     3: right_pane.notes_text_edit,
        # }

        self.central_window.setCentralWidget(h_splitter_1)
        main_win.setCentralWidget(self.central_window)
        main_win.setMenuBar(menubar)
        main_win.setStatusBar(statusbar)
        # setup_ui

    def set_recent_builds(self, config: Config):
        recents = config.recentBuilds()
        for x in range(5):
            print(x)
            action = self.actions_recent_builds[x]
            recent = recents[format("r%d" % x)]
            if recent != "-":
                action.setVisible(True)
                action.setText(recent)
            else:
                action.setVisible(False)

    # PoB_UI
