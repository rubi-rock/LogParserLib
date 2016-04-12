import copy
import logging
import os
from datetime import datetime, date

from constants import Headers, LOG_LEVEL_LIST, RowTypes
from other_helpers import ListEnum
from regex_helper import StringDateHelper
from constants import DEFAULT_CONTEXT_LENGTH, MIN_DATE


# Date used when the date and time from the log line cannot be parsed
UNPARSABLE_DATETIME = datetime(year=1900, month=1, day=1, hour=0)


#
#   Log context: a log line list that came before a log entry that has been selected to be part of the resulting analysis
#
class LogContext(list):
    def __init__(self, max_lines=DEFAULT_CONTEXT_LENGTH):
        super().__init__()
        self.__limit = max_lines

    def __str__(self):
        return '\n'.join([str(log) for log in self])

    def __clear(self):
        while len(self) > self.__limit:
            if len(self)  > 0:
                self.pop(0)

    def append(self, p_object):
        self.__clear()
        super(LogContext, self).append(p_object)

    @property
    def limit(self):
        return self.__limit

    @limit.setter
    def limit(self, value):
        self.__limit = value
        self.__clear()

# Keep it global for now, it's easier to log the previous log line no matter from where
log_context = LogContext()

class GroupSeq(object):
    def __init__(self):
        self.__group_seq = 0

    def next(self):
        self.__group_seq += 1
        return self.__group_seq
group_seq = GroupSeq()


class LogSession(object):
    __id_seq = 0

    # constructor
    def __init__(self, log_dict=None):
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
            self.__has_crashed = False
            self.__termination_reason = None
            self.__info = {}
            self.__group = 0
            self.__last_log_time = MIN_DATE
        except Exception:
            logging.exception('')
            raise

    # serialize as string to help for logging and debugging
    def __str__(self):
        try:
            if len(self.__lines) > 0:
                return "\n\tSession #{0} - {1}\n\t\tEntries:\n\t\t{2}".format(self.__id, self.message, "\n\t\t".join(
                    str(entry) for entry in self.__lines))
            else:
                return "\n\tSession #{0} - 0 entries".format(self.__id)

        except Exception:
            logging.exception('')
            raise

    # Add a filtered in log line
    def add_log(self, log_dict):
        dt = log_dict.datetime
        delta = dt - self.__last_log_time
        if delta.seconds > 1:
            self.__group = group_seq.next()

        log_dict.set_value(Headers.group, self.__group)
        self.__last_log_time = dt

        self.__lines.append(log_dict)

    # Add an entry to the session to indicate when the session did not terminate properly (killed session, crash...)
    def add_crashed_session_log(self):
        if len(self.lines) > 0:
            idx = len(self.lines) - 1
            crash_log_line = copy.deepcopy(self.lines[idx])
        else:
            # usually the LogLine creator takes care of splitting date and time from the date (text). We must keep it
            # consistent
            crash_log_line = Log_Line(
                {Headers.module: self.__module, Headers.date: self.__date, Headers.time: self.__time})

        self.__has_crashed = True
        crash_log_line.set_value(Headers.has_crashed, self.__has_crashed )

        if self.__termination_reason is not None:
            crash_log_line.set_value(Headers.message, self.__termination_reason)
            crash_log_line.set_value(Headers.category, 'KILLED')
        else:
            crash_log_line.set_value(Headers.message, 'SESSION TERMINATED ABNORMALLY - REASON UNKNOWN (log "END SESSION" not found)')
            crash_log_line.set_value(Headers.category, 'CRASHED')

        crash_log_line.set_value(Headers.level, LOG_LEVEL_LIST.EXCEPTION_TRACK)
        crash_log_line.set_value(Headers.group, 99999)  # Special group for the crashed indicator
        self.add_log(crash_log_line)

    # Add information to the session (version, user, configgroup...)
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

    # Represents the information related to the session (version, user, configgroup...)
    @property
    def message(self):
        return '[{0}]'.format(']['.join("{0}={1}".format(key, value) for key, value in self.__info.items()))

    # Set the termination reason when known
    def set_termination_reason(self, reason):
        self.__termination_reason = reason

    # Export the session as a dictionary to be saved in a CSV file
    # Todo: check if not faster an more readable if those properties are stored in a dict by default then pass the dict instead of manipulation a bunch of class members
    @property
    def as_csv_row(self):
        row = dict()
        row[Headers.type] = RowTypes.session
        row[Headers.date] = self.__date
        row[Headers.time] = self.__time
        row[Headers.session] = self.__id
        row[Headers.has_crashed] = self.has_crashed
        row[Headers.module] = self.__module
        row[Headers.message] = self.message
        return row


class Log_Line(object):
    # Constructor
    def __init__(self, line_dict):
        self.__data = line_dict
        self.__data[Headers.group] = 0
        self.__data[Headers.type] = RowTypes.line
        self.__data[Headers.context] = str(log_context)
        self.__fixe_date()

    # Fix the date format. There are several cases:
    #   . the date is already a date type - fine don't fix anything
    #   . the date is text: then convert it to date and time objects. Sometimes the format is not "standard" therefore
    #     instead of using the very efficient StringDateHelper.str_iso_to_date method then it uses the
    #     dateutil.parser.parse method from Python which is very flexible but slow: ratio = x6
    def __fixe_date(self):
        value = self.__data[Headers.date]
        if type(value) is not date:
            try:
                dt = StringDateHelper.str_iso_to_datetime(value)
            except:
                dt = UNPARSABLE_DATETIME
            self.__data[Headers.date] = dt.date()
            self.__data[Headers.time] = dt.time()


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
    def context(self):
        if Headers.context in self.__data.keys():
            return self.__data[Headers.context]
        else:
            return None

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
        if Headers.context in self.__data.keys():
            return "[date={0}][time={1}][category={2}][level={3}][module={4}][group={5}][message={6}][context={7}]".format(
                self.date, self.time, self.category, self.level, self.module, self.group, self.message, self.__data[Headers.context])
        else:
            return "[date={0}][time={1}][category={2}][level={3}][module={4}][group={5}][message={6}]".format(
                self.date, self.time, self.category, self.level, self.module, self.group, self.message)

    @property
    def datetime(self):
        return datetime.combine(self.date, self.time)


    @property
    def as_csv_row(self):
        return self.__data


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

    @property
    def session_count(self):
        return len(self.__sessions)

    # Returns the line count - all file's sessions together
    @property
    def lines_count(self):
        return sum(session.lines_count for session in self.__sessions)

    # Add a log entry (line) to the log, the session change detection is done here
    def add_log(self, log_dict):
        try:
            if self.__current_session is None:
                self.open_session()

            self.__current_session.add_log(log_dict)
        except Exception:
            logging.exception('')
            raise

    # Open a new session and set the current session - used to add new logs
    def open_session(self, log_dict=None):
        self.__current_session = LogSession(log_dict)
        self.__sessions.append(self.__current_session)


    # close the current session - if empty then delete it because we are not interested in sessions not meanningful
    def close_session(self, crashedsession=False):
        # document a crashed session (application crash, process killed)
        if crashedsession:
            self.__current_session.add_crashed_session_log()

        # flush an empty session
        if self.__current_session is not None and len(self.__current_session.lines) == 0:
            self.__sessions.remove(self.__current_session)
            self.__current_session = None

    def add_misaligned_ended_session(self, log_dict):
        if log_dict is None:
            return
        self.open_session(log_dict)
        log_dict.set_value(Headers.category, 'CRASHED')
        log_dict.set_value(Headers.type, 'UNMATCHED END SESSION')
        self.add_log(log_dict)
        self.close_session()

    def add_session_info(self, dict):
        if self.__current_session is None:
            self.open_session()
        self.__current_session.add_session_info(dict)

    def set_termination_reason(self, reason):
        if self.__current_session is None:
            self.open_session()
        self.__current_session.set_termination_reason(reason)

    @property
    def as_csv_row(self):
        row = dict()
        row[Headers.type] = RowTypes.file
        row[Headers.file] = self.parsed_file_info.fullname
        row[Headers.date] = self.parsed_file_info.date.date()
        row[Headers.time] = self.parsed_file_info.date.time()
        return row


#
#
#
UserSessionTokens = ListEnum(['folder', 'application', 'user', 'date', 'key'])

#
#
#
def build_user_session_struct(log_filename, date):
    result = {}
    tmp = (os.path.sep * 3 + log_filename)
    tmp = tmp.rsplit(os.path.sep, 1)
    result[UserSessionTokens.application] = ''.join(c for c in os.path.splitext(os.path.basename(tmp[1]))[0] if not c.isdigit())
    tmp = tmp[0].rsplit(os.path.sep, 1)
    result[UserSessionTokens.user] = tmp[1]
    result[UserSessionTokens.folder] = tmp[0].strip(os.path.sep)
    result[UserSessionTokens.date] = date
    result[UserSessionTokens.key] = '|'.join(str(value) for value in result.values())
    return result


#
#
#
class  UserSession(object):
    def __init__(self, **values):
        self.__values = values
        self.__session_count = 1

    def add_session(self):
        self.__session_count += 1

    @property
    def key(self):
        return self.__values[UserSessionTokens.key]
    @property
    def folder(self):
        return self.__values[UserSessionTokens.folder]
    @property
    def user(self):
        return self.__values[UserSessionTokens.user]
    @property
    def application(self):
        return self.__values[UserSessionTokens.application]
    @property
    def date(self):
        return self.__values[UserSessionTokens.date]
    @property
    def session_count(self):
        return self.__session_count


#
#
#
class UserSessionStats(object):
    def __init__(self):
        self.__items = {}

    def add_session(self, log_file_name, date):
        user_session = build_user_session_struct(log_file_name, date)
        key = user_session[UserSessionTokens.key]
        if key in self.__items.keys():
            self.__items[key].add_session()
        else:
            self.__items[key] = UserSession(**user_session)

    @property
    def items(self):
        return self.__items