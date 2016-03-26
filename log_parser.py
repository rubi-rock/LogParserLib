import copy
import logging
import os.path
import re
from datetime import datetime, timedelta

# keep LogUtility, even if it seems unused, it sets up the logging automatically
import other_helpers
from constants import Headers, ParamNames, RowTypes
from os_path_helper import FileSeeker
from regex_helper import RegExpSet, PreparedExpressionList, StringDateHelper
import csv_helper
#from pythonbenchmark import measure

'''
    The log parser walks through a folder and its subfolder to locate .log files from Purkinje then process them to build
    a tree of errors, statistics... that can be analyze easily to figure out what's tha cause of a problem or if the
    application is running smoothly (no errors, no performance problem) that can be detected from the logs.

    Log Folders & Files structure
    -----------------------------
    The structure of the log tree:
        Folder A
            File A1
                Session A1.1
                    log line
                    log line
                    ...
                Session A1.2
                    ...
            File A2
                Session A2.1
                    log line
                    log line
                    ...
                Session A2.2
            ...
        Folder B
            ...

    Log Line Structure:
    -------------------
    A log line is basically a file line from the log with a known structure that reflects in the log line structure of
    the log parser:
        date time, level, [module], message


    All logs are not consistents, since we meet exceptions that the log parser manages already:

        . inconsistent log file formats: the expected format is the ISO standard: yyyy/mm/dd hh:mm:ss.ms but we got
          formats that came who knows from where, e.g. '2013-28-01 8:23:32:396 am' (the total package is wrong)

          Since log files had been improved since 5.13, the log parser looks only to the default formant with 2 exceptions:
            - the separator before the milliseconds is ':' instead of '.' : fixed here
            - unknown format : rejected and the date is replaced by '1900/01/01 00:00:00.000'

        . Unexpected text between the time and the level, e.g.: '2016/03/01 10:24:12.234, (MAP1) [SYST}...'. In that
          case, the unexpected text ('MAP1' in this case) is moved at the beginning of the message. In the specific
          case of the MAPGEN map number it is tagged separately: [map=MAP1] that it can be easily extrated

        . Old log level from 4.31: not anymore supported, they are ignored if ever you want to analyze them: just go back
          to the old log parser application wrote in Delphi

    Log Line Filtering:
    -------------------
    A log file contains lines that are not meanningful in some contexts - never sometimes - therefore the log parser
    can discard them based on several criterias:

        . Log level: it lis possible to specify a list of log levels that we be preserved for analysis, log lines with
          any other level will be discarded.

            WARNING:  more log levels will require to process more log lines in details and it will have impacts on both
            =======   the memory comsumption and CPU usage. Therefore be careful, especialy when the statistic are active
                      in the log since 5.13 because you can meet logs 30-200MB containing statistic lines that represent
                      99% of the log file.
                      For instance it is possible to process 5564470 lines containing statistics in 5.13 in abouts 16secs
                      if you exclude the log level STATISTIC but it takes about 12 minutes if you include it.

        . date range : useful to look at only a period of time accross the log files from a folder.

            WARNING: Shorter the date range is, faster the parsing is...
            =======

        . exclusions: string list specifing patterns that discards a log line when it matches on of those patterns.
          There are 2 kind of exclusions:
            . simple text (e.g. 'Available levels : LOG=0,OPERATING_SYSTEM=1,FATAL=2'): this criteria allows to discard
              any log line containing this text. The search is case insensitive

            . regular expression (e.g.: 'REGEX=Can not find module (.*)\\Bin\\PurkScanContentProvider\.dll'): allows to
              discard specific line when a simple text annot be used. In the example here:
                    'REGEX=Can not find module (.*)\\Bin\\PurkScanContentProvider\.dll'
              it allows to exclude the line 'Can not find module C:\Purkinje\Bin\PurkScanContentProvider.dll'
              but not 'Can not find module C:\Purkinje\Bin\Winlogon.dll'

            WARNING: as much as you can use simple text criteria because they are much more faster and simpler to use
            =======  than regular expressions. For instance a regular expression can be 2 or 50+ times slower than a
                     simple text search depending of the regular expression complexity.

    Grouping:
    ---------
    Because logs are rarely "alone", when an error is encountered (exception), the log parser group the log lines in
    error that are in the same second from the previous error until the current log line is more than 1 second from the
    previous one.

    Categorization:
    ---------------
    Usualy there are repeatitive errors related the the sale area of code, to the piece of feature or framework or ...
    Therefore the log parser allows you to categorize the log lines to be able to find them accross all the log files.
    This mechanism - called consolidation in the log parser - allows for instance to look at all the PSL errors at a
    glance: just filter on the category 'PSL'.

    This is accomplished with the same principle than the criterias : simple text and regular expressions (see
    'Log Line Filtering' above).

        WARNING: the same recommendations applies for the categorization than for the filtering about the memory and CPU
        =======  consumption

'''

# Change the log level of DETAILLED_LOGGING_LEVEL to put more detail on the console (logging.info)
DETAILLED_LOGGING_NONE = 0          # Nothing
DETAILLED_LOGGING_FILE = 1          # Statis about the file only
DETAILLED_LOGGING_SESSION = 2       # details of the file (sessions & lines preserved)
DETAILLED_LOGGING_LEVEL = DETAILLED_LOGGING_SESSION

# Date used when the date and time from the log line cannot be parsed
UNPARSABLE_DATETIME = datetime(year=1900, month=1, day=1, hour=0)


#
# log line expression parser to break the line in its components (date, time, level...)
#
class LogLineSplitter(object):
    __filter_engine = re.compile(
            "(?P<date>[^, ]+[ ,]+[^, ]+)[, ]*(\((?P<map>\**[A-Z0-9]*\**)\)[, ]*)?\[(?P<level>[A-Z_]*)\][ ]*(\[(?P<module>[0-9A-Z_\.\-]*)\][ ]*)?(?P<message>.+)",
            flags=re.IGNORECASE)

    @staticmethod
    def parse_log_line(line):
        return LogLineSplitter.__filter_engine.match(line)


#
# Instance of a log session : between 'BEGIN SESSION' and 'END SESSION'
#
class LogSession(object):
    __id_seq = 0

    # constructor
    def __init__(self, log_dict = None):
        try:
            if log_dict is None:
                self.__module = 'Unknown'
                self.__date = str(UNPARSABLE_DATETIME.date())
                self.__time = str(UNPARSABLE_DATETIME.time())
            else:
                self.__module = log_dict.module
                self.__date = log_dict.date
                self.__time = log_dict.time
            LogSession.__id_seq += 1
            self.__id = LogSession.__id_seq
            self.__lines = []
            self.__module = ""
            self.__has_crashed = False
            self.__info = {}
        except Exception:
            logging.exception('')
            raise

    # serialize as string to help for logging and debugging
    def __str__(self):
        try:
            if len(self.__lines) > 0:
                return "\n\tSession #{0} - Entries:\n\t\t{1}".format( self.__id, "\n\t\t".join(str(entry) for entry in self.__lines))
            else:
                return "\n\tSession #{0} - 0 entries".format( self.__id)

        except Exception:
            logging.exception('')
            raise

    def add_crashed_session_log(self):
        if len(self.lines) > 0:
            idx = len(self.lines) - 1
            crash_log_line = copy.deepcopy(self.lines[idx])
        else:
            crash_log_line = Log_Line({Headers.module: self.__module, Headers.date: self.__date, Headers.time: self.__time})

        crash_log_line.set_value(Headers.message, 'SESSION TERMINATED ABNORMALLY (log "END SESSION" not found)')
        crash_log_line.set_value(Headers.level, 'CRASHED')
        crash_log_line.set_value(Headers.category, 'CRASHED')
        crash_log_line.set_value(Headers.group, 99999) # Special group for the crashed indicator
        self.lines.append(crash_log_line)
        self.__has_crashed = True

    def add_session_info(self, info_dict):
        for key, value in info_dict.items():
            if key in self.__info.keys():
                value = self.__info[key] + ', ' + value
            self.__info[key] = value

    # Session's ID. Uses to deferenciate sessions from a log file. Also useful to sort when the logs are added to a grid
    @property
    def session_id(self):
        return self.__id

    # List of entries (lines) preserved from the log file after filtering (exclusions, date range...)
    @property
    def lines(self):
        return self.__lines

    # Lines count in the session
    @property
    def lines_count(self):
        return len(self.__lines)

    # If a session did not have a 'END SESSION' in the logs then it's a crashed session or killed session
    @property
    def has_crashed(self):
        return self.__has_crashed

    @property
    def as_csv_row(self):
        row = dict()
        row[Headers.type] = RowTypes.session
        row[Headers.date] = self.__date
        row[Headers.time] = self.__time
        row[Headers.session] = self.__id
        row[Headers.has_crashed] = self.has_crashed
        row[Headers.module] = self.__module
        row[Headers.message] = '[{0}]'.format(']['.join("{0}={1}".format(key, value) for key, value in self.__info.items()))
        return row

#
# Parsed log line : date, time, level, module, message... in a structured way. It saves memory because a dict has to
# save names and values which is memory consuming
#
class Log_Line(object):
    def __init__(self, line_dict):
        self.__data = line_dict
        self.__fixe_date()
        self.__data[Headers.type] = RowTypes.line

    def __fixe_date(self):
        value = self.__data[Headers.date]
        if type(value) is not datetime.date:
            try:
                dt = StringDateHelper.str_iso_to_date(value)    # very efficient: x2+ faster than dateutil.parser.parse
            except:
                dt = UNPARSABLE_DATETIME
            self.__data[Headers.date] = dt.date()
            self.__data[Headers.time] = dt.time()

        self.__data[Headers.group] = 0

    @property
    def date(self):
        return self.__data[Headers.date]

    @property
    def time(self):
        return self.__data[Headers.time]

    @property
    def level(self):
        return self.__data[Headers.level]

    @property
    def module(self):
        return self.__data[Headers.module]

    @property
    def message(self):
        return self.__data[Headers.message]

    @property
    def group(self):
        return self.__data[Headers.group]

    @property
    def category(self):
        if Headers.category in self.__data.keys():
            return self.__data[Headers.category]
        else:
            return None

    def set_value(self, key, value):
        self.__data[key] = value

    def __str__(self):
        return "[date={0}][time={1}][category={2}][level={3}][module={4}][group={5}][msg={6}]".format(
            self.date, self.time, self.category, self.level, self.module, self.group, self.message)

    @property
    def as_csv_row(self):
        return self.__data


#
# Parsed log file: result of the parsing
#
class ParsedLogFile(object):
    # Constructor
    def __init__(self, file_to_parse_info):
        try:
            self.__file_info = file_to_parse_info
            self.__sessions = []
            self.__current_session = None
        except Exception:
            logging.exception('')
            raise

    # Returns the parsed log file as a string
    def __str__(self):
        l = len(self.sessions)
        if l > 0:
            return "{0} Sessions: {1}".format(l, "\n\t\t".join(str(lines) for lines in self.sessions))
        else:
            return "{0} Sessions: none".format(l)

    # Information about the parsed file (path, name, date...)
    @property
    def parsed_file_info(self):
        return self.__file_info

    # List of sessions for this log file
    @property
    def sessions(self):
        return self.__sessions

    # Returns the line count - all file's sessions together
    @property
    def lines_count(self):
        return sum(session.lines_count for session in self.__sessions)

    # Add a log entry (line) to the log, the session change detection is done here
    def add_log(self, log_dict):
        try:
            if self.__current_session is None:
                self.open_session()

            self.__current_session.lines.append(log_dict)
        except Exception:
            logging.exception('')
            raise

    # Open a new session and set the current session - used to add new logs
    def open_session(self, log_dict = None):
        self.__current_session = LogSession(log_dict)
        self.__sessions.append(self.__current_session)

    # close the current session - if empty then delete it because we are not interested in sessions not meanningful
    def close_session(self, crashedsession = False):
        # document a crashed session (application crash, process killed)
        if crashedsession:
            self.__current_session.add_crashed_session_log()
        # flush an empty session
        if self.__current_session is not None and len(self.__current_session.lines) == 0:
            self.__sessions.remove(self.__current_session)
            self.__current_session = None

    def add_session_info(self, dict):
        self.__current_session.add_session_info(dict)

    @property
    def as_csv_row(self):
        row = dict()
        row[Headers.type] = RowTypes.file
        row[Headers.file] = self.parsed_file_info.fullname
        row[Headers.date] = self.parsed_file_info.date.date()
        row[Headers.time] = self.parsed_file_info.date.time()
        return row




#
# Parses a log file and produces a ParsedLogFile when not empty
#
class LogFileParser(object):
    # Constructor
    def __init__(self, **params):
        try:
            self.__lines_processed = 0
            self.__re_exclusions = params[ParamNames.exclusions]
            self.__re_categories = params[ParamNames.categories]
            self.__re_session_info = params[ParamNames.session_info]
            self.__filtered_in_levels = params[ParamNames.filtered_in_levels]
            self.__min_date = params[ParamNames.min_date]
            self.__max_date = params[ParamNames.max_date]
            self.__parsed_file = ParsedLogFile(params[ParamNames.file_info])
            self.__session_opened = False
            self.__session_marker = False

            self.parse()
        except Exception:
            logging.exception('')
            raise

    # Parsed log file object resulting of the parsing process
    @property
    def parsed_file(self):
        return self.__parsed_file

    # Amount of lines processed from the log file
    @property
    def lines_processed(self):
        return self.__lines_processed

    # Returns true if the log entry is out of the selected range date
    def __is_line_out_of_date_range(self, **log_dict):
        try:
            date = log_dict[Headers.date] if Headers.date in log_dict.keys() else None
            if date is not None:
                return (date <= self.__min_date) or (date >= self.__max_date)
            else:
                return False
        except Exception:
            logging.exception('')
            raise

    # Returns true if the line must be excluded (lines that are 'polution or useless' from the log file)
    def __is_line_excluded(self, line):
        try:
            return RegExpSet.search_any_expression(line, self.__re_exclusions) is not None
        except Exception:
            logging.exception('')
            raise

    # Extract possible session information
    def __extract_session_info(self, line):
        info_name = RegExpSet.search_any_expression(line, self.__re_session_info)
        if info_name is not None:
            log_dict = self.__split_line(line)
            info = log_dict.message.split(':')[1].strip()
            info = {info_name: info}
            self.parsed_file.add_session_info(info)
            return True
        else:
            return False

    # Split a log line in its components (date, time, level, [module], message)
    def __split_line(self, line):
        try:
            match = LogLineSplitter.parse_log_line(line)
            if match is not None:
                return  Log_Line(match.groupdict())
            else:
                return None
        except Exception:
            logging.exception('')
            raise

    # Set the category of the line when it applies
    def __set_line_category(self, line_dict):
        category = RegExpSet.search_any_expression(line_dict.message, self.__re_categories)
        if category is not None:
            category = category.strip("0123456789.")
            line_dict.set_value(Headers.category, category)

    # Parse one log file based on the exclusions (logs to ignore) and categories (which category the log belongs to).
    def parse(self):
        try:
            file_name = self.parsed_file.parsed_file_info.fullname
            if not os.path.exists(file_name):
                exit()

            logging.info("Processing file: %s", file_name)
            text_file = open(file_name, mode='rt', encoding='latin-1')  # required to use latin-1 because logs contain french
            try:
                for line in iter(text_file):
                    self.__lines_processed += 1

                    if len(line) <= 1:
                        continue

                    if self.process_session(line):
                        continue    # because it was BEGIN SESSION or END SESSION

                    if self.__extract_session_info(line):
                        continue    # because it was about the session info

                    filtered_out = True
                    for key, level in self.__filtered_in_levels.items():
                        if level in line:
                            filtered_out = False
                    if filtered_out:
                        continue

                    if not self.__is_line_excluded(line):
                        log_line_dict = self.__split_line(line)
                        if log_line_dict is not None:
                            if log_line_dict.date < self.__max_date.date():
                                self.__set_line_category(log_line_dict)
                                self.__parsed_file.add_log(log_line_dict)
                        else:
                            logging.error("Unable to parse log line: %s", line)
            finally:
                self.process_session('')    # Close the session if not yet done (crashed session?)
                text_file.close()
        except Exception:
            logging.exception('')
            raise

    def process_session(self, line):
        if 'BEGIN SESSION' in line:
            # 2 open session in a row without a close session implies a session that was terminated abnormaly
            self.__close_session(crashedsession = self.__session_opened)
            log_line_dict = self.__split_line(line)
            self.__open_session(log_line_dict)
            return True
        elif 'END SESSION' in line:
            self.__close_session()
            return True
        else:
            return False

    def __open_session(self, log_dict = None):
        self.__parsed_file.open_session(log_dict)
        self.__session_opened = True

    def __close_session(self, crashedsession = False):
        self.__parsed_file.close_session(crashedsession)
        self.__session_opened = False

    def __add_session_info(self, dict):
        self.__parsed_file.add_session_info(dict)


#
# Walk through a folder and its sub folders to find and analyse log files
#
class FolderLogParser(object):
    __filtering_status = {True: "in", False: "out"}

    # Constructor
    # @measure
    def __init__(self, **kwargs):
        try:
            self.__processed_file_count = 0
            self.__min_date = datetime(year=2015, month=1, day=1)
            self.__max_date = datetime(year=2100, month=12, day=31)
            self.__log_file_info_list = []
            self.__parsed_files = []
            self.__re_exclusions = PreparedExpressionList(kwargs[ParamNames.exclusions]) if ParamNames.exclusions in kwargs.keys() \
                else PreparedExpressionList()
            self.__re_categories = PreparedExpressionList(kwargs[ParamNames.categories]) if ParamNames.categories in kwargs.keys() \
                else PreparedExpressionList()
            self.__re_session_info = PreparedExpressionList(kwargs[ParamNames.session_info]) if ParamNames.session_info in kwargs.keys() \
                else PreparedExpressionList()
            self.__files_processed = 0
            self.__lines_parsed = 0
        except Exception:
            logging.exception('')
            raise

    # list of parsed log file objects
    @property
    def log_file_info_list(self):
        return self.__log_file_info_list

    def filter_on_date(self, log_file_info_to_filter):
        try:
            filtered_in = self.__min_date <= log_file_info_to_filter.date <= self.__max_date
            logging.info('Log file filtered %s: %s', self.__filtering_status[filtered_in],
                         log_file_info_to_filter.fullname)
            return filtered_in
        except Exception:
            logging.exception('')
            raise

    def parse(self, root_path, log_levels_filtered_in, min_date, max_date):
        try:
            self.__filtered_in_levels = log_levels_filtered_in
            self.prepare_levels()
            self.__min_date = min_date
            self.__max_date = max_date + timedelta(hours=23, minutes=59, seconds=59)
            self.__log_file_info_list = FileSeeker.walk_and_filter_in(root_path, "*.log", self.filter_on_date)
            logging.info("%s files found:", str(len(self.__log_file_info_list)))
            for log_file in self.__log_file_info_list:
                logging.info(log_file.fullname)
            self.do_parse_files()
        except Exception:
            logging.exception('')
            raise

    def prepare_levels(self):
        for key, level in self.__filtered_in_levels.items():
            self.__filtered_in_levels[key] = '[{0}]'.format(level.upper())

    def parse_one_file(self, file_info_to_parse):
        lt = other_helpers.ProcessTimer()
        try:
            params = {ParamNames.file_info: file_info_to_parse, ParamNames.exclusions: self.__re_exclusions, ParamNames.session_info: self.__re_session_info,
                      ParamNames.categories: self.__re_categories, ParamNames.filtered_in_levels: self.__filtered_in_levels,
                      ParamNames.min_date: self.__min_date, ParamNames.max_date: self.__max_date}
            log_parser = LogFileParser(**params)
            self.__processed_file_count  += 1
            parsed_file = log_parser.parsed_file
            if len(parsed_file.sessions) > 0:
                self.__parsed_files.append(parsed_file)
            else:
                logging.info("\t%s does not contains any lines to analyze", parsed_file.parsed_file_info.fullname)
            self.__lines_parsed += log_parser.lines_processed

            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                logging.info(
                    "\tDone {0} - {1}/{2} lines parsed - {3}/{4} files. CPU Time: {5} sec., {6} new lines to analyze from this file.".format(
                        parsed_file.parsed_file_info.fullname,
                        log_parser.lines_processed,
                        self.lines_parsed,
                        self.files_processed,
                        len(self.log_file_info_list),
                        lt.time_to_str,
                        parsed_file.lines_count))
            if DETAILLED_LOGGING_LEVEL > DETAILLED_LOGGING_FILE:
                logging.info( "%s", str(parsed_file))
        except Exception:
            logging.exception('')
            raise

    @property
    def parsed_files(self):
        return self.__parsed_files

    @property
    def lines_parsed(self):
        return self.__lines_parsed

    @property
    def total_lines_to_analyze(self):
        return sum(x.lines_count for x in self.parsed_files)

    @property
    def sessions_count(self):
        return sum(len(x.sessions) for x in self.parsed_files)

    @property
    def preserved_files_count(self):
        return len(self.__parsed_files)

    @property
    def files_processed(self):
        return self.__processed_file_count

    def do_parse_files(self):
        et = other_helpers.ElapseTimer()
        pt = other_helpers.ProcessTimer()
        try:
            logging.info("Start processing log files...")
            self.__files_processed = 0
            for file_info in self.__log_file_info_list:
                try:
                    self.parse_one_file(file_info)
                except Exception:
                    logging.exception('')
            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                logging.info(
                    "Processing log files done with a total of {0} files and {1} lines parsed in {2} sec. Output: {3} files with {4} sessions containing a total of {5} lines to process!!!".format(
                        self.__processed_file_count, self.lines_parsed, pt.time_to_str, self.preserved_files_count, self.sessions_count, self.total_lines_to_analyze))
                time_per_line = pt.time / self.lines_parsed
                logging.info("Elapsed time: {0} sec., average {1} msec. per line or {2} lines per minute".format(
                    et.time_to_str,
                    time_per_line * 1000,
                    round(60 * self.lines_parsed / pt.time)))
        except Exception:
            logging.exception('')
            raise

    @property
    def csv_header(self):
        return Headers

    # Save the log extraction to a CSV file
    def save_to_csv_file(self, csv_file_name = None):
        et = other_helpers.ElapseTimer()
        pt = other_helpers.ProcessTimer()
        try:
            csv_file_name = csv_helper.WriteDictToCSV(self, csv_file_name)

            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                time_per_line = pt.time / self.total_lines_to_analyze
                logging.info("Saved in CSV file {0}".format(csv_file_name))
                logging.info("Elapsed time: {0} sec., average {1} msec. per line or {2} lines per minute".format(
                    et.time_to_str,
                    time_per_line * 1000,
                    round(60 * self.total_lines_to_analyze / pt.time)))
        except Exception:
            logging.exception('')
            raise

