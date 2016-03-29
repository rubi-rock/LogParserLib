from other_helpers import ListEnum

#
#
#
LogLevels = ListEnum(
    [  # Standard log levels
        'LOG', 'OPERATING_SYSTEM', 'FATAL', 'EXCEPTION_TRACK', 'LEAK', 'WARNING', 'STATISTIC', 'TRACE', 'DUMP',
        'MESSAGES', 'UNKNOWN',
        # Map log levels
        'SYST HIGH', 'SYST MEDIUM', 'SYST LOW', 'SYST', 'DEBUG'])   # Mapgen also has a LOG level, we don't duplicate it
ErrorLogLevels = 'OPERATING_SYSTEM|FATAL|EXCEPTION_TRACK|LEAK|STATISTIC|SYST HIGH|SYST MEDIUM'

#
# Enumarates columns manipulated by the log parser for each session or log line
#
Headers = ListEnum(
    ['file', 'date', 'time', 'type', 'session', 'group', 'has_crashed', 'category', 'level', 'module', 'message', 'context'])

#
# Enumerates the row type when saving/loading to/from a CSV file
#
RowTypes = ListEnum(['file', 'session', 'line'])

#
# Enumerates parameter names used in dict or kwargs to pass from a method/function to another one
#
ParamNames = ListEnum(
    ['file_info', 'session_info', 'exclusions', 'categories', 'filtered_in_levels', 'min_date', 'max_date', 'performance_trigger_in_ms', 'provide_context'])

# Be careful: this one does not use regular expression nor upper or any facilitator for performance reasons.
# Therefore the text we are looking for must be exactly this one and with this case.
DefaultSessionInfo = [
    'Version :',
    'Client Session Protocol:',
    'User logged :',
    'CurrentConfig',
    'Active ConfigGroup:'
]

# Default performance trigger in ms: when none it ignores statistics, else it looks at it and keep only what is higher
# than specified
PerformanceTriggerOff = None
