import csv
import logging
import os
from datetime import datetime
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

def WriteDictToCSV(log_folder_parser, csv_file_name = None):
    try:
        if csv_file_name is None:
            csv_file_name = os.path.join(os.path.curdir, 'log-file-parsed - %s.csv' % datetime.now().strftime('%Y%m%d-%H%M%S'))
        elif not os.path.isabs(csv_file_name):
            csv_file_name = os.path.join(os.path.curdir, csv_file_name)

        headers = log_folder_parser.csv_header
        with open(csv_file_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=log_folder_parser.csv_header)
            writer.writeheader()

            for parsed_file in log_folder_parser.parsed_files:
                writer.writerow(parsed_file.as_csv_row)
                file_name = parsed_file.parsed_file_info.fullname
                for session in parsed_file.sessions:
                    row = session.as_csv_row
                    row[Headers.file] = file_name
                    writer.writerow(row)

        return csv_file_name
    except Exception:
        logging.exception('')
    return

'''

            for values in d
            writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
    writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
    writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)

'''