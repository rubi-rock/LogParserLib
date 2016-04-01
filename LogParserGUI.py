import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QFileDialog
import LogParserMainWindow
import icons_rc
from constants import LOG_LEVEL_LIST, DEFAULT_EXCLUSIONS, DEFAULT_CATEGORIES


class LogParserMainWindows(object):
    def __init__(self, selected_log_levels = None):
        self.__app = QtWidgets.QApplication(sys.argv)
        self.__mainwindow = QtWidgets.QMainWindow()
        self.__ui = LogParserMainWindow.Ui_MainWindow()
        self.__ui.setupUi(self.__mainwindow)
        self.__init_events()
        self.__init_UI(selected_log_levels)

    def __init_UI(self, selected_log_levels):
        self.__init_loglevels(selected_log_levels)
        self.__init_exclusions()
        self.__init_categories()

    # Load exclusions on screen
    def __init_exclusions(self):
        self.__ui.edt_Exclusions.clear()
        for exclusion in DEFAULT_EXCLUSIONS.values():
            self.__ui.edt_Exclusions.appendPlainText(exclusion)

    # Load categories on screen
    def __init_categories(self):
        self.__ui.edt_Categories.clear()
        for cat_name, cat_expr in DEFAULT_CATEGORIES.items():
            self.__ui.edt_Categories.appendPlainText(cat_name.split('.', 1)[1] + '=' + cat_expr)

    # Connect all events
    def __init_events(self):
        self.__ui.actionQuit.triggered.connect(self.__handleQuitButton)
        self.__ui.actionSelect_Folder.triggered.connect(self.__select_Dir)
        self.__ui.btn_SelectDir.clicked.connect(self.__select_Dir)

    # Initialize the log level checkbox list
    def __init_loglevels(self, selected_log_levels):
        if selected_log_levels is None:
            selected_log_levels = {}

        self.__ui.listWidget_LogLevels.clear()

        for level in LOG_LEVEL_LIST:
            item = QtWidgets.QListWidgetItem(level, self.__ui.listWidget_LogLevels)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked if level in selected_log_levels.values() else QtCore.Qt.Unchecked)

    # Quit action event handler
    def __handleQuitButton(self):
        self.__mainwindow.close()

    # Folder selection action event handler
    def __select_Dir(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec_():
            self.__ui.edt_Path.setText(dialog.selectedFiles()[0])

    def ShowMainWindow(self):
        self.__mainwindow.showMaximized()
        sys.exit(self.__app.exec_())

