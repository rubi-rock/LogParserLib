from other_helpers import ListEnum


#
# Enumarates columns manipulated by the log parser for each session or log line
#
Headers = ListEnum(['file', 'date', 'time', 'type', 'session', 'group', 'has_crashed', 'category', 'level', 'module', 'message'])

#
# Enumerates the row type when saving/loading to/from a CSV file
#
RowTypes = ListEnum(['file', 'session', 'line'])


#
# Enumerates parameter names used in dict or kwargs to pass from a method/function to another one
#
ParamNames = ListEnum(['file_info', 'session_info', 'exclusions', 'categories', 'filtered_in_levels', 'min_date', 'max_date'])
