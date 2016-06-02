import logging
import uuid
import re
import datetime
import dateutil.parser
from constants import Headers, LOG_LEVEL_LIST


class PreparedExpressionList(dict):
    def __init__(self, exp_list=None, **kwargs):
        super().__init__(**kwargs)
        self.__expr_list = {}
        self.__prepared_expressions = {}
        self.__prepared_plain_text = {}
        self.__prepared = False
        self.initialize(exp_list)

    def initialize(self, expression_list=None):
        self.__reset()
        self.__expr_list = {}
        if expression_list is not None:
            for key, value in expression_list.items():
                self.add(value, key)
        self.__do_prepare()

    def __reset(self):
        self.__prepared_expressions = {}
        self.__prepared_plain_text = {}
        self.__prepared = False

    @property
    def all_expressions(self):
        return self.__expr_list

    @property
    def prepared(self):
        return self.__prepared

    @property
    def text_expressions(self):
        return self.__prepared_plain_text

    @property
    def regular_expressions(self):
        return self.__prepared_expressions

    def __str__(self):
        return str(self.__expr_list)

    def add(self, expression, name=None):
        if (expression is None) or (expression == ""):
            return
        if (name is None) or (name == ""):
            name = str(uuid.uuid4())
        self.__expr_list[name] = expression
        self.__reset()

    @property
    def combined_expressions(self):
        s = '({0})'.format(')|('.join(value for key, value in list(self.__expr_list.items())))
        return s

    def __do_prepare(self):
        if not self.__prepared:
            for key, expression in self.all_expressions.items():
                if str(expression).startswith("REGEX="):
                    regex = expression.replace("REGEX=", "", 1)
                    self.__prepared_expressions[regex] = re.compile(regex, flags=re.IGNORECASE or re.ASCII)
                    logging.info('Regular expression added to parser: {0}'.format(regex))
                else:
                    plain_text = str(expression).upper()
                    self.__prepared_plain_text[key] = plain_text
                    logging.info('Text added to parser: {0}'.format(plain_text))
            self.__prepared = True


class RegExpSet(object):
    @staticmethod
    def search_any_expression(in_text, prepared_expressions):
        result = None
        in_text = in_text.upper()  # allows simple text comparison to match (case insensitive)

        # process simple text search first - because they are more efficient than regular expression
        for key, plain_text in prepared_expressions.text_expressions.items():
            if plain_text in in_text:
                logging.debug("Text '{0}' found in line '{1}".format(plain_text, in_text))
                return key

        # process regular expression when nothing matches yet
        for key, expression in prepared_expressions.regular_expressions.items():
            result = expression.search(in_text)
            if result is not None:
                logging.debug("Expression '{0}' match found in line '{1}'".format(key, in_text))
                return key

        return result

    @staticmethod
    def is_text_containing(in_text, from_text_list):
        for lookup_text in from_text_list:
            if lookup_text in in_text:
                return lookup_text
        return None

    @staticmethod
    def is_text_begining_with(in_text, from_text_list):
        for lookup_text in from_text_list.items():
            if in_text.startswith(lookup_text):
                return lookup_text
        return None


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

    @staticmethod
    def get_line_parts(line, sep):
        broken_line = line.split(sep, 1)
        return broken_line

    @staticmethod
    def extract_message(line, sep=']'):
        broken_line = line.rsplit(sep, 1)
        return broken_line[len(broken_line) - 1].strip()

    @staticmethod
    def extract_time_measure_from_message(log_line_dict):
        try:
            value = 0
            area = ''
            time_str = None
            if log_line_dict.level == 'STATISTIC':
                if log_line_dict. message.rstrip().endswith('! sec.'):
                    time_str = str(log_line_dict.message.rsplit(': ', 1)[1].split(' ', 1)[0])
                elif 'sec !' in log_line_dict. message.rstrip():
                    try:
                        time_str = str(log_line_dict.message.rsplit('sec !', 1)[0].strip().rsplit(' ', 1)[1])
                    except:
                        pass

                if time_str is not None:
                    value = int(float(time_str) * 1000) # sec => ms
                    area = 'stats'
            elif log_line_dict.module is not None and log_line_dict.module.startswith('Mapgen') and log_line_dict.message.rstrip().endswith(' ms !!'):
                time_str = str(log_line_dict.message.rsplit('**', 1)[1].split(' ms !!', 1)[0])
                value = int(time_str)  # trunc less than millisecs
                area = 'map'

            if value > 0:
                log_line_dict.measure = value
            return value, area
        except:
            logging.exception(str(log_line_dict))
        return 0, ''

    # Low level function that is by default faster than a regular expression, which is worst here because MAPGEN logs
    # do not follow the standard log format (e.g.: mapgen.dci.exe) and this is worst when injected in an application
    # log file because it's not well integrate and there are 2 levels in lone log line:
    #   '2016/03/18 08:10:47:827, [LOG] [Mapgen.dll]  (*MAP2*) [SYST] TMapObject.Create... (Alias=, ConnectID=CBEDARD, RegPath=Software\Purkinje\DciCliniquev5\Local\MAP\Map2)'
    # [LOG] and [SYST] in this case (SYST is the right level to consider, even there why is it not SYST LOW to SYST HIGH, INFO, LOG
    # or whatever that makes sense and is homogeneous with the application logs?)
    #
    # Another issue: the date/time separator (before the log level) is sometimes a ' ' instead of ','
    #
    # By the way, the log format resulting of the injection of MAPGEN logs in an application log file is difficult to
    # parse with a regular expression and makes the performance really bad.
    #
    # This low level parser is x2+ fater than a regular expression.
    #
    @staticmethod
    def low_level_parse_log_line(line):
        log_dict = {}
        map = None
        fake_level_true_message = None

        try:
            # date & time
            tmp = line.split(',', 1)
            log_dict[Headers.date] = tmp[0]

            # process the map tag when reading a mapgen file (e.g.: mapgen.dci.exe)
            if tmp[1].strip()[0] == '(':
                tmp = tmp[1].split('(')[1].split(')')
                map = tmp[0]

            # let's go for a '[level] [module]' block parsing
            if tmp[1].strip()[0] == '[':
                # level
                tmp = tmp[1].split('[', 1)[1].split(']', 1)
                log_dict[Headers.level] = tmp[0]

                # optional: module
                if tmp[1].strip()[0] == '[':
                    tmp = tmp[1].split('[', 1)[1].split(']', 1)
                    log_dict[Headers.module] = tmp[0]
                else:
                    log_dict[Headers.module] = None
            # probably one of those not standard logs (e.g.: CPU)... :-(
            else:
                log_dict[Headers.level] = LOG_LEVEL_LIST.LOG
                log_dict[Headers.module] = None

            # process the map tag and the level again when reading mapgen information in an application file (e.g.: dci.exe)
            if tmp[1].strip()[0] == '(':
                tmp = tmp[1].split('(', 1)[1].split(')', 1)
                map = tmp[0]
            # Complicated!!! Sometimes it's a log level from MAPGEN, sometimes it a log from an application that added
            # a text between brackets at the beginning of the message. Cannot trust that there is (MAP!) or something
            # like that just before because it's not always the case for the MAPGEN logs
            if tmp[1].strip()[0] == '[':
                tmp = tmp[1].split('[', 1)[1].split(']', 1)
                if tmp[0] in LOG_LEVEL_LIST.as_list:
                    log_dict[Headers.level] = tmp[0]
                else:
                    fake_level_true_message = tmp[0]

            # message
            log_dict[Headers.message] = (map + ' ' if map is not None else '') + \
                                        (fake_level_true_message + ' ' if fake_level_true_message is not None else '') + \
                                        tmp[1].lstrip()

        except:
            logging.exception('Unable to parse line: %s', line)

        return log_dict if len(log_dict) > 0 else None


# Very efficient string to date conversion because it replaces characters (c library in the backend) instead of Python
# string processing and copy/copy...
class StringDateHelper(object):
    __intab = '/-: .'
    __outtab = ',,,,,'
    __trantab = str.maketrans(__intab, __outtab)

    @staticmethod
    def __str_to_date_using_map(text):
        transtext = text.translate(StringDateHelper.__trantab)
        values = [int(x) for x in transtext.split(',')]
        values[-1] = values[-1] * 1000
        dt = datetime.datetime(*values)
        return dt

    @staticmethod
    def str_iso_to_datetime(text):
        dt = None
        try:
            dt = StringDateHelper.__str_to_date_using_map(text)
        except:
            try:
                text = text[::-1].replace(":", ".", 1)[::-1]
                dt = dateutil.parser.parse(text)
            except:
                raise
        return dt
