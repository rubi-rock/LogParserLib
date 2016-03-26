import logging
import datetime
import log_parser
from constants import ParamNames
from other_helpers import LogUtility    # keep it even if it seems unused, it set up the logging automatically

'''
def filter_function(lfi):
    return "Purkinje" in lfi.filename
'''


class FilterClass(object):
    beginDate = datetime.datetime(year=2016, month=2, day=9)
    endDate = datetime.datetime(year=2016, month=4, day=9)

    @staticmethod
    def filter_method(lfi):
        return "Purkinje" in lfi.file_name

    @staticmethod
    def filter_static_method(lfi):
        return "Purkinje" in lfi.file_name

    def filter_on_date(self, lfi):
        return lfi.date >= self.beginDate


if __name__ == '__main__':
    logging.info("Start")

    '''
    print( LogLineParserFactory.get_parser_list())
    parser = LogLineParserFactory.get_parser('mapgen')
    parser = LogLineParserFactory.get_parser('')
    parser = LogLineParserFactory.get_parser('bean')
    exit(0)
    '''

    '''
    lfl = FileUtilities.FileSeeker.walk_and_filter_in("/Users/ChristianRocher/Downloads/log", "*.log", filter_function)
    print(len(lfl))

    lfl = FileUtilities.FileSeeker.walk_and_filter_in("/Users/ChristianRocher/Downloads/log", "*.log", FilterClass.filter_static_method)
    print(len(lfl))

    fc = FilterClass()
    lfl = FileUtilities.FileSeeker.walk_and_filter_in("/Users/ChristianRocher/Downloads/log", "*.log", fc.filter_method)
    print(len(lfl))

    fc = FilterClass()
    lfl = FileUtilities.FileSeeker.walk_and_filter_in("/Users/ChristianRocher/Downloads/log", "*.log", fc.filter_on_date)
    print(len(lfl))

    flp = LogParser.FolderLogParser()
    flp.parse("/Users/ChristianRocher/Downloads/log", datetime.datetime(year=2015, month=2, day=9), datetime.datetime(year=2016, month=2, day=9))
    print(len(flp.log_file_list))
    flp.parse("/Users/ChristianRocher/Downloads/log", datetime.datetime(year=2016, month=3, day=10), datetime.datetime(year=2016, month=3, day=10))
    print(len(flp.log_file_list))

    res = RegExpSet()
    res.add("", "")
    res.add("", "no expr")
    res.add("1234567890", "")
    res.add("abcdefghij", "COMPLETE")
    print(res)
    print(res.combined_expressions)

    rel = {"": "abc", "": "123", "passe-passe": "QWERTY", "Coyote": "%$#$%"}
    resi = RegExpSet(rel)
    print(resi)
    '''
    exclusions = {
        '1': 'BEGIN SESSION',
        '2': 'END SESSION',
        # DOSSIER LOG EXCLUSIONS
        '10': 'OPERATING_SYSTEM=0,FATAL=1,EXCEPTION_TRACK=2',
        '11': 'Available levels : LOG=0,OPERATING_SYSTEM=1,FATAL=2',
        '12': '----> Current Level:',
        '15': 'DebugTools created by',
        '16': 'DebugTools destroyed by',
        '17': 'plugged to DebugTools',
        '20': 'User logged :',
        '21': 'Client Session Protocol:',
        '22': 'Client Session State:',
        '23': 'CurrentConfig:',
        '25': 'Cache - Limit:',
        '26': '================== CACHES STATISTICS =====================',
        '30': 'REGEX=Can not find module (.*)\\Bin\\PurkScanContentProvider\.dll',
        '31': 'Can not find module Cmdlinetool.dll',
        '32': "SCANSETUP: Le handle de module n'est pas accessible",
        '33': 'Record class was not registered in the DataRecordFactory',
        '40': 'REGEX=Version[ ]*: [0-9\.]{12}',
        '41': 'Interface: ',
        '42': 'MaxBlobSize:',
        '43': 'Server Name:',
        '44': 'Database:',
        '45': 'program: ',
        '46': 'REGEX=^Config\:',
        '47': '* Context * ',
        '48': 'Active ConfigGroup:',
        # EXTENSIONS EXCLUSIONS
        '100': 'REGEX=\[TXMLDataRecordProviderTool::TXMLDataRecordProviderTool.Create\] Module not found : "(.*)\\bin\\sqimDossierAdapterDispense\.dll"',
        '101': '//Concurrent access',
        '102': "REGEX=(\w+)\.Edit\-\>L'enregistrement est d.j. en mode .dition par(.*)",
        '103': "Active ConfigGroup: ",
        # MAPGEN LOG EXCLUSIONS
        '150': 'MsgLevel: 0->None, 1->system + exceptions, 2->squeleton, 3->Detailed, 4-> Max Details 5->Debug',
        '151': 'MsgLevel can be overriden by commandLine switch "Maploglevel="',
        '152': 'Parameters: (MsgLevel=1, AppendMode=0, StepSave=0)',
        '153': 'Auto-Park Delay:',
        '154': 'Allow Open Retries:',
        '155': 'TMapObject.Create... (Alias=',
        '156': 'Pooling Enabled:'
        }

    session_info = {
        'Version': 'Version :',
        'Protocol': 'Client Session Protocol',
        'User': 'User logged :',
        'Config': 'CurrentConfig',
        'ConfigGroup': 'Active ConfigGroup:',
        }

    log_levels = {
        '1': 'OPERATING_SYSTEM',
        '2': 'FATAL',
        '3': 'EXCEPTION_TRACK',
        '4': 'LEAK',
        #'5': 'STATISTIC',
        '10': 'SYST HIGH',
        '11': 'SYST MEDIUM',
        '12': 'SYST LOW'
        }

    categories = {
        # Check for Client Files issues
        '1.CLIENT FILE': 'REGEX=Exception EFCreateError in module(.*)CLIENTFILE_CONTENT',
        # Check for PSL issues
        '10.PSL': 'ExpEval',
        # Paramerization issues
        '20.PARAMETRIZATION': 'LoadDocuments\: can not find doctype for ',
        # Event Processor (Automations)
        '30.EVENT PROCESSOR': 'TEventProcessor.ProcessEvent',
        # Check for session not terminated normally
        '40.ABNORMAL TERMINATION': 'SESSION TERMINATED ABNORMALLY (log "END SESSION" not found)',
        # MAP ERRORS
        '50.MAPGEN': 'REGEX=Exception(.*)Mapgen\.dll(.*)',
        # Storage issue
        '60.STORAGE': 'REGEX=Exception EFCreateError in module(.*)Cannot create file(.*)',
        '61.STORAGE': 'REGEX=Exception EAbstractExternalObj in module(.*)Error into external storage extension module : Cannot create file(.*)',
        # Access violations & Exceptions - excluding those already categorized in previous categories
        '70.EXCEPTIONS': 'REGEX=Access violation at address ([A-F0-9]{8})(.*)',
        '71.EXCEPTIONS': 'Exception',
        # WINDOWS LOGON
        '90.WINDOWS LOGON': 'LOGON: Le handle de module n''est pas accessible.',
        '91.WINDOWS LOGON': 'REGEX=Can not load(.*)\\WindowsLogonProvider\.dll',
        # Transactions
        '100.TRANSACTION': '(Transaction Rollback)'
        }


    params = {ParamNames.exclusions: exclusions, ParamNames.categories: categories, ParamNames.session_info: session_info}
    flp = log_parser.FolderLogParser(**params)

    flp.parse("/Users/ChristianRocher/Downloads/ACTUEL_TS_LOGS", log_levels, datetime.datetime(year=2016, month=1, day=1), datetime.datetime(year=2016, month=3, day=31))
    #flp.parse("/Users/ChristianRocher/Downloads/log", log_levels, datetime.datetime(year=2016, month=3, day=10), datetime.datetime(year=2016, month=3, day=10))
    #flp.parse("/Users/ChristianRocher/Downloads/log/AJHeafey", log_levels, datetime.datetime(year=2016, month=3, day=10), datetime.datetime(year=2016, month=3, day=10))
    #flp.parse("/Users/ChristianRocher/Downloads/log/afisher", log_levels, datetime.datetime(year=2016, month=1, day=10), datetime.datetime(year=2016, month=3, day=10))
    #flp.parse("/Users/ChristianRocher/Downloads/log/LBlundell", log_levels, datetime.datetime(year=2016, month=3, day=1), datetime.datetime(year=2016, month=3, day=31))
    flp.save_to_csv_file()
