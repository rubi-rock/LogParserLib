import logging
from datetime import datetime
import log_parser_engine
from constants import ParamNames, LOG_LEVEL_LIST
from other_helpers import LogUtility    # keep it even if it seems unused, it set up the logging automatically

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QTextEdit, QWidget, QDialog, QApplication
import LogParserGUI



if __name__ == '__main__':
    logging.info("Start")

    log_levels = {
        '1': LOG_LEVEL_LIST.OPERATING_SYSTEM,
        '2': LOG_LEVEL_LIST.FATAL,
        '3': LOG_LEVEL_LIST.EXCEPTION_TRACK,
        '4': LOG_LEVEL_LIST.LEAK,
        # '5': LogLevels.STATISTIC,
        '10': LOG_LEVEL_LIST.SYST_HIGH,
        '11': LOG_LEVEL_LIST.SYST_MEDIUM,
        '12': LOG_LEVEL_LIST.SYST_LOW
    }

    mainwindow = LogParserGUI.LogParserMainWindows(log_levels)
    mainwindow.ShowMainWindow()





