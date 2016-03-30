import csv
import logging
import os

import os_path_helper
from constants import Headers

'''
# read a CSV file and load it in a dictonary
def ReadCSVasDict(csv_file):
    try:
        with open(csv_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print row['Row'], row['Name'], row['Country']
    except IOError as (errno, strerror):
            print("I/O error({0}): {1}".format(errno, strerror))
    return
'''


def WriteParsedLoFileToCSV(parsed_file, csv_file_name):
    try:
        if os.path.isabs(csv_file_name):
            csv_file_name = os.path.join(os.path.curdir, csv_file_name)

        mode = 'a' if os.path.exists(csv_file_name) else 'w'
        with open(csv_file_name, mode) as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', extrasaction='ignore', quoting=csv.QUOTE_ALL,
                                    fieldnames=Headers)
            writer.writeheader()

            # dump the file
            file_name = parsed_file.parsed_file_info.fullname
            writer.writerow(parsed_file.as_csv_row)
            # dump the sessions
            for session in parsed_file.sessions:
                row = session.as_csv_row
                row[Headers.file] = file_name
                writer.writerow(row)
                # dump the lines
                for line in session.lines:
                    row = line.as_csv_row
                    row[Headers.file] = file_name
                    row[Headers.message] = row[Headers.message].encode('latin-1')       # because of the french text
                    row[Headers.context] = row[Headers.context].encode('latin-1')       # because of the french text
                    row[Headers.session] = session.session_id
                    writer.writerow(row)

    except Exception:
        logging.exception('')


def WriteLogFolderParserToCSV(log_folder_parser, csv_file_name=None):
    try:
        if csv_file_name is None:
            csv_file_name = os_path_helper.generate_file_name(None)
        elif not os.path.isabs(csv_file_name):
            csv_file_name = os.path.join(os.path.curdir, csv_file_name)

        with open(csv_file_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', extrasaction='ignore', quoting=csv.QUOTE_ALL,
                                    fieldnames=Headers)
            writer.writeheader()

            # dump the file
            for parsed_file in log_folder_parser.parsed_files:
                file_name = parsed_file.parsed_file_info.fullname
                writer.writerow(parsed_file.as_csv_row)
                # dump the sessions
                for session in parsed_file.sessions:
                    row = session.as_csv_row
                    row[Headers.file] = file_name
                    writer.writerow(row)
                    # dump the lines
                    for line in session.lines:
                        row = line.as_csv_row
                        row[Headers.file] = file_name
                        row[Headers.message] = row[Headers.message].encode('latin-1')       # because of the french text
                        row[Headers.context] = row[Headers.context].encode('latin-1')       # because of the french text
                        row[Headers.session] = session.session_id
                        writer.writerow(row)

        return csv_file_name
    except Exception:
        logging.exception('')
