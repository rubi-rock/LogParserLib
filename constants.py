from other_helpers import ListEnum
from _datetime import datetime
from collections import OrderedDict

MIN_DATE = datetime(year=2015, month=1, day=1)
MAX_DATE = datetime(year=2100, month=12, day=31)

#
#
#
LOG_LEVEL_LIST = ListEnum(
    [  # Standard log levels
        'LOG', 'OPERATING_SYSTEM', 'FATAL', 'EXCEPTION_TRACK', 'LEAK', 'WARNING', 'STATISTIC', 'ACTION', 'TRACE',
        'DUMP',
        'MESSAGES', 'UNKNOWN',
        # Map log levels
        'SYST HIGH', 'SYST MEDIUM', 'SYST LOW', 'SYST', 'DEBUG'])  # Mapgen also has a LOG level, we don't duplicate it
ErrorLogLevels = 'OPERATING_SYSTEM|FATAL|EXCEPTION_TRACK|LEAK|STATISTIC|SYST HIGH|SYST MEDIUM'

#
# Enumarates columns manipulated by the log parser for each session or log line
#
Headers = ListEnum(
    ['file', 'date', 'time', 'type', 'session', 'user', 'application', 'machine', 'group', 'has_crashed', 'category', 'measure', 'level', 'module', 'message',
     'context'])
IndexedHeaders = {x: i + 1 for i, x in enumerate(Headers)}

#
# Enumerates the row type when saving/loading to/from a CSV file
#
RowTypes = ListEnum(['error', 'file', 'session', 'line'])

#
# Enumerates the info shared to be displayed in a statusbar
#
StatusBarValues = ListEnum(
    ['text', 'total_files', 'files_processed', 'total_lines', 'lines_processed', 'lines_to_analyze', 'elapsed_time'])

#
# Enumerates parameter names used in dict or kwargs to pass from a method/function to another one
#
ParamNames = ListEnum(
    ['file_info', 'session_info', 'exclusions', 'categories', 'filtered_in_levels', 'min_date', 'max_date',
     'save_file_by_file', 'performance_trigger_in_ms', 'provide_context', 'cancel_callback', 'start_session_callback', 'end_session_callback'])

# Be careful: this one does not use regular expression nor upper or any facilitator for performance reasons.
# Therefore the text we are looking for must be exactly this one and with this case.
DefaultSessionInfo = [
    'Version :',
    'Client Session Protocol:',
    'User logged :',
    'CurrentConfig',
    'Active ConfigGroup:'
]

DEFAULT_EXCLUSIONS = OrderedDict([
    ('1', 'BEGIN SESSION'),
    ('2', 'END SESSION'),
    # DOSSIER LOG EXCLUSIONS
    ('10', 'OPERATING_SYSTEM=0,FATAL=1,EXCEPTION_TRACK=2'),
    ('11', 'Available levels : LOG=0,OPERATING_SYSTEM=1,FATAL=2'),
    ('12', '----> Current Level:'),
    ('15', 'DebugTools created by)'),
    ('16', 'DebugTools destroyed by'),
    ('17', 'plugged to DebugTools'),
    ('20', 'User logged :'),
    ('21', 'Client Session Protocol:'),
    ('22', 'Client Session State:'),
    ('23', 'CurrentConfig:'),
    ('25', 'Cache - Limit:'),
    ('26', '================== CACHES STATISTICS ====================='),
    ('30', 'REGEX=Can not find module (.*)\\Bin\\PurkScanContentProvider\.dll'),
    ('31', 'Can not find module Cmdlinetool.dll'),
    ('32', "SCANSETUP: Le handle de module n'est pas accessible"),
    ('33', 'Record class was not registered in the DataRecordFactory'),
    ('40', 'REGEX=Version[ ]*: [0-9\.]{12}'),
    ('41', 'Interface: '),
    ('42', 'MaxBlobSize:'),
    ('43', 'Server Name:'),
    ('44', 'Database:'),
    ('45', 'program: '),
    ('46', 'REGEX=^Config\:'),
    ('47', '* Context * '),
    ('48', 'Active ConfigGroup:'),
    # EXTENSIONS EXCLUSIONS
    ('100',
     'REGEX=\[TXMLDataRecordProviderTool::TXMLDataRecordProviderTool.Create\] Module not found : "(.*)\\bin\\sqimDossierAdapterDispense\.dll"'),
    ('101', '//Concurrent access'),
    ('102', "REGEX=(\w+)\.Edit\-\>L'enregistrement est d.j. en mode .dition par(.*)"),
    ('103', "Active ConfigGroup: "),
    # MAPGEN LOG EXCLUSIONS
    ('150', 'MsgLevel: 0->None, 1->system + exceptions, 2->squeleton, 3->Detailed, 4-> Max Details 5->Debug'),
    ('151', 'MsgLevel can be overriden by commandLine switch "Maploglevel="'),
    ('152', 'Parameters: (MsgLevel=1, AppendMode=0, StepSave=0)'),
    ('153', 'Auto-Park Delay:'),
    ('154', 'Allow Open Retries:'),
    ('155', 'TMapObject.Create... (Alias='),
    ('156', 'Pooling Enabled:)')
])

DEFAULT_LOG_LEVELS = OrderedDict([
    ('1', LOG_LEVEL_LIST.OPERATING_SYSTEM),
    ('2', LOG_LEVEL_LIST.FATAL),
    ('3', LOG_LEVEL_LIST.EXCEPTION_TRACK),
    ('4', LOG_LEVEL_LIST.LEAK),
    ('10', LOG_LEVEL_LIST.SYST_HIGH),
    ('11', LOG_LEVEL_LIST.SYST_MEDIUM),
    ('12', LOG_LEVEL_LIST.SYST_LOW)
])

DEFAULT_CATEGORIES = OrderedDict([
    # Check for Client Files issues
    ('1.CLIENT FILE', 'REGEX=Exception EFCreateError in module(.*)CLIENTFILE_CONTENT'),
    # Check for PSL issues
    ('10.PSL', 'ExpEval'),
    # Paramerization issues
    ('20.PARAMETRIZATION', 'LoadDocuments\: can not find doctype for '),
    # Event Processor (Automations)
    ('30.EVENT PROCESSOR', 'TEventProcessor.ProcessEvent'),
    # Check for session not terminated normally
    ('40.ABNORMAL TERMINATION', 'SESSION TERMINATED ABNORMALLY (log "END SESSION" not found)'),
    # MAP ERRORS
    ('50.MAPGEN', 'REGEX=Exception(.*)Mapgen\.dll(.*)'),
    # Storage issue
    ('60.STORAGE', 'REGEX=Exception EFCreateError in module(.*)Cannot create file(.*)'),
    ('61.STORAGE', 'REGEX=Exception EAbstractExternalObj in module(.*)Error into external storage extension module : Cannot create file(.*)'),
    # Access violations & Exceptions - excluding those already categorized in previous categories
    ('70.EXCEPTIONS', 'REGEX=Access violation at address ([A-F0-9]{8})(.*)'),
    ('71.EXCEPTIONS', 'Exception'),
    # WINDOWS LOGON
    ('90.WINDOWS LOGON', 'LOGON: Le handle de module n''est pas accessible.'),
    ('91.WINDOWS LOGON', 'REGEX=Can not load(.*)\\WindowsLogonProvider\.dll'),
    # Transactions
    ('100.TRANSACTION', '(Transaction Rollback)')
])

# Default performance trigger in ms: when none it ignores statistics, else it looks at it and keep only what is higher
# than specified
PERFORMANCE_TRIGGER_OFF = None
DEFAULT_PERFORMANCE_TRIGGER_IN_MS = 3500

# DEfault context lengyh (line amount)
DEFAULT_CONTEXT_LENGTH = 20
