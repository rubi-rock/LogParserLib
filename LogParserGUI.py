import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import  QFileDialog
from PyQt5.QtCore import QCoreApplication

from collections import OrderedDict
import os.path

import LogParserMainWindow
from constants import LOG_LEVEL_LIST, DEFAULT_LOG_LEVELS, DEFAULT_EXCLUSIONS, DEFAULT_CATEGORIES, DEFAULT_CONTEXT_LENGTH, \
    DEFAULT_PERFORMANCE_TRIGGER_IN_MS, ParamNames, StatusBarValues
import log_parser_engine

# Keep it - required for the icons on the buttons of the main form
import icons_rc
from xml_excel_helper import GetOutputXlsxFileName

SPLITTER_MIN_SIZE = 30

class LogParserMainWindows(object):
    def __init__(self, path=None, fromdate=None, todate=None, output=None, autoopen=True):
        self.__app = QtWidgets.QApplication(sys.argv)
        self.__mainwindow = QtWidgets.QMainWindow()
        self.__ui = LogParserMainWindow.Ui_MainWindow()
        self.__ui.setupUi(self.__mainwindow)
        self.__ui.chk_AutoOpen.setChecked(autoopen)
        self.__init_UI()
        self.__init_events()
        self.__mainwindow.setContentsMargins( 0, 0 ,0 ,0)
        self.__stopped = False
        self.__console_scrollbar = self.__ui.edt_console.verticalScrollBar()
        self.__init_statusbar()

        if path is not None:
            self.__ui.edt_Path.setText(path)
        if fromdate is not None:
            self.__ui.date_From.setDate( QtCore.QDate.fromString(str(fromdate), 'yyyy-MM-dd'))
        if todate is not None:
            self.__ui.date_To.setDate(QtCore.QDate.fromString(str(todate), 'yyyy-MM-dd'))
        self.__ui.edt_output.setText(GetOutputXlsxFileName(output))

    # Init the form with required data (or config)
    def __init_UI(self):
        self.__ui.actionParse.setEnabled(False)
        self.__ui.actionStop.setEnabled(False)
        self.__init_loglevels(DEFAULT_LOG_LEVELS)
        self.__init_exclusions()
        self.__init_categories()
        self.__ui.spin_contextLOL.setValue(DEFAULT_CONTEXT_LENGTH)
        self.__ui.spin_perfTrigger.setValue(DEFAULT_PERFORMANCE_TRIGGER_IN_MS / 1000)
        self.__init_statusbar()

    # Fill the statusbar with appropriate controls - not possible to do from Qt Creatur (!!!???)
    def __init_statusbar(self):
        self.__ui.statusBar.addWidget(self.__ui.frame_files, 0)
        self.__ui.statusBar.addWidget(self.__ui.frame_lines, 0)
        self.__ui.statusBar.addWidget(self.__ui.frame_elapsed_time, 0)
        self.__ui.statusBar.addWidget(self.__ui.frame_log_entries, 0)
        self.__ui.statusBar.addWidget(self.__ui.frame_progress_bar, 0)
        self.__update_statusbar()

    def __update_statusbar(self, **kwargs):
        if StatusBarValues.total_files in kwargs.keys():
            self.__ui.lbl_total_files.setText(str(kwargs[StatusBarValues.total_files]))
            self.__ui.progressBar.setMaximum(kwargs[StatusBarValues.total_files])
        if StatusBarValues.files_processed in kwargs.keys():
            self.__ui.progressBar.setValue(kwargs[StatusBarValues.files_processed])
            self.__ui.lbl_processed_files.setText(str(kwargs[StatusBarValues.files_processed]))

        if StatusBarValues.lines_processed in kwargs.keys():
            self.__ui.lbl_processed_lines.setText(str(kwargs[StatusBarValues.lines_processed]))
        if StatusBarValues.total_lines in kwargs.keys():
            self.__ui.lbl_total_lines.setText(str(kwargs[StatusBarValues.total_lines]))

        if StatusBarValues.lines_to_analyze in kwargs.keys():
            self.__ui.lbl_log_entries_count.setText(str(kwargs[StatusBarValues.lines_to_analyze]))

        if StatusBarValues.elapsed_time in kwargs.keys():
            self.__ui.lbl_elapsed_time.setText(kwargs[StatusBarValues.elapsed_time])

    #
    # Initialization of the UI
    #

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

    # Initialize the log level checkbox list
    def __init_loglevels(self, selected_log_levels):
        if selected_log_levels is None:
            selected_log_levels = {}

        self.__ui.listWidget_LogLevels.clear()

        for level in LOG_LEVEL_LIST:
            item = QtWidgets.QListWidgetItem(level, self.__ui.listWidget_LogLevels)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked if level in selected_log_levels.values() else QtCore.Qt.Unchecked)

    #
    # Initialization of the UI event handlers
    #

    # Connect all events
    def __init_events(self):
        self.__ui.actionQuit.triggered.connect(self.__handleQuitButton)
        self.__ui.actionSelect_Folder.triggered.connect(self.__select_Dir)
        self.__ui.btn_SelectDir.clicked.connect(self.__select_Dir)
        self.__ui.edt_Path.textChanged.connect(self.__edt_path_changed)
        self.__ui.actionParse.triggered.connect(self.__parse)
        self.__ui.actionStop.triggered.connect(self.__stop)


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

    # Path field changed event handler
    def __edt_path_changed(self, text):
        self.__ui.actionParse.setEnabled(os.path.exists(text))

    # Callback to display progresses
    def __progress_callback(self, **kwargs):
        if StatusBarValues.text in kwargs.keys():
            self.__ui.edt_console.appendPlainText(kwargs[StatusBarValues.text])
        self.__console_scrollbar.setValue(self.__console_scrollbar.maximum())   #autoscroll
        self.__update_statusbar(**kwargs)
        QCoreApplication.processEvents()
        return self.__stopped

    # Callback to let know to the parser that the parsing is cancelled
    def __cancel_callback(self):
        QCoreApplication.processEvents()
        return self.__stopped

    # STOP THE PARSING IN PROGRESS
    def __stop(self):
        self.__stopped = True

    #
    # Getter to retrieve values from the UI
    #

    # Returns exclusion from the UI (user's choice instead of the defaults)
    def __get_exclusions_from_UI(self):
        lines = self.__ui.edt_Exclusions.toPlainText().split('\n')
        exclusions = OrderedDict( [ ( lines.index(excl), excl ) for excl in lines] )
        return exclusions

    # Returns exclusion from the UI (user's choice instead of the defaults)
    def __get_categories_from_UI(self):
        categories = OrderedDict()
        lines = self.__ui.edt_Categories.toPlainText().split('\n')
        for line in lines:
            line = line.split('=', 1)
            cat_name = '{0}.{1}'.format(len(categories) + 1, line[0])
            cat_expr = line[1]
            categories[cat_name] = cat_expr
        return categories

    # Returns parameters from the UI (user's choice instead of the defaults)
    def __get_params_from_UI(self):
        params = {}
        params[ParamNames.exclusions] = self.__get_exclusions_from_UI()
        params[ParamNames.categories] = self.__get_categories_from_UI()
        params[ParamNames.performance_trigger_in_ms] = self.__ui.spin_perfTrigger.value() * 1000
        params[ParamNames.provide_context] = self.__ui.spin_contextLOL.value()
        return params

    # Manage actions states
    def __update_action_states(self, isparsing):
        self.__ui.actionStop.setEnabled(isparsing)
        self.__ui.actionParse.setEnabled((not isparsing) and os.path.exists(self.__ui.edt_Path.text()))
        self.__ui.actionQuit.setEnabled(not isparsing)
        self.__ui.actionClean_logs.setEnabled(not isparsing)
        self.__ui.actionSelect_Folder.setEnabled(not isparsing)
        self.__ui.actionLoad_config_from_file.setEnabled(not isparsing)
        self.__ui.actionSave_config_to_file.setEnabled(not isparsing)

    #
    # Parse the log file action event handler
    #
    def __parse(self):
        self.__stopped = False
        self.__update_action_states(True)
        try:
            params = self.__get_params_from_UI()
            # params = {ParamNames.exclusions: exclusions, ParamNames.categories: categories, ParamNames.performance_trigger_in_ms: 3500, ParamNames.provide_context: 10}
            flp = log_parser_engine.FolderLogParser(**params)
            flp.set_progress_callback(self.__progress_callback)
            flp.set_cancel_callback(self.__cancel_callback)
            flp.parse(self.__ui.edt_Path.text(), DEFAULT_LOG_LEVELS, self.__ui.date_From.dateTime().toPyDateTime(), self.__ui.date_To.dateTime().toPyDateTime(), self.__ui.edt_output.text())
        finally:
            self.__update_action_states(False)

    #
    # Show the main window (maximized)
    #
    def ShowMainWindow(self):
        self.__mainwindow.showMaximized()
        sys.exit(self.__app.exec_())

