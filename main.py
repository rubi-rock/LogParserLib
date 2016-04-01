import logging
from datetime import datetime
import log_parser_engine
from constants import ParamNames, LOG_LEVEL_LIST
from other_helpers import LogUtility    # keep it even if it seems unused, it set up the logging automatically

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QTextEdit, QWidget, QDialog, QApplication


if __name__ == '__main__':
    logging.info("Start")

    # Instanciate the parser with general settings
    #params = {ParamNames.exclusions: exclusions, ParamNames.categories: categories, ParamNames.performance_trigger_in_ms: 3500, ParamNames.provide_context: 10}
    #flp = log_parser_engine.FolderLogParser(**params)
    flp = log_parser_engine.FolderLogParser()

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

    # parse one file for specific log levels in a specific date range. If the ParamNames.performance_trigger_in_ms general
    # setting is not None or 0, then no need to select the STATISTIC level because it will be processed to identify
    # any performance issue anyway
    flp.parse("/Users/ChristianRocher/Downloads/ACTUEL_TS_LOGS", log_levels, datetime(year=2016, month=3, day=1), datetime(year=2016, month=3, day=31))
    #flp.parse("/Users/ChristianRocher/Downloads/ACTUEL_TS_LOGS/log - copie/bdobson", log_levels, datetime(year=2016, month=1, day=1), datetime(year=2016, month=3, day=31))
    #flp.parse("/Users/ChristianRocher/Downloads/log", log_levels, datetime(year=2016, month=3, day=10), datetime(year=2016, month=3, day=10))
    #flp.parse("/Users/ChristianRocher/Downloads/log/AJHeafey", log_levels, datetime(year=2016, month=3, day=10), datetime(year=2016, month=3, day=10))
    #flp.parse("/Users/ChristianRocher/Downloads/log/afisher", log_levels, datetime(year=2016, month=1, day=10), datetime(year=2016, month=3, day=10))
    #flp.parse("/Users/ChristianRocher/Downloads/log/LBlundell", log_levels, datetime(year=2016, month=3, day=1), datetime(year=2016, month=3, day=31))

    #flp.parse(r"C:\Users\crocher\Downloads\ACTUEL_TS_LOGS\Mar-29-2016", log_levels, datetime(year=2016, month=3, day=24), datetime(year=2016, month=3, day=31))
    #flp.parse(r"C:\Users\crocher\Downloads\ACTUEL_TS_LOGS\Mar-29-2016\log - 2012_ts5-Mar29\log - Copy", log_levels, datetime(year=2016, month=3, day=24), datetime(year=2016, month=3, day=31))

    #flp.save_to_csv_file()



