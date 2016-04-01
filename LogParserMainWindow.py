# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/log_oxigen_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Canada))
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.tabWidget_General = QtWidgets.QTabWidget(self.centralWidget)
        self.tabWidget_General.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget_General.setObjectName("tabWidget_General")
        self.tab_Parameters = QtWidgets.QWidget()
        self.tab_Parameters.setObjectName("tab_Parameters")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_Parameters)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.tab_Parameters)
        self.label_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.tab_Parameters)
        self.label_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 3, 1, 1)
        self.date_From = QtWidgets.QDateEdit(self.tab_Parameters)
        self.date_From.setCalendarPopup(True)
        self.date_From.setObjectName("date_From")
        self.gridLayout_2.addWidget(self.date_From, 0, 2, 1, 1)
        self.date_To = QtWidgets.QDateEdit(self.tab_Parameters)
        self.date_To.setCalendarPopup(True)
        self.date_To.setDate(QtCore.QDate(2100, 1, 1))
        self.date_To.setObjectName("date_To")
        self.gridLayout_2.addWidget(self.date_To, 0, 4, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.tab_Parameters)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 0, 7, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.tab_Parameters)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 8, 1, 1)
        self.spin_contextLOL = QtWidgets.QSpinBox(self.tab_Parameters)
        self.spin_contextLOL.setMaximum(100)
        self.spin_contextLOL.setSingleStep(5)
        self.spin_contextLOL.setProperty("value", 10)
        self.spin_contextLOL.setObjectName("spin_contextLOL")
        self.gridLayout_2.addWidget(self.spin_contextLOL, 0, 9, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tab_Parameters)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 5, 1, 1)
        self.spin_perfTrigger = QtWidgets.QDoubleSpinBox(self.tab_Parameters)
        self.spin_perfTrigger.setDecimals(1)
        self.spin_perfTrigger.setMinimum(0.5)
        self.spin_perfTrigger.setMaximum(999.0)
        self.spin_perfTrigger.setSingleStep(0.5)
        self.spin_perfTrigger.setProperty("value", 3.5)
        self.spin_perfTrigger.setObjectName("spin_perfTrigger")
        self.gridLayout_2.addWidget(self.spin_perfTrigger, 0, 6, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.tab_Parameters)
        self.label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.btn_SelectDir = QtWidgets.QToolButton(self.tab_Parameters)
        self.btn_SelectDir.setObjectName("btn_SelectDir")
        self.gridLayout.addWidget(self.btn_SelectDir, 0, 2, 1, 1)
        self.edt_Path = QtWidgets.QLineEdit(self.tab_Parameters)
        self.edt_Path.setObjectName("edt_Path")
        self.gridLayout.addWidget(self.edt_Path, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.tab_Parameters)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 4, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.push_Collapse = QtWidgets.QPushButton(self.tab_Parameters)
        self.push_Collapse.setObjectName("push_Collapse")
        self.horizontalLayout_4.addWidget(self.push_Collapse)
        self.push_Expand = QtWidgets.QPushButton(self.tab_Parameters)
        self.push_Expand.setObjectName("push_Expand")
        self.horizontalLayout_4.addWidget(self.push_Expand)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.label_Filter = QtWidgets.QLabel(self.tab_Parameters)
        self.label_Filter.setObjectName("label_Filter")
        self.horizontalLayout_4.addWidget(self.label_Filter)
        self.edt_Filter = QtWidgets.QLineEdit(self.tab_Parameters)
        self.edt_Filter.setMinimumSize(QtCore.QSize(255, 0))
        self.edt_Filter.setMaximumSize(QtCore.QSize(500, 16777215))
        self.edt_Filter.setObjectName("edt_Filter")
        self.horizontalLayout_4.addWidget(self.edt_Filter)
        self.toolButton = QtWidgets.QToolButton(self.tab_Parameters)
        self.toolButton.setMaximumSize(QtCore.QSize(28, 28))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/delete_24.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setIconSize(QtCore.QSize(24, 24))
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout_4.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.treeWidget_Results = QtWidgets.QTreeWidget(self.tab_Parameters)
        self.treeWidget_Results.setObjectName("treeWidget_Results")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget_Results)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/folder_search_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item_0.setIcon(0, icon2)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/delete_24.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item_1.setIcon(0, icon3)
        self.verticalLayout.addWidget(self.treeWidget_Results)
        self.tabWidget_General.addTab(self.tab_Parameters, "")
        self.tab_Config = QtWidgets.QWidget()
        self.tab_Config.setObjectName("tab_Config")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_Config)
        self.verticalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_AppLogLevels = QtWidgets.QLabel(self.tab_Config)
        self.label_AppLogLevels.setObjectName("label_AppLogLevels")
        self.verticalLayout_2.addWidget(self.label_AppLogLevels)
        self.listWidget_LogLevels = QtWidgets.QListWidget(self.tab_Config)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_LogLevels.sizePolicy().hasHeightForWidth())
        self.listWidget_LogLevels.setSizePolicy(sizePolicy)
        self.listWidget_LogLevels.setMinimumSize(QtCore.QSize(0, 80))
        self.listWidget_LogLevels.setMaximumSize(QtCore.QSize(16777215, 80))
        self.listWidget_LogLevels.setLineWidth(1)
        self.listWidget_LogLevels.setProperty("showDropIndicator", False)
        self.listWidget_LogLevels.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.listWidget_LogLevels.setAlternatingRowColors(False)
        self.listWidget_LogLevels.setFlow(QtWidgets.QListView.TopToBottom)
        self.listWidget_LogLevels.setProperty("isWrapping", True)
        self.listWidget_LogLevels.setResizeMode(QtWidgets.QListView.Fixed)
        self.listWidget_LogLevels.setLayoutMode(QtWidgets.QListView.Batched)
        self.listWidget_LogLevels.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget_LogLevels.setModelColumn(0)
        self.listWidget_LogLevels.setSelectionRectVisible(True)
        self.listWidget_LogLevels.setObjectName("listWidget_LogLevels")
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_LogLevels.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_LogLevels.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_LogLevels.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_LogLevels.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.listWidget_LogLevels.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.listWidget_LogLevels.addItem(item)
        self.verticalLayout_2.addWidget(self.listWidget_LogLevels)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_Exclusions = QtWidgets.QLabel(self.tab_Config)
        self.label_Exclusions.setObjectName("label_Exclusions")
        self.verticalLayout_4.addWidget(self.label_Exclusions)
        self.edt_Exclusions = QtWidgets.QPlainTextEdit(self.tab_Config)
        self.edt_Exclusions.setObjectName("edt_Exclusions")
        self.verticalLayout_4.addWidget(self.edt_Exclusions)
        self.verticalLayout_6.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_Categories = QtWidgets.QLabel(self.tab_Config)
        self.label_Categories.setObjectName("label_Categories")
        self.verticalLayout_3.addWidget(self.label_Categories)
        self.edt_Categories = QtWidgets.QPlainTextEdit(self.tab_Config)
        self.edt_Categories.setObjectName("edt_Categories")
        self.verticalLayout_3.addWidget(self.edt_Categories)
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
        self.tabWidget_General.addTab(self.tab_Config, "")
        self.verticalLayout_5.addWidget(self.tabWidget_General)
        self.frame_console_titlebar = QtWidgets.QFrame(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.frame_console_titlebar.setFont(font)
        self.frame_console_titlebar.setStyleSheet("background-color:qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255))")
        self.frame_console_titlebar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_console_titlebar.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_console_titlebar.setObjectName("frame_console_titlebar")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_console_titlebar)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_8 = QtWidgets.QLabel(self.frame_console_titlebar)
        self.label_8.setStyleSheet("color:rgb(255, 255, 255)")
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        spacerItem1 = QtWidgets.QSpacerItem(915, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btn_toggleConsole = QtWidgets.QToolButton(self.frame_console_titlebar)
        self.btn_toggleConsole.setStyleSheet("background-color:rgb(255, 255, 255)")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/arrow-down-16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_toggleConsole.setIcon(icon4)
        self.btn_toggleConsole.setArrowType(QtCore.Qt.NoArrow)
        self.btn_toggleConsole.setObjectName("btn_toggleConsole")
        self.horizontalLayout_3.addWidget(self.btn_toggleConsole)
        self.verticalLayout_5.addWidget(self.frame_console_titlebar)
        self.frame_console = QtWidgets.QFrame(self.centralWidget)
        self.frame_console.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_console.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_console.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_console.setObjectName("frame_console")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_console)
        self.verticalLayout_7.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.edt_console = QtWidgets.QPlainTextEdit(self.frame_console)
        self.edt_console.setEnabled(False)
        self.edt_console.setTabStopWidth(80)
        self.edt_console.setObjectName("edt_console")
        self.verticalLayout_7.addWidget(self.edt_console)
        self.verticalLayout_5.addWidget(self.frame_console)
        self.tabWidget_General.raise_()
        self.frame_console.raise_()
        self.frame_console_titlebar.raise_()
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1024, 22))
        self.menuBar.setDefaultUp(False)
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuOptions = QtWidgets.QMenu(self.menuBar)
        self.menuOptions.setObjectName("menuOptions")
        self.menuRun = QtWidgets.QMenu(self.menuBar)
        self.menuRun.setObjectName("menuRun")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setIconSize(QtCore.QSize(32, 32))
        self.mainToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/shutdown_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon5)
        self.actionQuit.setObjectName("actionQuit")
        self.actionSave_config_to_file = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/Arrow-down-icon_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_config_to_file.setIcon(icon6)
        self.actionSave_config_to_file.setObjectName("actionSave_config_to_file")
        self.actionLoad_config_from_file = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/Arrow-up-icon_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoad_config_from_file.setIcon(icon7)
        self.actionLoad_config_from_file.setObjectName("actionLoad_config_from_file")
        self.actionParse = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/Categories-preferences-system-icon_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionParse.setIcon(icon8)
        self.actionParse.setIconVisibleInMenu(True)
        self.actionParse.setPriority(QtWidgets.QAction.NormalPriority)
        self.actionParse.setObjectName("actionParse")
        self.actionClean_logs = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/bin-red-full-icon_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClean_logs.setIcon(icon9)
        self.actionClean_logs.setObjectName("actionClean_logs")
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setObjectName("action_2")
        self.actionSelect_Folder = QtWidgets.QAction(MainWindow)
        self.actionSelect_Folder.setIcon(icon2)
        self.actionSelect_Folder.setObjectName("actionSelect_Folder")
        self.actionRecursive = QtWidgets.QAction(MainWindow)
        self.actionRecursive.setCheckable(True)
        self.actionRecursive.setObjectName("actionRecursive")
        self.actionSave_Results_to_CSV = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/Arrow-double-down-icon_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_Results_to_CSV.setIcon(icon10)
        self.actionSave_Results_to_CSV.setObjectName("actionSave_Results_to_CSV")
        self.actionLoad_Results_from_CSV = QtWidgets.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icons/Arrow-double-up-icon_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoad_Results_from_CSV.setIcon(icon11)
        self.actionLoad_Results_from_CSV.setObjectName("actionLoad_Results_from_CSV")
        self.menuFile.addAction(self.actionQuit)
        self.menuOptions.addAction(self.actionSave_config_to_file)
        self.menuOptions.addAction(self.actionLoad_config_from_file)
        self.menuRun.addAction(self.actionParse)
        self.menuRun.addAction(self.actionClean_logs)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionSelect_Folder)
        self.menuRun.addAction(self.actionRecursive)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionSave_Results_to_CSV)
        self.menuRun.addAction(self.actionLoad_Results_from_CSV)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())
        self.menuBar.addAction(self.menuOptions.menuAction())
        self.mainToolBar.addAction(self.actionQuit)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionSelect_Folder)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionParse)
        self.mainToolBar.addAction(self.actionClean_logs)
        self.mainToolBar.addAction(self.actionSave_Results_to_CSV)
        self.mainToolBar.addAction(self.actionLoad_Results_from_CSV)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionSave_config_to_file)
        self.mainToolBar.addAction(self.actionLoad_config_from_file)

        self.retranslateUi(MainWindow)
        self.tabWidget_General.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Log Parser V5"))
        self.label_2.setText(_translate("MainWindow", "From:"))
        self.label_3.setText(_translate("MainWindow", "To:"))
        self.date_From.setDisplayFormat(_translate("MainWindow", "yyyy/MM/dd"))
        self.date_To.setDisplayFormat(_translate("MainWindow", "yyyy/MM/dd"))
        self.label_7.setText(_translate("MainWindow", "sec"))
        self.label_4.setText(_translate("MainWindow", "Context:"))
        self.label_6.setText(_translate("MainWindow", "Performance Trigger:"))
        self.label.setText(_translate("MainWindow", "Path:"))
        self.btn_SelectDir.setText(_translate("MainWindow", "..."))
        self.label_5.setText(_translate("MainWindow", "previous lines"))
        self.push_Collapse.setText(_translate("MainWindow", "Collapse"))
        self.push_Expand.setText(_translate("MainWindow", "Expand"))
        self.label_Filter.setText(_translate("MainWindow", "Filter on:"))
        self.toolButton.setText(_translate("MainWindow", "..."))
        self.treeWidget_Results.headerItem().setText(0, _translate("MainWindow", "File"))
        self.treeWidget_Results.headerItem().setText(1, _translate("MainWindow", "Icon"))
        self.treeWidget_Results.headerItem().setText(2, _translate("MainWindow", "Date/Time"))
        self.treeWidget_Results.headerItem().setText(3, _translate("MainWindow", "Category"))
        self.treeWidget_Results.headerItem().setText(4, _translate("MainWindow", "Log Level"))
        self.treeWidget_Results.headerItem().setText(5, _translate("MainWindow", "Label"))
        __sortingEnabled = self.treeWidget_Results.isSortingEnabled()
        self.treeWidget_Results.setSortingEnabled(False)
        self.treeWidget_Results.topLevelItem(0).setText(0, _translate("MainWindow", "DCI.log"))
        self.treeWidget_Results.topLevelItem(0).setText(2, _translate("MainWindow", "2016/03/01"))
        self.treeWidget_Results.topLevelItem(0).child(0).setText(0, _translate("MainWindow", "#1"))
        self.treeWidget_Results.topLevelItem(0).child(0).setText(2, _translate("MainWindow", "18:34"))
        self.treeWidget_Results.topLevelItem(0).child(0).setText(3, _translate("MainWindow", "KILLED"))
        self.treeWidget_Results.topLevelItem(0).child(0).setText(4, _translate("MainWindow", "CRASHED"))
        self.treeWidget_Results.topLevelItem(0).child(0).setText(5, _translate("MainWindow", "RDP Session Terminated by windows"))
        self.treeWidget_Results.setSortingEnabled(__sortingEnabled)
        self.tabWidget_General.setTabText(self.tabWidget_General.indexOf(self.tab_Parameters), _translate("MainWindow", "Parsing"))
        self.label_AppLogLevels.setText(_translate("MainWindow", "Log Levels:"))
        self.listWidget_LogLevels.setSortingEnabled(False)
        __sortingEnabled = self.listWidget_LogLevels.isSortingEnabled()
        self.listWidget_LogLevels.setSortingEnabled(False)
        item = self.listWidget_LogLevels.item(0)
        item.setText(_translate("MainWindow", "LOG"))
        item = self.listWidget_LogLevels.item(1)
        item.setText(_translate("MainWindow", "FATAL"))
        item = self.listWidget_LogLevels.item(2)
        item.setText(_translate("MainWindow", "EXCEPTION_TRACK"))
        item = self.listWidget_LogLevels.item(3)
        item.setText(_translate("MainWindow", "LEAK"))
        item = self.listWidget_LogLevels.item(4)
        item.setText(_translate("MainWindow", "WARNING"))
        item = self.listWidget_LogLevels.item(5)
        item.setText(_translate("MainWindow", "STATISTICS"))
        self.listWidget_LogLevels.setSortingEnabled(__sortingEnabled)
        self.label_Exclusions.setText(_translate("MainWindow", "Exclusions:"))
        self.label_Categories.setText(_translate("MainWindow", "Categories:"))
        self.tabWidget_General.setTabText(self.tabWidget_General.indexOf(self.tab_Config), _translate("MainWindow", "Configuration"))
        self.label_8.setText(_translate("MainWindow", "Console"))
        self.btn_toggleConsole.setText(_translate("MainWindow", "..."))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOptions.setTitle(_translate("MainWindow", "Options"))
        self.menuRun.setTitle(_translate("MainWindow", "Run"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Alt+Q"))
        self.actionSave_config_to_file.setText(_translate("MainWindow", "Save options to file..."))
        self.actionLoad_config_from_file.setText(_translate("MainWindow", "Load options from file..."))
        self.actionParse.setText(_translate("MainWindow", "Parse"))
        self.actionParse.setIconText(_translate("MainWindow", "Parse"))
        self.actionParse.setShortcut(_translate("MainWindow", "Alt+R"))
        self.actionClean_logs.setText(_translate("MainWindow", "Clean logs"))
        self.actionClean_logs.setToolTip(_translate("MainWindow", "Clean log files"))
        self.action_2.setText(_translate("MainWindow", "-"))
        self.actionSelect_Folder.setText(_translate("MainWindow", "Select Folder..."))
        self.actionRecursive.setText(_translate("MainWindow", "Recursive"))
        self.actionSave_Results_to_CSV.setText(_translate("MainWindow", "Save Results to CSV..."))
        self.actionLoad_Results_from_CSV.setText(_translate("MainWindow", "Load Results from CSV..."))

import icons_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

