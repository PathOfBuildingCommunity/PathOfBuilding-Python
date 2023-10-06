# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlgBrowseFile.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QListView, QListWidgetItem,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from widgets.listbox import ListBox
# import PoB_rc

class Ui_BrowseFile(object):
    def setupUi(self, BrowseFile):
        if not BrowseFile.objectName():
            BrowseFile.setObjectName(u"BrowseFile")
        BrowseFile.resize(900, 600)
        icon = QIcon()
        icon.addFile(u":/Art/Icons/edit-list-order.png", QSize(), QIcon.Normal, QIcon.Off)
        BrowseFile.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(BrowseFile)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.hLayout_CurrDir = QHBoxLayout()
        self.hLayout_CurrDir.setObjectName(u"hLayout_CurrDir")
        self.label_CurrDir = QLabel(BrowseFile)
        self.label_CurrDir.setObjectName(u"label_CurrDir")

        self.hLayout_CurrDir.addWidget(self.label_CurrDir)

        self.lineEdit_CurrDir = QLineEdit(BrowseFile)
        self.lineEdit_CurrDir.setObjectName(u"lineEdit_CurrDir")
        self.lineEdit_CurrDir.setMinimumSize(QSize(520, 24))

        self.hLayout_CurrDir.addWidget(self.lineEdit_CurrDir)

        self.btn_CurrDir = QPushButton(BrowseFile)
        self.btn_CurrDir.setObjectName(u"btn_CurrDir")
        self.btn_CurrDir.setMinimumSize(QSize(0, 0))
        self.btn_CurrDir.setMaximumSize(QSize(24, 16777215))

        self.hLayout_CurrDir.addWidget(self.btn_CurrDir)


        self.verticalLayout.addLayout(self.hLayout_CurrDir)

        self.list_Files = ListBox(BrowseFile)
        self.list_Files.setObjectName(u"list_Files")
        font = QFont()
        font.setFamilies([u"Noto Sans"])
        font.setPointSize(10)
        self.list_Files.setFont(font)
        self.list_Files.setStyleSheet(u"")
        self.list_Files.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_Files.setAutoScroll(True)
        self.list_Files.setProperty("showDropIndicator", False)
        self.list_Files.setDragEnabled(False)
        self.list_Files.setDragDropMode(QAbstractItemView.DragOnly)
        self.list_Files.setDefaultDropAction(Qt.IgnoreAction)
        self.list_Files.setAlternatingRowColors(True)
        self.list_Files.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_Files.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list_Files.setMovement(QListView.Free)
        self.list_Files.setUniformItemSizes(True)

        self.verticalLayout.addWidget(self.list_Files)

        self.hLayout_SaveAs = QHBoxLayout()
        self.hLayout_SaveAs.setObjectName(u"hLayout_SaveAs")
        self.label_SaveAs = QLabel(BrowseFile)
        self.label_SaveAs.setObjectName(u"label_SaveAs")

        self.hLayout_SaveAs.addWidget(self.label_SaveAs)

        self.lineEdit_SaveAs = QLineEdit(BrowseFile)
        self.lineEdit_SaveAs.setObjectName(u"lineEdit_SaveAs")
        self.lineEdit_SaveAs.setMinimumSize(QSize(520, 24))

        self.hLayout_SaveAs.addWidget(self.lineEdit_SaveAs)

        self.rBtn_v2 = QRadioButton(BrowseFile)
        self.rBtn_v2.setObjectName(u"rBtn_v2")
        self.rBtn_v2.setMinimumSize(QSize(40, 24))
        self.rBtn_v2.setChecked(True)

        self.hLayout_SaveAs.addWidget(self.rBtn_v2)

        self.rBtn_v1 = QRadioButton(BrowseFile)
        self.rBtn_v1.setObjectName(u"rBtn_v1")
        self.rBtn_v1.setMinimumSize(QSize(40, 24))

        self.hLayout_SaveAs.addWidget(self.rBtn_v1)


        self.verticalLayout.addLayout(self.hLayout_SaveAs)

        self.hLayout_Buttons = QHBoxLayout()
        self.hLayout_Buttons.setSpacing(12)
        self.hLayout_Buttons.setObjectName(u"hLayout_Buttons")
        self.hSpacer_Buttons = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hLayout_Buttons.addItem(self.hSpacer_Buttons)

        self.btn_Task = QPushButton(BrowseFile)
        self.btn_Task.setObjectName(u"btn_Task")
        self.btn_Task.setMinimumSize(QSize(75, 0))
        self.btn_Task.setFocusPolicy(Qt.NoFocus)
        self.btn_Task.setAutoDefault(False)

        self.hLayout_Buttons.addWidget(self.btn_Task)

        self.btn_Close = QPushButton(BrowseFile)
        self.btn_Close.setObjectName(u"btn_Close")
        self.btn_Close.setMinimumSize(QSize(75, 0))
        self.btn_Close.setFocusPolicy(Qt.NoFocus)
        self.btn_Close.setAutoDefault(False)

        self.hLayout_Buttons.addWidget(self.btn_Close)


        self.verticalLayout.addLayout(self.hLayout_Buttons)

        QWidget.setTabOrder(self.lineEdit_CurrDir, self.list_Files)
        QWidget.setTabOrder(self.list_Files, self.lineEdit_SaveAs)
        QWidget.setTabOrder(self.lineEdit_SaveAs, self.rBtn_v2)
        QWidget.setTabOrder(self.rBtn_v2, self.rBtn_v1)

        self.retranslateUi(BrowseFile)

        self.list_Files.setCurrentRow(-1)
        self.btn_Task.setDefault(True)


        QMetaObject.connectSlotsByName(BrowseFile)
    # setupUi

    def retranslateUi(self, BrowseFile):
        BrowseFile.setWindowTitle(QCoreApplication.translate("BrowseFile", u"Manage Files", None))
        self.label_CurrDir.setText(QCoreApplication.translate("BrowseFile", u"Current Directory :", None))
        self.btn_CurrDir.setText(QCoreApplication.translate("BrowseFile", u"...", None))
        self.label_SaveAs.setText(QCoreApplication.translate("BrowseFile", u"New File Name : ", None))
        self.rBtn_v2.setText(QCoreApplication.translate("BrowseFile", u"v&2", None))
        self.rBtn_v1.setText(QCoreApplication.translate("BrowseFile", u"v&1", None))
        self.btn_Task.setText(QCoreApplication.translate("BrowseFile", u"task", None))
#if QT_CONFIG(tooltip)
        self.btn_Close.setToolTip(QCoreApplication.translate("BrowseFile", u"Close without selecting anything", None))
#endif // QT_CONFIG(tooltip)
        self.btn_Close.setText(QCoreApplication.translate("BrowseFile", u"&Close", None))
    # retranslateUi

