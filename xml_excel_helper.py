import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import logging
import os

import os_path_helper
from constants import Headers, IndexedHeaders, RowTypes
from other_helpers import ListEnum


#
# Enumerates the row type when saving/loading to/from a CSV file
#
CellFormat = ListEnum(['default', Headers.file, Headers.date, Headers.time])
StyleType = ListEnum(['default', 'crashed', 'alt1', 'alt2'])
RowLevels = { RowTypes.file: {'level': 0, 'collapsed': True}, RowTypes.session: {'level': 1}, RowTypes.line: {'level': 2}}


def get_cell_format(column_name):
    if column_name == CellFormat.date or column_name == CellFormat.time:
        return column_name
    else:
        return CellFormat.default


class StyleManager(object):
    def __init__(self, workbook):
        self.__workbook = workbook
        self.__default_style = {'valign': 'top', 'text_wrap': True, 'top': 1, 'border_color': 'FFFFFF'}
        self.__hyperlink_style = {'underline': 1}
        self.__date_format = {'num_format': 'yyyy-mm-dd'}
        self.__time_format = {'num_format': 'hh:mm:ss.000;@'}
        self.__file_style =  {'bold': True, 'bg_color': '0066cc', 'font_color': 'white'}
        self.__session_style = {'italic': True, 'bg_color': '80bfff', 'font_color': 'black'}
        self.__crahsed_style = {'italic': True, 'bg_color': 'ff9900', 'font_color': 'white'}
        self.__alt_color_1 = {'bg_color': 'ffffb3', 'font_color': 'black'}
        self.__alt_color_2 = {'bg_color': 'ffffcc', 'font_color': 'black'}
        self.__styles =  { RowTypes.file:
                            {
                                StyleType.default : {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None, CellFormat.time: None},
                            },
                           RowTypes.session:
                            {
                                StyleType.default: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None, CellFormat.time: None},
                                StyleType.crashed: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None, CellFormat.time: None}
                            },
                           RowTypes.line:
                            {
                                StyleType.alt1: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None, CellFormat.time: None},
                                StyleType.alt2: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None, CellFormat.time: None}
                            }
                        }
        self.__build_style()

    def __build_style(self):
        for rowtype, stylegroup in self.__styles.items():
            for styletype, stylelist in stylegroup.items():
                style = self.__default_style.copy()

                if rowtype == RowTypes.file:
                    style.update(self.__file_style)
                elif rowtype == RowTypes.session:
                    if styletype == StyleType.crashed:
                        style.update(self.__crahsed_style)
                    else:
                        style.update(self.__session_style)
                elif rowtype == RowTypes.line:
                    if styletype == StyleType.alt1:
                        style.update(self.__alt_color_1)
                    else:
                        style.update(self.__alt_color_2)

                for cellformat in stylelist.keys():
                    final_style = style.copy()
                    if cellformat == CellFormat.file:
                        final_style.update(self.__hyperlink_style)
                    elif cellformat == CellFormat.date:
                        final_style.update(self.__date_format)
                    elif cellformat == CellFormat.time:
                        final_style.update(self.__time_format)

                    stylelist[cellformat] = self.__workbook.add_format(final_style)

    def get_format(self, row_type, style_type, column_name):
        cellformat = get_cell_format(column_name)
        return self.__styles[row_type][style_type][cellformat]


#
#
#
class LogXlsxWriter(object):
    def __init__(self, log_folder_parser, filename):
        self.__log_folder_parser = log_folder_parser
        self.__row_count = 0

        self.__workbook = xlsxwriter.Workbook(filename)
        self.__worksheet = self.__workbook.add_worksheet("Log Compilation")
        self.__worksheet.tab_color = "FF3300"
        self.__style_manager = StyleManager(self.__workbook)
        self.__add_header()

    def __cell_coord(self, col_name, rowtype, row = None):
        if row is None:
            row = self.__row_count
        col = IndexedHeaders[col_name]
        cell = xl_rowcol_to_cell( row, col - 1)
        if rowtype == RowTypes.session and col_name == Headers.message:
            cell1 = xl_rowcol_to_cell( row, col)
            cell = cell + ':' + cell1
        return cell

    def __add_header(self):
        header = '&L{0}&Rfrom: {1} to : {2}'.format(self.__log_folder_parser.folder, self.__log_folder_parser.from_date, self.__log_folder_parser.to_date)
        self.__worksheet.set_header(header)

        header_style = self.__workbook.add_format({'bold': True, 'bg_color': '4169FF', 'font_color': 'white', 'align': 'center'})
        for header in Headers:
            self.__worksheet.write(self.__cell_coord(header, None), header.replace('_', ' ').title(), header_style)
        self.__row_count += 1


    def append_row(self, row_as_csv, rowtype, styletype):
        for column_name in Headers:
            cell = self.__cell_coord(column_name, rowtype)

            if column_name in row_as_csv.keys():
                value = row_as_csv[column_name]
                format = self.__style_manager.get_format(rowtype, styletype, column_name)
                if column_name == Headers.file:
                    self.__worksheet.write_url(cell, r'external:' + value, format)
                elif rowtype == RowTypes.session and column_name == Headers.message:
                    self.__worksheet.merge_range(cell, str(value) if type(value) is bytes else value, format)
                else:
                    self.__worksheet.write(cell, str(value) if type(value) is bytes else value, format)
            else:
                self.__worksheet.write(cell, "", format)

        self.__worksheet.set_row(self.__row_count, None, None, RowLevels[rowtype])

    def append_file(self, file_info_as_csv):
        self.append_row(file_info_as_csv, RowTypes.file, StyleType.default)
        self.__row_count += 1

    def append_session(self, session_as_csv):
        self.append_row(session_as_csv, RowTypes.session, StyleType.crashed if session_as_csv[Headers.has_crashed] else StyleType.default)
        self.__row_count += 1

    def append_line(self, line_as_csv):
        self.append_row(line_as_csv, RowTypes.line, StyleType.alt1 if line_as_csv[Headers.group] % 2 == 0 else StyleType.alt2)
        self.__row_count += 1

    def __add_processing_stats(self):
        stats_worksheet = self.__workbook.add_worksheet('Logs Processing Statistics')
        stats_worksheet.tab_color = "96FF33"
        stats_worksheet.set_column('A:A', 200)
        rowpos= 0
        for stat in self.__log_folder_parser.processing_stats:
            stats_worksheet.write(rowpos, 0, str(stat))
            rowpos += 1

    def __add_session_stats(self):
        stats_worksheet = self.__workbook.add_worksheet('Session Statistics')
        stats_worksheet.tab_color = "1072BA"
        stats_worksheet.set_column('A:C', 30)
        stats_worksheet.write('A1', 'Folder')
        stats_worksheet.write('B1', 'User')
        stats_worksheet.write('C1', 'Application')
        stats_worksheet.write('D1', 'Session Count')
        rowpos = 1
        for stat in self.__log_folder_parser.session_stats.items.values():
            stats_worksheet.write(rowpos, 0, str(stat.folder))
            stats_worksheet.write(rowpos, 1, str(stat.user))
            stats_worksheet.write(rowpos, 2, str(stat.application))
            stats_worksheet.write(rowpos, 3, stat.session_count)
            rowpos += 1
        stats_worksheet.autofilter(0, 0, rowpos, 3)

    def close(self):
        self.__worksheet.set_column('A:A', 40)
        self.__worksheet.set_column('B:C', 12)
        self.__worksheet.set_column('D:G', 8)
        self.__worksheet.set_column('H:J', 15)
        self.__worksheet.set_column('K:K', 60)
        self.__worksheet.set_column('L:L', 80)

        self.__worksheet.autofilter(0, 0, self.__log_folder_parser.files_and_sessions_and_lines_count , len(Headers) - 1)

        self.__add_session_stats()
        self.__add_processing_stats()

        self.__workbook.close()


#
#
#
def __clean_up_text_for_excel(text):
    # because of the french text and xml encoding
    return str(text.replace('\n\n', '\n'))


#
#
#
def GetOutputXlsxFileName(xlsx_file_name=None):
    if xlsx_file_name is None:
        xlsx_file_name = os_path_helper.generate_file_name('Log Compilation - ', '.xlsx')
    elif not os.path.isabs(xlsx_file_name):
        xlsx_file_name = os.path.join(os.path.curdir, xlsx_file_name)
    if not xlsx_file_name.endswith('.xlsx'):
        xlsx_file_name = xlsx_file_name + '.xlsx'
    return xlsx_file_name


def WriteLogFolderParserToXSLX(log_folder_parser, xlsx_file_name=None):
    try:
        xlsx_file_name = GetOutputXlsxFileName(xlsx_file_name)

        # Create a workbook and add a worksheet.
        writer = LogXlsxWriter(log_folder_parser, xlsx_file_name)
        try:
            # dump the file
            for parsed_file in log_folder_parser.parsed_files:
                file_name = parsed_file.parsed_file_info.fullname
                writer.append_file(parsed_file.as_csv_row)
                for session in parsed_file.sessions:
                    row = session.as_csv_row
                    row[Headers.file] = file_name
                    writer.append_session(row)
                    # dump the lines
                    for line in session.lines:
                        row = line.as_csv_row
                        row[Headers.file] = file_name
                        row[Headers.message] = __clean_up_text_for_excel(row[Headers.message])
                        row[Headers.context] = __clean_up_text_for_excel(row[Headers.context])
                        row[Headers.session] = session.session_id
                        writer.append_line(row)
        finally:
            writer.close()

        return xlsx_file_name
    except Exception:
        logging.exception('')
