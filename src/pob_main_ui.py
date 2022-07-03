# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setWindowTitle("Path of Building")
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        icon = QIcon()
        iconThemeName = "application-exit"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionExit.setIcon(icon)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionTree = QAction(MainWindow)
        self.actionTree.setObjectName("actionTree")
        self.actionTree.setEnabled(True)
        self.actionTree.setAutoRepeat(False)
        self.actionTree.setVisible(True)
        self.actionSkills = QAction(MainWindow)
        self.actionSkills.setObjectName("actionSkills")
        self.actionSkills.setEnabled(True)
        self.actionSkills.setAutoRepeat(False)
        self.actionSkills.setVisible(True)
        self.actionItems = QAction(MainWindow)
        self.actionItems.setObjectName("actionItems")
        self.actionItems.setEnabled(True)
        self.actionItems.setAutoRepeat(False)
        self.actionItems.setVisible(True)
        self.actionNotes = QAction(MainWindow)
        self.actionNotes.setObjectName("actionNotes")
        self.actionNotes.setEnabled(True)
        self.actionNotes.setAutoRepeat(False)
        self.actionNotes.setVisible(True)
        self.actionFive = QAction(MainWindow)
        self.actionFive.setObjectName("actionFive")
        self.actionLight = QAction(MainWindow)
        self.actionLight.setObjectName("actionLight")
        self.actionDark = QAction(MainWindow)
        self.actionDark.setObjectName("actionDark")
        self.actionFusion = QAction(MainWindow)
        self.actionFusion.setObjectName("actionFusion")
        self.actionStandard = QAction(MainWindow)
        self.actionStandard.setObjectName("actionStandard")
        self.actionDarcula = QAction(MainWindow)
        self.actionDarcula.setObjectName("actionDarcula")
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
        self.widget = QWidget(self.frame)
        self.widget.setObjectName("widget")
        self.widget.setGeometry(QRect(10, 10, 150, 24))
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.comboBox = QComboBox(self.widget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setMinimumSize(QSize(100, 0))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox)

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
        self.tabWidget.addTab(self.tabTree, "")
        self.tabSkills = QWidget()
        self.tabSkills.setObjectName("tabSkills")
        self.tabWidget.addTab(self.tabSkills, "")
        self.tabItems = QWidget()
        self.tabItems.setObjectName("tabItems")
        self.tabWidget.addTab(self.tabItems, "")
        self.mainsplitter.addWidget(self.tabWidget)

        self.horizontalLayout.addWidget(self.mainsplitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 600, 22))
        self.menubar.setMinimumSize(QSize(400, 0))
        self.menubar.setMaximumSize(QSize(600, 24))
        self.menuWidget = QMenu(self.menubar)
        self.menuWidget.setObjectName("menuWidget")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setEnabled(True)
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuWidget.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menuWidget.addAction(self.actionNew)
        self.menuWidget.addAction(self.actionOpen)
        self.menuWidget.addAction(self.actionSave)
        self.menuWidget.addSeparator()
        self.menuWidget.addAction(self.actionExit)
        self.menuWidget.addSeparator()
        self.menuView.addAction(self.actionLight)
        self.menuView.addAction(self.actionDark)
        self.menuView.addAction(self.actionStandard)
        self.menuView.addAction(self.actionDarcula)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        self.actionNew.setText(QCoreApplication.translate("MainWindow", "New", None))
        # if QT_CONFIG(tooltip)
        self.actionNew.setToolTip(
            QCoreApplication.translate("MainWindow", "Start a new build", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+N", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Save", None))
        # if QT_CONFIG(tooltip)
        self.actionSave.setToolTip(
            QCoreApplication.translate("MainWindow", "Save this build", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        # if QT_CONFIG(tooltip)
        self.actionExit.setToolTip(
            QCoreApplication.translate("MainWindow", "Exit Path of Building", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+X", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", "Open", None))
        # if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+O", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionTree.setText(QCoreApplication.translate("MainWindow", "Tree", None))
        # if QT_CONFIG(tooltip)
        self.actionTree.setToolTip(
            QCoreApplication.translate("MainWindow", "Switch Tabs", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionTree.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+1", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionSkills.setText(
            QCoreApplication.translate("MainWindow", "Skills", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionSkills.setToolTip(
            QCoreApplication.translate("MainWindow", "Switch Tabs", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionSkills.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+2", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionItems.setText(
            QCoreApplication.translate("MainWindow", "Items", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionItems.setToolTip(
            QCoreApplication.translate("MainWindow", "Switch Tabs", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionItems.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+3", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionNotes.setText(
            QCoreApplication.translate("MainWindow", "Notes", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionNotes.setToolTip(
            QCoreApplication.translate("MainWindow", "Switch Tabs", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionNotes.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+4", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionFive.setText(QCoreApplication.translate("MainWindow", "Five", None))
        # if QT_CONFIG(shortcut)
        self.actionFive.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+5", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionLight.setText(
            QCoreApplication.translate("MainWindow", "Light", None)
        )
        # if QT_CONFIG(whatsthis)
        self.actionLight.setWhatsThis(
            QCoreApplication.translate("MainWindow", "light", None)
        )
        # endif // QT_CONFIG(whatsthis)
        self.actionDark.setText(QCoreApplication.translate("MainWindow", "Dark", None))
        # if QT_CONFIG(whatsthis)
        self.actionDark.setWhatsThis(
            QCoreApplication.translate("MainWindow", "dark", None)
        )
        # endif // QT_CONFIG(whatsthis)
        self.actionFusion.setText(
            QCoreApplication.translate("MainWindow", "Fusion", None)
        )
        # if QT_CONFIG(whatsthis)
        self.actionFusion.setWhatsThis(
            QCoreApplication.translate("MainWindow", "Fusion", None)
        )
        # endif // QT_CONFIG(whatsthis)
        self.actionStandard.setText(
            QCoreApplication.translate("MainWindow", "Standard", None)
        )
        # if QT_CONFIG(whatsthis)
        self.actionStandard.setWhatsThis("")
        # endif // QT_CONFIG(whatsthis)
        # if QT_CONFIG(shortcut)
        self.actionStandard.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+0", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionDarcula.setText(
            QCoreApplication.translate("MainWindow", "Dracula", None)
        )
        # if QT_CONFIG(whatsthis)
        self.actionDarcula.setWhatsThis(
            QCoreApplication.translate("MainWindow", "Windows", None)
        )
        # endif // QT_CONFIG(whatsthis)
        self.label.setText(QCoreApplication.translate("MainWindow", "Bandits:", None))
        # if QT_CONFIG(accessibility)
        self.tabWidget.setAccessibleName("")
        # endif // QT_CONFIG(accessibility)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabTree),
            QCoreApplication.translate("MainWindow", "&Tree", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabSkills),
            QCoreApplication.translate("MainWindow", "&Skills", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabItems),
            QCoreApplication.translate("MainWindow", "&Items", None),
        )
        self.menuWidget.setTitle(
            QCoreApplication.translate("MainWindow", "&Builds", None)
        )
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", "&View", None))
        pass

    # retranslateUi
