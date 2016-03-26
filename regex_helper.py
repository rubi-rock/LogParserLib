import logging
import uuid
import re
import datetime
import dateutil.parser


class PreparedExpressionList(dict):
    def __init__(self, exp_list=None):
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
        in_text = in_text.upper()  # allows simple text comparison to math (case insensitive)

        # process simple text search first - because they are more efficient than regular expression
        for key, plain_text in prepared_expressions.text_expressions.items():
            if plain_text in in_text:
                logging.debug("Text '{0}' found in line '{1}".format(plain_text, in_text))
                return key

        # process regular expression when nothing matches yet
        for key, expression in prepared_expressions.regular_expressions.items():
            result = result or expression.search(in_text)
            if result is not None:
                logging.debug("Expression '{0}' match found in line '{1}'".format(key, in_text))
                return key

        return result

# Very efficient string to date conversion because it replaces characters (c library in the backend) instead of Python
# string processing and copy/copy...
class StringDateHelper(object):
    __intab = '/-: .'
    __outtab = ',,,,,'
    __trantab = str.maketrans(__intab, __outtab)

    @staticmethod
    def str_iso_to_date(text):
        dt = None
        try:
            value_list = text.translate(StringDateHelper.__trantab)
            dt = datetime.datetime(*map(int, value_list))
        except:
            try:
                text = text[::-1].replace(":", ".", 1)[::-1]
                dt = dateutil.parser.parse(text)
            except:
                raise
        return dt