import logging
import os.path
from datetime import timedelta

# keep LogUtility, even if it seems unused, it sets up the logging automatically
import os_path_helper
import other_helpers
import xml_excel_helper
from constants import Headers, ParamNames, DefaultSessionInfo, DEFAULT_EXCLUSIONS, DEFAULT_LOG_LEVELS, StatusBarValues, \
    DEFAULT_CATEGORIES, DEFAULT_PERFORMANCE_TRIGGER_IN_MS, SAVE_FILE_BY_FILE, DEFAULT_CONTEXT_LENGTH, MIN_DATE, MAX_DATE
from log_parser_objects import log_context, Log_Line, ParsedLogFile
from os_path_helper import FileSeeker
from regex_helper import RegExpSet, PreparedExpressionList, LogLineSplitter
import csv_helper
import xlsx_helper

# from pythonbenchmark import measure

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

    Session Information:
    --------------------
    Found from multiple lines of each session, this information is collected and saved in the 'message' field of the
    session to provide context such as the user ID, the version, the config groups...
'''

# Change the log level of DETAILLED_LOGGING_LEVEL to put more detail on the console (logging.info)
DETAILLED_LOGGING_NONE = 0  # Nothing
DETAILLED_LOGGING_FILE = 1  # Statis about the file only
DETAILLED_LOGGING_SESSION = 2  # details of the file (sessions & lines preserved)
DETAILLED_LOGGING_LEVEL = DETAILLED_LOGGING_NONE


#
# Instance of a log session : between 'BEGIN SESSION' and 'END SESSION'
#
#
# Parsed log line : date, time, level, module, message... in a structured way. It saves memory because a dict has to
# save names and values which is memory consuming
#
#
# Parsed log file: result of the parsing
#
#
# Parses a log file and produces a ParsedLogFile when not empty
#
class LogFileParser(object):
    # Constructor
    def __init__(self, **params):
        try:
            log_context.clear()
            self.__cancel_callback = params[ParamNames.cancel_callback]
            self.__lines_processed = 0
            self.__re_exclusions = params[ParamNames.exclusions]
            self.__re_categories = params[ParamNames.categories]
            self.__session_info = params[ParamNames.session_info]
            self.__performance_trigger_in_ms = params[ParamNames.performance_trigger_in_ms]
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
    def __extract_session_info(self, log_line_dict):
        result = RegExpSet.is_text_containing(log_line_dict.message, self.__session_info)
        if result is not None:
            message = LogLineSplitter.get_line_parts(log_line_dict.message, ':')
            info = {message[0].strip(): message[1].strip()}
            self.__add_session_info(info)
        return None

    # Split a log line in its components (date, time, level, [module], message)
    @staticmethod
    def __split_line(line):
        try:
            log_dict = LogLineSplitter.low_level_parse_log_line(line)
            return Log_Line(log_dict)
        except Exception:
            logging.exception('')
            raise

    # Set the category of the line when it applies
    def __set_line_category(self, line_dict):
        category = RegExpSet.search_any_expression(line_dict.message, self.__re_categories)
        if category is not None:
            category = category.strip("0123456789.")  # remove numbers before category names (e.g. 71.EXCEPTION)
            line_dict.set_value(Headers.category, category)

    # Parse one log file based on the exclusions (logs to ignore) and categories (which category the log belongs to).
    def parse(self):
        try:
            file_name = self.parsed_file.parsed_file_info.fullname
            if not os.path.exists(file_name):
                return
            bak_file_name = file_name + '.bak'
            if os.path.exists(bak_file_name):
                self.__do_parse_file(bak_file_name)
            self.__do_parse_file(file_name)

        except Exception:
            logging.exception('')
            raise

    #
    def __do_parse_file(self, file_name):
        logging.info("Processing file: %s", file_name)
        # required to use latin-1 because logs contain french (i.e.: çéèà...)
        text_file = open(file_name, mode='rt', encoding='iso-8859-1')
        try:
            for line in iter(text_file):
                self.__lines_processed += 1

                if self.__cancel_callback is not None and self.__lines_processed % 100000:
                    cancelled = self.__cancel_callback()
                    if cancelled:
                        break

                if len(line) <= 1:
                    continue

                log_line_dict = self.__split_line(line)
                if self.__filter_log_line(log_line_dict, line):
                    continue

                filtered_out = True
                for key, level in self.__filtered_in_levels.items():
                    if level in line:
                        filtered_out = False

                # If not added when it was triggered as an Exception or a new session then it must be part of the
                # context
                if filtered_out:
                    continue

                if not self.__is_line_excluded(line):
                    self.__set_line_category(log_line_dict)
                    self.__parsed_file.add_log(log_line_dict)
        finally:
            self.__process_session(None)  # Close the session if not yet done (crashed session?)
            text_file.close()

    #
    def __filter_log_line(self, log_line_dict, line):
        if log_line_dict is None:
            # when statistics level is active there is too much garbage: not well formatted lines that are not recognized to log that
            # logging.error("Unable to parse line: %s", line)
            return True

        if not self.__min_date.date() <= log_line_dict.date <= self.__max_date.date():
            return True  # because it's not in the date range to process

        log_context.append(line)

        if self.__process_session(log_line_dict):
            return True  # because it was BEGIN SESSION or END SESSION

        if self.__extract_session_info(log_line_dict):
            return True  # because it was about the session info

        # Here process the log performance trigger
        if self.__performance_trigger_in_ms is not None:
            if self.__track_potential_performance_issue(log_line_dict):
                return True

        return False

    #
    def __process_session(self, log_line_dict):
        try:
            if log_line_dict is not None and log_line_dict.message.startswith('BEGIN SESSION'):
                # 2 open session in a row without a close session implies a session that was terminated abnormaly
                self.__close_session(crashedsession=self.__session_opened)
                self.__open_session(log_line_dict)
                return True
            elif log_line_dict is None or log_line_dict.message.startswith('END SESSION'):
                if not self.__session_opened:
                    self.add_misaligned_ended_session(log_line_dict)
                self.__close_session()
                return True
            elif log_line_dict is not None and 'session is terminated' in log_line_dict.message:
                self.__set_session_termination_reason(log_line_dict.message)
                return True
            else:
                return False
        except:
            logging.exception('')
            return False

    def __open_session(self, log_dict=None):
        self.__parsed_file.open_session(log_dict)
        self.__session_opened = True

    def add_misaligned_ended_session(self, log_dict):
        self.__parsed_file.add_misaligned_ended_session(log_dict)

    def __close_session(self, crashedsession=False):
        self.__parsed_file.close_session(crashedsession)
        self.__session_opened = False

    def __add_session_info(self, dict):
        self.__parsed_file.add_session_info(dict)

    def __set_session_termination_reason(self, reason):
        self.parsed_file.set_termination_reason(reason)

    def __track_potential_performance_issue(self, log_line_dict):
        if self.__performance_trigger_in_ms is not None:
            if log_line_dict.level == 'STATISTIC':
                time_value = LogLineSplitter.extract_time_measure_from_message(log_line_dict.message)
                if time_value > self.__performance_trigger_in_ms:
                    log_line_dict.set_value(Headers.category, 'PERFORMANCE')
                    self.parsed_file.add_log(log_line_dict)
                    return True
        return False


#
# Walk through a folder and its sub folders to find and analyse log files
#
class FolderLogParser(object):
    __filtering_status = {True: "in", False: "out"}

    # Constructor
    # @measure
    def __init__(self, **kwargs):
        try:
            self.__stopped = False
            self.__timer = None
            self.__progress_callback = None
            self.__cancel_callback = None
            if ParamNames.provide_context in kwargs.keys() and kwargs[ParamNames.provide_context] is not None:
                log_context.limit = kwargs[ParamNames.provide_context]
            else:
                log_context.limit = DEFAULT_CONTEXT_LENGTH
            self.__csv_file_name = os_path_helper.generate_file_name('log-files-parsed - ')
            self.__processed_file_count = 0
            self.__root_parth = ""
            self.__min_date = MIN_DATE
            self.__max_date = MAX_DATE
            self.__log_file_info_list = []
            self.__parsed_files = []
            self.__save_file_by_file = kwargs[
                ParamNames.save_file_by_file] if ParamNames.save_file_by_file in kwargs.keys() \
                else SAVE_FILE_BY_FILE
            self.__performance_trigger_in_ms = kwargs[
                ParamNames.performance_trigger_in_ms] if ParamNames.performance_trigger_in_ms in kwargs.keys() \
                else DEFAULT_PERFORMANCE_TRIGGER_IN_MS
            self.__re_exclusions = PreparedExpressionList(
                kwargs[ParamNames.exclusions]) if ParamNames.exclusions in kwargs.keys() \
                else PreparedExpressionList(DEFAULT_EXCLUSIONS)
            self.__re_categories = PreparedExpressionList(
                kwargs[ParamNames.categories]) if ParamNames.categories in kwargs.keys() \
                else PreparedExpressionList(DEFAULT_CATEGORIES)
            self.__session_info = kwargs[ParamNames.session_info] if ParamNames.session_info in kwargs.keys() \
                else DefaultSessionInfo
            self.__files_processed = 0
            self.__lines_parsed = 0
            self.__lines_to_analyze_count = 0
            self.__last_logfile_lines_parsed = 0
            self.__filtered_in_levels = DEFAULT_LOG_LEVELS
        except Exception:
            logging.exception('')
            raise

    # list of parsed log file objects
    @property
    def log_file_info_list(self):
        return self.__log_file_info_list

    @property
    def files_and_sessions_and_lines_count(self):
        return len(self.parsed_files) + self.sessions_count + self.total_lines_to_analyze

    @property
    def folder(self):
        return self.__root_parth

    @property
    def from_date(self):
        return self.__min_date

    @property
    def to_date(self):
        return self.__max_date

    def filter_on_date(self, log_file_info_to_filter):
        try:
            # Just ignore the MAPGEN files, their format is not as expected (Purkinje Standard Log Format as implemented
            # in debug tools to be compliant in 2.0 with the log format from 1.x at that time). Anyway all logs are now
            # (5.13+) in the same log file than the running application instead of a separate log file
            #
            # Same thing for other files like LogInstallDB, ... they do not follow any standard, there is no ',' after
            # the time... Don't know where do they come from?
            if log_file_info_to_filter.file_name.startswith('mapgen.') \
                    or log_file_info_to_filter.file_name == 'LogBuildDBImage.log' \
                    or log_file_info_to_filter.file_name == 'Installed.log' \
                    or log_file_info_to_filter.file_name == 'LogInstallDB.log' \
                    or log_file_info_to_filter.file_name == 'LogSetup.log' \
                    or log_file_info_to_filter.file_name == 'BuildDBImage.log':
                return False

            # keeps only files that are in the requested date range - be careful: logs changed recently can contain logs
            # requested from an older date. Therefore the filter can apply only on the end date.
            filtered_in = self.__min_date <= log_file_info_to_filter.date
            logging.info('Log file filtered %s: %s', self.__filtering_status[filtered_in],
                         log_file_info_to_filter.fullname)
            return filtered_in
        except Exception:
            logging.exception('')
            raise

    def parse(self, root_path, log_levels_filtered_in=DEFAULT_LOG_LEVELS, min_date=MIN_DATE, max_date=MAX_DATE):
        try:
            self.__filtered_in_levels = log_levels_filtered_in
            self.prepare_levels()
            self.__root_parth = root_path
            self.__min_date = min_date
            self.__max_date = max_date + timedelta(hours=23, minutes=59, seconds=59)
            self.__log_file_info_list = FileSeeker.walk_and_filter_in(root_path, ['*.log'],
                                                                      self.filter_on_date)
            log_text = "{0} files found:".format(len(self.__log_file_info_list))
            logging.info(log_text)
            self.__provide_feedback(**{StatusBarValues.text: log_text})

            for log_file in self.__log_file_info_list:
                logging.info(log_file.fullname)
                self.__provide_feedback(**{StatusBarValues.text: log_file.fullname})

            self.do_parse_files()
        except Exception:
            logging.exception('')
            raise

    def __provide_feedback(self, **kwargs):
        if self.__progress_callback is not None:
            if self.__timer is not None:
                kwargs[StatusBarValues.elapsed_time] = self.__timer.time_to_str
            kwargs[StatusBarValues.lines_to_analyze] = self.total_lines_to_analyze
            self.__stopped = self.__progress_callback(**kwargs)

    def prepare_levels(self):
        for key, level in self.__filtered_in_levels.items():
            self.__filtered_in_levels[key] = '[{0}]'.format(level.upper())

    def parse_one_file(self, file_info_to_parse):
        lt = other_helpers.ProcessTimer()
        try:
            params = {ParamNames.file_info: file_info_to_parse, ParamNames.exclusions: self.__re_exclusions,
                      ParamNames.session_info: self.__session_info,
                      ParamNames.categories: self.__re_categories,
                      ParamNames.performance_trigger_in_ms: self.__performance_trigger_in_ms,
                      ParamNames.filtered_in_levels: self.__filtered_in_levels,
                      ParamNames.min_date: self.__min_date, ParamNames.max_date: self.__max_date,
                      ParamNames.cancel_callback: self.__cancel_callback}
            log_parser = LogFileParser(**params)
            self.__processed_file_count += 1
            parsed_file = log_parser.parsed_file
            if len(parsed_file.sessions) > 0:
                self.__parsed_files.append(parsed_file)
            else:
                log_text = "\t{0} does not contains any lines to analyze".format(parsed_file.parsed_file_info.fullname)
                logging.info(log_text)
                self.__provide_feedback(**{StatusBarValues.text: log_text})

            self.__lines_parsed += log_parser.lines_processed

            log_text = "\tDone {0} - {1}/{2} lines parsed - {3}/{4} files. CPU Time: {5} sec., {6} new lines to analyze from this file.".format(
                parsed_file.parsed_file_info.fullname,
                log_parser.lines_processed,
                self.lines_parsed,
                self.files_processed,
                len(self.log_file_info_list),
                lt.time_to_str,
                parsed_file.lines_count)
            self.__provide_feedback(**{StatusBarValues.text: log_text,
                                       StatusBarValues.total_lines: self.lines_parsed,
                                       StatusBarValues.lines_processed: log_parser.lines_processed,
                                       StatusBarValues.total_files: len(self.log_file_info_list),
                                       StatusBarValues.files_processed: self.files_processed
                                       })
            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                logging.info(log_text)
            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_SESSION:
                logging.info(str(parsed_file))

            if len(parsed_file.sessions) > 0:
                return parsed_file
            else:
                return None
        except Exception:
            logging.exception('')
            raise

    def set_progress_callback(self, callback):
        self.__progress_callback = callback

    def set_cancel_callback(self, callback):
        self.__cancel_callback = callback

    @property
    def parsed_files(self):
        return self.__parsed_files

    @property
    def lines_parsed(self):
        return self.__lines_parsed

    @property
    def total_lines_to_analyze(self):
        return self.__lines_to_analyze_count

    @property
    def sessions_count(self):
        return sum(x.session_count for x in self.parsed_files)

    @property
    def preserved_files_count(self):
        return len(self.__parsed_files)

    @property
    def files_processed(self):
        return self.__processed_file_count

    def do_parse_files(self):
        self.__timer = other_helpers.ElapseTimer()
        pt = other_helpers.ProcessTimer()
        try:
            logging.info("Start processing log files...")
            self.__files_processed = 0
            for file_info in self.__log_file_info_list:
                try:
                    parsed_file = self.parse_one_file(file_info)
                    if parsed_file is not None:
                        self.__lines_to_analyze_count += parsed_file.lines_count
                        self.__save_parsed_file_to_csv(parsed_file)
                    if self.__stopped:
                        break
                except Exception:
                    logging.exception('')

            log_text = "Processing log files done with a total of {0} files and {1} lines parsed in {2} sec. Output: {3} files with {4} sessions containing a total of {5} lines to process!!!".format(
                self.__processed_file_count, self.lines_parsed, pt.time_to_str, self.preserved_files_count,
                self.sessions_count, self.total_lines_to_analyze)
            self.__provide_feedback(**{StatusBarValues.text: log_text})

            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                logging.info(log_text)

            time_per_line = pt.time / self.lines_parsed if self.lines_parsed > 0 else 0
            log_text = "Elapsed time: {0} sec., average {1} msec. per line or {2} lines per minute".format(
                self.__timer.time_to_str,
                time_per_line * 1000,
                round(60 * self.lines_parsed / pt.time))
            self.__provide_feedback(**{StatusBarValues.text: log_text})

            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                logging.info(log_text)

            if not self.__save_file_by_file:
                self.save_to_csv_file()
        except Exception:
            logging.exception('')
            raise

    def __save_parsed_file_to_csv(self, parsed_file):
        if self.__save_file_by_file:
            csv_helper.WriteParsedLoFileToCSV(parsed_file, self.__csv_file_name)
            #xlsx_helper.WriteParsedLoFileToXSLX(parsed_file, self.__csv_file_name.replace('csv', 'xlsx'))
            self.__parsed_files.clear()

    # Save the log extraction to a CSV file
    def save_to_csv_file(self, xslx_file_name=None):
        if xslx_file_name is None:
            xslx_file_name = os_path_helper.generate_file_name('log-files-parsed - ') + '.xlsx'

        et = other_helpers.ElapseTimer()
        pt = other_helpers.ProcessTimer()
        try:
            xslx_file_name = xml_excel_helper.WriteLogFolderParserToXSLX(self, xslx_file_name)

            if DETAILLED_LOGGING_LEVEL >= DETAILLED_LOGGING_FILE:
                time_per_line = pt.time / self.total_lines_to_analyze if self.total_lines_to_analyze > 0 else 0
                logging.info("Saved in CSV file {0}".format(xslx_file_name))
                logging.info("Elapsed time: {0} sec., average {1} msec. per line or {2} lines per minute".format(
                    et.time_to_str,
                    time_per_line * 1000,
                    round(60 * self.total_lines_to_analyze / (pt.time if pt.time > 0 else 1))))
        except Exception:
            logging.exception('')
            raise
