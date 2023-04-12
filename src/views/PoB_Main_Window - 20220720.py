# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PoB_Main_Window - 20220720.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFontComboBox,
    QFormLayout,
    QFrame,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
import PoB_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1269, 765)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setWindowTitle("Path of Building")
        icon = QIcon()
        icon.addFile(":/Art/Icons/PathOfBuilding.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.action_New = QAction(MainWindow)
        self.action_New.setObjectName("action_New")
        icon1 = QIcon()
        iconThemeName = "appointment-new"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(
                ":/Art/Icons/add-folder.png", QSize(), QIcon.Normal, QIcon.Off
            )

        self.action_New.setIcon(icon1)
        self.action_Save = QAction(MainWindow)
        self.action_Save.setObjectName("action_Save")
        icon2 = QIcon()
        iconThemeName = "document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(
                ":/Art/Icons/downloads-folder.png", QSize(), QIcon.Normal, QIcon.Off
            )

        self.action_Save.setIcon(icon2)
        self.action_Exit = QAction(MainWindow)
        self.action_Exit.setObjectName("action_Exit")
        icon3 = QIcon()
        iconThemeName = "application-exit"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(
                ":/Art/Icons/door-open-out.png", QSize(), QIcon.Normal, QIcon.Off
            )

        self.action_Exit.setIcon(icon3)
        self.action_Open = QAction(MainWindow)
        self.action_Open.setObjectName("action_Open")
        icon4 = QIcon()
        icon4.addFile(":/Art/Icons/opened-folder.png", QSize(), QIcon.Normal, QIcon.Off)
        self.action_Open.setIcon(icon4)
        self.action_Theme = QAction(MainWindow)
        self.action_Theme.setObjectName("action_Theme")
        icon5 = QIcon()
        icon5.addFile(":/Art/Icons/yin-yang.png", QSize(), QIcon.Normal, QIcon.Off)
        self.action_Theme.setIcon(icon5)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainsplitter = QSplitter(self.centralwidget)
        self.mainsplitter.setObjectName("mainsplitter")
        self.mainsplitter.setAutoFillBackground(False)
        self.mainsplitter.setStyleSheet("")
        self.mainsplitter.setOrientation(Qt.Horizontal)
        self.frame = QFrame(self.mainsplitter)
        self.frame.setObjectName("frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(180, 600))
        self.frame.setMaximumSize(QSize(400, 2000))
        self.frame.setSizeIncrement(QSize(10, 0))
        self.frame.setBaseSize(QSize(200, 0))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.layoutWidget = QWidget(self.frame)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 170, 24))
        self.formLayout = QFormLayout(self.layoutWidget)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.bandit_label = QLabel(self.layoutWidget)
        self.bandit_label.setObjectName("bandit_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.bandit_label)

        self.bandit_comboBox = QComboBox(self.layoutWidget)
        self.bandit_comboBox.addItem("")
        self.bandit_comboBox.addItem("")
        self.bandit_comboBox.setObjectName("bandit_comboBox")
        self.bandit_comboBox.setMinimumSize(QSize(120, 0))
        self.bandit_comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.bandit_comboBox.setMinimumContentsLength(60)
        self.bandit_comboBox.setModelColumn(0)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.bandit_comboBox)

        self.comboBox = QComboBox(self.frame)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(60, 90, 111, 31))
        self.mainsplitter.addWidget(self.frame)
        self.tabWidget = QTabWidget(self.mainsplitter)
        self.tabWidget.setObjectName("tabWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tabWidget.setMinimumSize(QSize(600, 500))
        self.tabWidget.setStyleSheet("")
        self.tabTree = QWidget()
        self.tabTree.setObjectName("tabTree")
        self.horizontalLayout_2 = QHBoxLayout(self.tabTree)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.graphicsView = QGraphicsView(self.tabTree)
        self.graphicsView.setObjectName("graphicsView")

        self.horizontalLayout_2.addWidget(self.graphicsView)

        self.tabWidget.addTab(self.tabTree, "")
        self.tabSkills = QWidget()
        self.tabSkills.setObjectName("tabSkills")
        self.horizontalLayout_3 = QHBoxLayout(self.tabSkills)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_SkillsTabLeft = QFrame(self.tabSkills)
        self.frame_SkillsTabLeft.setObjectName("frame_SkillsTabLeft")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(4)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.frame_SkillsTabLeft.sizePolicy().hasHeightForWidth()
        )
        self.frame_SkillsTabLeft.setSizePolicy(sizePolicy2)
        self.frame_SkillsTabLeft.setFrameShape(QFrame.StyledPanel)
        self.frame_SkillsTabLeft.setFrameShadow(QFrame.Raised)
        self.label_SocketGroups = QLabel(self.frame_SkillsTabLeft)
        self.label_SocketGroups.setObjectName("label_SocketGroups")
        self.label_SocketGroups.setGeometry(QRect(10, 40, 100, 22))
        self.label_SkillSet = QLabel(self.frame_SkillsTabLeft)
        self.label_SkillSet.setObjectName("label_SkillSet")
        self.label_SkillSet.setGeometry(QRect(10, 10, 100, 22))
        self.combo_SkillSet = QComboBox(self.frame_SkillsTabLeft)
        self.combo_SkillSet.setObjectName("combo_SkillSet")
        self.combo_SkillSet.setGeometry(QRect(110, 10, 180, 22))
        self.btn_SkillsManage = QPushButton(self.frame_SkillsTabLeft)
        self.btn_SkillsManage.setObjectName("btn_SkillsManage")
        self.btn_SkillsManage.setGeometry(QRect(310, 10, 75, 22))
        self.btn_SkillsDelete = QPushButton(self.frame_SkillsTabLeft)
        self.btn_SkillsDelete.setObjectName("btn_SkillsDelete")
        self.btn_SkillsDelete.setGeometry(QRect(210, 40, 75, 22))
        self.btn_SkillsDeleteAll = QPushButton(self.frame_SkillsTabLeft)
        self.btn_SkillsDeleteAll.setObjectName("btn_SkillsDeleteAll")
        self.btn_SkillsDeleteAll.setGeometry(QRect(310, 40, 75, 22))
        self.btn_SkillsNew = QPushButton(self.frame_SkillsTabLeft)
        self.btn_SkillsNew.setObjectName("btn_SkillsNew")
        self.btn_SkillsNew.setGeometry(QRect(110, 40, 75, 22))
        self.list_Skills = QListWidget(self.frame_SkillsTabLeft)
        self.list_Skills.setObjectName("list_Skills")
        self.list_Skills.setGeometry(QRect(10, 70, 375, 311))
        self.label_Usage_Hints = QLabel(self.frame_SkillsTabLeft)
        self.label_Usage_Hints.setObjectName("label_Usage_Hints")
        self.label_Usage_Hints.setGeometry(QRect(10, 385, 375, 91))
        self.label_Usage_Hints.setScaledContents(True)
        self.group_SkillTabLeft = QGroupBox(self.frame_SkillsTabLeft)
        self.group_SkillTabLeft.setObjectName("group_SkillTabLeft")
        self.group_SkillTabLeft.setGeometry(QRect(0, 480, 400, 165))
        self.group_SkillTabLeft.setMinimumSize(QSize(375, 165))
        self.label = QLabel(self.group_SkillTabLeft)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 15, 170, 22))
        self.label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_2 = QLabel(self.group_SkillTabLeft)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(10, 40, 170, 22))
        self.label_2.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_3 = QLabel(self.group_SkillTabLeft)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(10, 65, 170, 22))
        self.label_3.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_4 = QLabel(self.group_SkillTabLeft)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(10, 90, 170, 22))
        self.label_4.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_5 = QLabel(self.group_SkillTabLeft)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(10, 115, 170, 22))
        self.label_5.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_6 = QLabel(self.group_SkillTabLeft)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(10, 140, 170, 22))
        self.label_6.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.comboBox_2 = QComboBox(self.group_SkillTabLeft)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.setGeometry(QRect(220, 15, 171, 22))
        self.check_MatchToLevel = QCheckBox(self.group_SkillTabLeft)
        self.check_MatchToLevel.setObjectName("check_MatchToLevel")
        self.check_MatchToLevel.setGeometry(QRect(190, 40, 75, 20))
        self.spin_DefaultGemLevel = QSpinBox(self.group_SkillTabLeft)
        self.spin_DefaultGemLevel.setObjectName("spin_DefaultGemLevel")
        self.spin_DefaultGemLevel.setGeometry(QRect(190, 65, 42, 22))
        self.spin_DefaultGemLevel.setMinimum(1)
        self.spin_DefaultGemLevel.setMaximum(20)
        self.spin_DefaultGemQuality = QSpinBox(self.group_SkillTabLeft)
        self.spin_DefaultGemQuality.setObjectName("spin_DefaultGemQuality")
        self.spin_DefaultGemQuality.setGeometry(QRect(190, 90, 42, 22))
        self.spin_DefaultGemQuality.setMaximum(20)
        self.combo_ShowSupportGems = QComboBox(self.group_SkillTabLeft)
        self.combo_ShowSupportGems.setObjectName("combo_ShowSupportGems")
        self.combo_ShowSupportGems.setGeometry(QRect(190, 115, 202, 22))
        self.check_ShowGemQualityVariants = QCheckBox(self.group_SkillTabLeft)
        self.check_ShowGemQualityVariants.setObjectName("check_ShowGemQualityVariants")
        self.check_ShowGemQualityVariants.setGeometry(QRect(190, 140, 75, 20))
        self.check_SortByDPS = QCheckBox(self.group_SkillTabLeft)
        self.check_SortByDPS.setObjectName("check_SortByDPS")
        self.check_SortByDPS.setGeometry(QRect(190, 15, 75, 20))

        self.horizontalLayout_3.addWidget(self.frame_SkillsTabLeft)

        self.frame_SkillsTabRight = QFrame(self.tabSkills)
        self.frame_SkillsTabRight.setObjectName("frame_SkillsTabRight")
        self.frame_SkillsTabRight.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(5)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.frame_SkillsTabRight.sizePolicy().hasHeightForWidth()
        )
        self.frame_SkillsTabRight.setSizePolicy(sizePolicy3)
        self.frame_SkillsTabRight.setFrameShape(QFrame.StyledPanel)
        self.frame_SkillsTabRight.setFrameShadow(QFrame.Raised)
        self.label_SkillLabel = QLabel(self.frame_SkillsTabRight)
        self.label_SkillLabel.setObjectName("label_SkillLabel")
        self.label_SkillLabel.setGeometry(QRect(10, 10, 61, 22))
        self.lineEdit_SkillLabel = QLineEdit(self.frame_SkillsTabRight)
        self.lineEdit_SkillLabel.setObjectName("lineEdit_SkillLabel")
        self.lineEdit_SkillLabel.setGeometry(QRect(80, 10, 391, 22))
        self.widget = QWidget(self.frame_SkillsTabRight)
        self.widget.setObjectName("widget")
        self.widget.setGeometry(QRect(0, 100, 500, 40))
        self.check_GemEnabled1 = QCheckBox(self.widget)
        self.check_GemEnabled1.setObjectName("check_GemEnabled1")
        self.check_GemEnabled1.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemEnabled1.setChecked(True)
        self.combo_GemList1 = QComboBox(self.widget)
        self.combo_GemList1.setObjectName("combo_GemList1")
        self.combo_GemList1.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel1 = QSpinBox(self.widget)
        self.spin_GemLevel1.setObjectName("spin_GemLevel1")
        self.spin_GemLevel1.setGeometry(QRect(210, 10, 42, 22))
        self.spin_GemLevel1.setMinimum(1)
        self.spin_GemLevel1.setMaximum(20)
        self.spin_GemQuality1 = QSpinBox(self.widget)
        self.spin_GemQuality1.setObjectName("spin_GemQuality1")
        self.spin_GemQuality1.setGeometry(QRect(260, 10, 42, 22))
        self.spin_GemQuality1.setMaximum(20)
        self.combo_GemVariant1 = QComboBox(self.widget)
        self.combo_GemVariant1.addItem("")
        self.combo_GemVariant1.addItem("")
        self.combo_GemVariant1.setObjectName("combo_GemVariant1")
        self.combo_GemVariant1.setGeometry(QRect(310, 10, 81, 22))
        self.check_GemEnabled1_2 = QCheckBox(self.widget)
        self.check_GemEnabled1_2.setObjectName("check_GemEnabled1_2")
        self.check_GemEnabled1_2.setGeometry(QRect(415, 10, 20, 20))
        self.check_GemEnabled1_2.setChecked(True)
        self.spin_GemCount1 = QSpinBox(self.widget)
        self.spin_GemCount1.setObjectName("spin_GemCount1")
        self.spin_GemCount1.setGeometry(QRect(450, 10, 42, 22))
        self.spin_GemCount1.setMinimum(1)
        self.spin_GemCount1.setMaximum(20)
        self.label_SocketedIn = QLabel(self.frame_SkillsTabRight)
        self.label_SocketedIn.setObjectName("label_SocketedIn")
        self.label_SocketedIn.setGeometry(QRect(10, 40, 71, 22))
        self.combo_SocketedIn = QComboBox(self.frame_SkillsTabRight)
        self.combo_SocketedIn.setObjectName("combo_SocketedIn")
        self.combo_SocketedIn.setGeometry(QRect(80, 40, 171, 22))
        self.check_SocketGroupEnabled = QCheckBox(self.frame_SkillsTabRight)
        self.check_SocketGroupEnabled.setObjectName("check_SocketGroupEnabled")
        self.check_SocketGroupEnabled.setGeometry(QRect(260, 40, 75, 20))
        self.check_SocketGroupEnabled.setChecked(False)
        self.check_SocketGroup_FullDPS = QCheckBox(self.frame_SkillsTabRight)
        self.check_SocketGroup_FullDPS.setObjectName("check_SocketGroup_FullDPS")
        self.check_SocketGroup_FullDPS.setGeometry(QRect(350, 40, 121, 20))
        self.check_SocketGroup_FullDPS.setChecked(False)
        self.label_GemName = QLabel(self.frame_SkillsTabRight)
        self.label_GemName.setObjectName("label_GemName")
        self.label_GemName.setGeometry(QRect(30, 80, 70, 22))
        self.label_Level = QLabel(self.frame_SkillsTabRight)
        self.label_Level.setObjectName("label_Level")
        self.label_Level.setGeometry(QRect(210, 80, 40, 22))
        self.label_Variant = QLabel(self.frame_SkillsTabRight)
        self.label_Variant.setObjectName("label_Variant")
        self.label_Variant.setGeometry(QRect(310, 80, 40, 22))
        self.label_Enabled = QLabel(self.frame_SkillsTabRight)
        self.label_Enabled.setObjectName("label_Enabled")
        self.label_Enabled.setGeometry(QRect(400, 80, 41, 22))
        self.label_Count = QLabel(self.frame_SkillsTabRight)
        self.label_Count.setObjectName("label_Count")
        self.label_Count.setGeometry(QRect(450, 80, 40, 22))
        self.label_Quality = QLabel(self.frame_SkillsTabRight)
        self.label_Quality.setObjectName("label_Quality")
        self.label_Quality.setGeometry(QRect(260, 80, 40, 22))
        self.widget_3 = QWidget(self.frame_SkillsTabRight)
        self.widget_3.setObjectName("widget_3")
        self.widget_3.setGeometry(QRect(0, 160, 500, 40))
        self.check_GemEnabled3 = QCheckBox(self.widget_3)
        self.check_GemEnabled3.setObjectName("check_GemEnabled3")
        self.check_GemEnabled3.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemEnabled3.setChecked(True)
        self.combo_GemList3 = QComboBox(self.widget_3)
        self.combo_GemList3.setObjectName("combo_GemList3")
        self.combo_GemList3.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel3 = QSpinBox(self.widget_3)
        self.spin_GemLevel3.setObjectName("spin_GemLevel3")
        self.spin_GemLevel3.setGeometry(QRect(210, 10, 42, 22))
        self.spin_GemLevel3.setMinimum(1)
        self.spin_GemLevel3.setMaximum(20)
        self.spin_GemQuality3 = QSpinBox(self.widget_3)
        self.spin_GemQuality3.setObjectName("spin_GemQuality3")
        self.spin_GemQuality3.setGeometry(QRect(260, 10, 42, 22))
        self.spin_GemQuality3.setMaximum(20)
        self.combo_GemVariant3 = QComboBox(self.widget_3)
        self.combo_GemVariant3.addItem("")
        self.combo_GemVariant3.addItem("")
        self.combo_GemVariant3.setObjectName("combo_GemVariant3")
        self.combo_GemVariant3.setGeometry(QRect(310, 10, 81, 22))
        self.check_GemEnabled3_2 = QCheckBox(self.widget_3)
        self.check_GemEnabled3_2.setObjectName("check_GemEnabled3_2")
        self.check_GemEnabled3_2.setGeometry(QRect(415, 10, 20, 20))
        self.check_GemEnabled3_2.setChecked(True)
        self.spin_GemCount3 = QSpinBox(self.widget_3)
        self.spin_GemCount3.setObjectName("spin_GemCount3")
        self.spin_GemCount3.setGeometry(QRect(450, 10, 42, 22))
        self.spin_GemCount3.setMinimum(1)
        self.spin_GemCount3.setMaximum(20)
        self.widget_2 = QWidget(self.frame_SkillsTabRight)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setGeometry(QRect(0, 130, 500, 40))
        self.check_GemEnabled2 = QCheckBox(self.widget_2)
        self.check_GemEnabled2.setObjectName("check_GemEnabled2")
        self.check_GemEnabled2.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemEnabled2.setChecked(True)
        self.combo_GemList2 = QComboBox(self.widget_2)
        self.combo_GemList2.setObjectName("combo_GemList2")
        self.combo_GemList2.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel2 = QSpinBox(self.widget_2)
        self.spin_GemLevel2.setObjectName("spin_GemLevel2")
        self.spin_GemLevel2.setGeometry(QRect(210, 10, 42, 22))
        self.spin_GemLevel2.setMinimum(1)
        self.spin_GemLevel2.setMaximum(20)
        self.spin_GemQuality2 = QSpinBox(self.widget_2)
        self.spin_GemQuality2.setObjectName("spin_GemQuality2")
        self.spin_GemQuality2.setGeometry(QRect(260, 10, 42, 22))
        self.spin_GemQuality2.setMaximum(20)
        self.combo_GemVariant2 = QComboBox(self.widget_2)
        self.combo_GemVariant2.addItem("")
        self.combo_GemVariant2.addItem("")
        self.combo_GemVariant2.setObjectName("combo_GemVariant2")
        self.combo_GemVariant2.setGeometry(QRect(310, 10, 81, 22))
        self.check_GemEnabled2_2 = QCheckBox(self.widget_2)
        self.check_GemEnabled2_2.setObjectName("check_GemEnabled2_2")
        self.check_GemEnabled2_2.setGeometry(QRect(415, 10, 20, 20))
        self.check_GemEnabled2_2.setChecked(True)
        self.spin_GemCount2 = QSpinBox(self.widget_2)
        self.spin_GemCount2.setObjectName("spin_GemCount2")
        self.spin_GemCount2.setGeometry(QRect(450, 10, 42, 22))
        self.spin_GemCount2.setMinimum(1)
        self.spin_GemCount2.setMaximum(20)
        self.widget_4 = QWidget(self.frame_SkillsTabRight)
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setGeometry(QRect(0, 190, 500, 40))
        self.check_GemEnabled4 = QCheckBox(self.widget_4)
        self.check_GemEnabled4.setObjectName("check_GemEnabled4")
        self.check_GemEnabled4.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemEnabled4.setChecked(True)
        self.combo_GemList4 = QComboBox(self.widget_4)
        self.combo_GemList4.setObjectName("combo_GemList4")
        self.combo_GemList4.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel4 = QSpinBox(self.widget_4)
        self.spin_GemLevel4.setObjectName("spin_GemLevel4")
        self.spin_GemLevel4.setGeometry(QRect(210, 10, 42, 22))
        self.spin_GemLevel4.setMinimum(1)
        self.spin_GemLevel4.setMaximum(20)
        self.spin_GemQuality4 = QSpinBox(self.widget_4)
        self.spin_GemQuality4.setObjectName("spin_GemQuality4")
        self.spin_GemQuality4.setGeometry(QRect(260, 10, 42, 22))
        self.spin_GemQuality4.setMaximum(20)
        self.combo_GemVariant4 = QComboBox(self.widget_4)
        self.combo_GemVariant4.addItem("")
        self.combo_GemVariant4.addItem("")
        self.combo_GemVariant4.setObjectName("combo_GemVariant4")
        self.combo_GemVariant4.setGeometry(QRect(310, 10, 81, 22))
        self.check_GemEnabled4_2 = QCheckBox(self.widget_4)
        self.check_GemEnabled4_2.setObjectName("check_GemEnabled4_2")
        self.check_GemEnabled4_2.setGeometry(QRect(415, 10, 20, 20))
        self.check_GemEnabled4_2.setChecked(True)
        self.spin_GemCount4 = QSpinBox(self.widget_4)
        self.spin_GemCount4.setObjectName("spin_GemCount4")
        self.spin_GemCount4.setGeometry(QRect(450, 10, 42, 22))
        self.spin_GemCount4.setMinimum(1)
        self.spin_GemCount4.setMaximum(20)
        self.widget_5 = QWidget(self.frame_SkillsTabRight)
        self.widget_5.setObjectName("widget_5")
        self.widget_5.setGeometry(QRect(0, 220, 500, 40))
        self.check_GemEnabled5 = QCheckBox(self.widget_5)
        self.check_GemEnabled5.setObjectName("check_GemEnabled5")
        self.check_GemEnabled5.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemEnabled5.setChecked(True)
        self.combo_GemList5 = QComboBox(self.widget_5)
        self.combo_GemList5.setObjectName("combo_GemList5")
        self.combo_GemList5.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel5 = QSpinBox(self.widget_5)
        self.spin_GemLevel5.setObjectName("spin_GemLevel5")
        self.spin_GemLevel5.setGeometry(QRect(210, 10, 42, 22))
        self.spin_GemLevel5.setMinimum(1)
        self.spin_GemLevel5.setMaximum(20)
        self.spin_GemQuality5 = QSpinBox(self.widget_5)
        self.spin_GemQuality5.setObjectName("spin_GemQuality5")
        self.spin_GemQuality5.setGeometry(QRect(260, 10, 42, 22))
        self.spin_GemQuality5.setMaximum(20)
        self.combo_GemVariant5 = QComboBox(self.widget_5)
        self.combo_GemVariant5.addItem("")
        self.combo_GemVariant5.addItem("")
        self.combo_GemVariant5.setObjectName("combo_GemVariant5")
        self.combo_GemVariant5.setGeometry(QRect(310, 10, 81, 22))
        self.check_GemEnabled5_2 = QCheckBox(self.widget_5)
        self.check_GemEnabled5_2.setObjectName("check_GemEnabled5_2")
        self.check_GemEnabled5_2.setGeometry(QRect(415, 10, 20, 20))
        self.check_GemEnabled5_2.setChecked(True)
        self.spin_GemCount5 = QSpinBox(self.widget_5)
        self.spin_GemCount5.setObjectName("spin_GemCount5")
        self.spin_GemCount5.setGeometry(QRect(450, 10, 42, 22))
        self.spin_GemCount5.setMinimum(1)
        self.spin_GemCount5.setMaximum(20)
        self.widget_6 = QWidget(self.frame_SkillsTabRight)
        self.widget_6.setObjectName("widget_6")
        self.widget_6.setGeometry(QRect(0, 250, 500, 40))
        self.check_GemEnabled6 = QCheckBox(self.widget_6)
        self.check_GemEnabled6.setObjectName("check_GemEnabled6")
        self.check_GemEnabled6.setGeometry(QRect(10, 10, 20, 20))
        self.check_GemEnabled6.setChecked(True)
        self.combo_GemList6 = QComboBox(self.widget_6)
        self.combo_GemList6.setObjectName("combo_GemList6")
        self.combo_GemList6.setGeometry(QRect(30, 10, 171, 22))
        self.spin_GemLevel6 = QSpinBox(self.widget_6)
        self.spin_GemLevel6.setObjectName("spin_GemLevel6")
        self.spin_GemLevel6.setGeometry(QRect(210, 10, 42, 22))
        self.spin_GemLevel6.setMinimum(1)
        self.spin_GemLevel6.setMaximum(20)
        self.spin_GemQuality6 = QSpinBox(self.widget_6)
        self.spin_GemQuality6.setObjectName("spin_GemQuality6")
        self.spin_GemQuality6.setGeometry(QRect(260, 10, 42, 22))
        self.spin_GemQuality6.setMaximum(20)
        self.combo_GemVariant6 = QComboBox(self.widget_6)
        self.combo_GemVariant6.addItem("")
        self.combo_GemVariant6.addItem("")
        self.combo_GemVariant6.setObjectName("combo_GemVariant6")
        self.combo_GemVariant6.setGeometry(QRect(310, 10, 81, 22))
        self.check_GemEnabled6_2 = QCheckBox(self.widget_6)
        self.check_GemEnabled6_2.setObjectName("check_GemEnabled6_2")
        self.check_GemEnabled6_2.setGeometry(QRect(415, 10, 20, 20))
        self.check_GemEnabled6_2.setChecked(True)
        self.spin_GemCount6 = QSpinBox(self.widget_6)
        self.spin_GemCount6.setObjectName("spin_GemCount6")
        self.spin_GemCount6.setGeometry(QRect(450, 10, 42, 22))
        self.spin_GemCount6.setMinimum(1)
        self.spin_GemCount6.setMaximum(20)

        self.horizontalLayout_3.addWidget(self.frame_SkillsTabRight)

        self.tabWidget.addTab(self.tabSkills, "")
        self.tabItems = QWidget()
        self.tabItems.setObjectName("tabItems")
        self.tabWidget.addTab(self.tabItems, "")
        self.tabNotes = QWidget()
        self.tabNotes.setObjectName("tabNotes")
        self.verticalLayout = QVBoxLayout(self.tabNotes)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.combo_Notes_Font = QFontComboBox(self.tabNotes)
        self.combo_Notes_Font.setObjectName("combo_Notes_Font")
        self.combo_Notes_Font.setMinimumSize(QSize(200, 0))
        self.combo_Notes_Font.setEditable(False)

        self.horizontalLayout_4.addWidget(self.combo_Notes_Font)

        self.spin_Notes_FontSize = QSpinBox(self.tabNotes)
        self.spin_Notes_FontSize.setObjectName("spin_Notes_FontSize")
        self.spin_Notes_FontSize.setMinimumSize(QSize(35, 0))
        self.spin_Notes_FontSize.setMinimum(3)
        self.spin_Notes_FontSize.setMaximum(50)
        self.spin_Notes_FontSize.setValue(15)

        self.horizontalLayout_4.addWidget(self.spin_Notes_FontSize)

        self.combo_Notes_Colour = QComboBox(self.tabNotes)
        self.combo_Notes_Colour.setObjectName("combo_Notes_Colour")
        self.combo_Notes_Colour.setMinimumSize(QSize(140, 0))

        self.horizontalLayout_4.addWidget(self.combo_Notes_Colour)

        self.horizontalSpacer = QSpacerItem(
            90, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.textEdit_Notes = QTextEdit(self.tabNotes)
        self.textEdit_Notes.setObjectName("textEdit_Notes")
        self.textEdit_Notes.setLineWrapMode(QTextEdit.NoWrap)

        self.verticalLayout.addWidget(self.textEdit_Notes)

        self.tabWidget.addTab(self.tabNotes, "")
        self.mainsplitter.addWidget(self.tabWidget)

        self.horizontalLayout.addWidget(self.mainsplitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 600, 22))
        self.menubar.setMinimumSize(QSize(400, 0))
        self.menubar.setMaximumSize(QSize(600, 24))
        self.menu_Builds = QMenu(self.menubar)
        self.menu_Builds.setObjectName("menu_Builds")
        self.menu_View = QMenu(self.menubar)
        self.menu_View.setObjectName("menu_View")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setEnabled(True)
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_Builds.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menu_Builds.addAction(self.action_New)
        self.menu_Builds.addAction(self.action_Open)
        self.menu_Builds.addAction(self.action_Save)
        self.menu_Builds.addSeparator()
        self.menu_Builds.addAction(self.action_Exit)
        self.menu_Builds.addSeparator()
        self.menu_View.addAction(self.action_Theme)
        self.toolBar.addAction(self.action_New)
        self.toolBar.addAction(self.action_Open)
        self.toolBar.addAction(self.action_Save)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_Theme)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        self.action_Exit.triggered.connect(MainWindow.close)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        self.action_New.setText(QCoreApplication.translate("MainWindow", "New", None))
        # if QT_CONFIG(tooltip)
        self.action_New.setToolTip(
            QCoreApplication.translate("MainWindow", "Start a new build", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.action_New.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+N", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.action_Save.setText(QCoreApplication.translate("MainWindow", "Save", None))
        # if QT_CONFIG(tooltip)
        self.action_Save.setToolTip(
            QCoreApplication.translate("MainWindow", "Save this build", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.action_Save.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.action_Exit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        # if QT_CONFIG(tooltip)
        self.action_Exit.setToolTip(
            QCoreApplication.translate("MainWindow", "Exit Path of Building", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.action_Exit.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+X", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.action_Open.setText(QCoreApplication.translate("MainWindow", "Open", None))
        # if QT_CONFIG(shortcut)
        self.action_Open.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+O", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.action_Theme.setText(
            QCoreApplication.translate("MainWindow", "Light", None)
        )
        # if QT_CONFIG(tooltip)
        self.action_Theme.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Change the theme between the light and the dark", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(whatsthis)
        self.action_Theme.setWhatsThis(
            QCoreApplication.translate("MainWindow", "light", None)
        )
        # endif // QT_CONFIG(whatsthis)
        self.bandit_label.setText(
            QCoreApplication.translate("MainWindow", "Bandits:", None)
        )
        self.bandit_comboBox.setItemText(
            0, QCoreApplication.translate("MainWindow", "2 Passives Points", None)
        )
        self.bandit_comboBox.setItemText(
            1,
            QCoreApplication.translate(
                "MainWindow", "Oak (Life Regen, Phys.Dmg. Reduction, Phys.Dmg)", None
            ),
        )

        self.bandit_comboBox.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Make  a Selection", None)
        )
        # if QT_CONFIG(accessibility)
        self.tabWidget.setAccessibleName("")
        # endif // QT_CONFIG(accessibility)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabTree),
            QCoreApplication.translate("MainWindow", "&Tree", None),
        )
        self.label_SocketGroups.setText(
            QCoreApplication.translate("MainWindow", "Socket Groups:", None)
        )
        self.label_SkillSet.setText(
            QCoreApplication.translate("MainWindow", "Skill Set: ", None)
        )
        self.btn_SkillsManage.setText(
            QCoreApplication.translate("MainWindow", "Manage", None)
        )
        self.btn_SkillsDelete.setText(
            QCoreApplication.translate("MainWindow", "Delete", None)
        )
        self.btn_SkillsDeleteAll.setText(
            QCoreApplication.translate("MainWindow", "Delete All", None)
        )
        self.btn_SkillsNew.setText(
            QCoreApplication.translate("MainWindow", "New", None)
        )
        self.label_Usage_Hints.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><span style=" font-size:9pt;">Usage Hints:<br>- You can copy/paste socket groups using Ctrl-C and Ctrl-V.<br>- Ctrl-Left click to enable and disable socket groups.<br>- Ctrl-Right click to include/exclude in FullDPS calculations.<br>- Right click to set as the Main skill group.</span></body></html>',
                None,
            )
        )
        self.group_SkillTabLeft.setTitle(
            QCoreApplication.translate("MainWindow", "Gem Options", None)
        )
        self.label.setText(
            QCoreApplication.translate("MainWindow", "Sort Gems by DPS", None)
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "MainWindow", "Match Gems to Character Level", None
            )
        )
        self.label_3.setText(
            QCoreApplication.translate("MainWindow", "Default Gem Level", None)
        )
        self.label_4.setText(
            QCoreApplication.translate("MainWindow", "Default Gem Quality", None)
        )
        self.label_5.setText(
            QCoreApplication.translate("MainWindow", "Show Support Gems", None)
        )
        self.label_6.setText(
            QCoreApplication.translate("MainWindow", "Show Gem Quality Variants", None)
        )
        self.check_MatchToLevel.setText("")
        self.check_ShowGemQualityVariants.setText("")
        self.check_SortByDPS.setText("")
        self.label_SkillLabel.setText(
            QCoreApplication.translate("MainWindow", "Skill Label:", None)
        )
        self.check_GemEnabled1.setText("")
        self.combo_GemVariant1.setItemText(
            0, QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.combo_GemVariant1.setItemText(
            1, QCoreApplication.translate("MainWindow", "Anomolous", None)
        )

        self.check_GemEnabled1_2.setText("")
        self.label_SocketedIn.setText(
            QCoreApplication.translate("MainWindow", "Socketed In:", None)
        )
        self.check_SocketGroupEnabled.setText(
            QCoreApplication.translate("MainWindow", "Enabled", None)
        )
        self.check_SocketGroup_FullDPS.setText(
            QCoreApplication.translate("MainWindow", "Include in Full DPS", None)
        )
        self.label_GemName.setText(
            QCoreApplication.translate("MainWindow", "Gem Name:", None)
        )
        self.label_Level.setText(
            QCoreApplication.translate("MainWindow", "Level:", None)
        )
        self.label_Variant.setText(
            QCoreApplication.translate("MainWindow", "Variant", None)
        )
        self.label_Enabled.setText(
            QCoreApplication.translate("MainWindow", "Enabled", None)
        )
        self.label_Count.setText(
            QCoreApplication.translate("MainWindow", "Count", None)
        )
        self.label_Quality.setText(
            QCoreApplication.translate("MainWindow", "Quality", None)
        )
        self.check_GemEnabled3.setText("")
        self.combo_GemVariant3.setItemText(
            0, QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.combo_GemVariant3.setItemText(
            1, QCoreApplication.translate("MainWindow", "Anomolous", None)
        )

        self.check_GemEnabled3_2.setText("")
        self.check_GemEnabled2.setText("")
        self.combo_GemVariant2.setItemText(
            0, QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.combo_GemVariant2.setItemText(
            1, QCoreApplication.translate("MainWindow", "Anomolous", None)
        )

        self.check_GemEnabled2_2.setText("")
        self.check_GemEnabled4.setText("")
        self.combo_GemVariant4.setItemText(
            0, QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.combo_GemVariant4.setItemText(
            1, QCoreApplication.translate("MainWindow", "Anomolous", None)
        )

        self.check_GemEnabled4_2.setText("")
        self.check_GemEnabled5.setText("")
        self.combo_GemVariant5.setItemText(
            0, QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.combo_GemVariant5.setItemText(
            1, QCoreApplication.translate("MainWindow", "Anomolous", None)
        )

        self.check_GemEnabled5_2.setText("")
        self.check_GemEnabled6.setText("")
        self.combo_GemVariant6.setItemText(
            0, QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.combo_GemVariant6.setItemText(
            1, QCoreApplication.translate("MainWindow", "Anomolous", None)
        )

        self.check_GemEnabled6_2.setText("")
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabSkills),
            QCoreApplication.translate("MainWindow", "&Skills", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabItems),
            QCoreApplication.translate("MainWindow", "&Items", None),
        )
        self.combo_Notes_Font.setCurrentText(
            QCoreApplication.translate("MainWindow", "Times New Roman", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabNotes),
            QCoreApplication.translate("MainWindow", "&Notes", None),
        )
        self.menu_Builds.setTitle(
            QCoreApplication.translate("MainWindow", "&Builds", None)
        )
        self.menu_View.setTitle(QCoreApplication.translate("MainWindow", "&View", None))
        self.toolBar.setWindowTitle(
            QCoreApplication.translate("MainWindow", "toolBar", None)
        )
        pass

    # retranslateUi
