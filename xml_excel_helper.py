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


#
#
#
def clean_up_text_for_excel(text):
    # because of the french text and xml encoding
    return str(text.replace('\n\n', '\n'))


#
#
#
def get_cell_format(column_name):
    if column_name == CellFormat.date or column_name == CellFormat.time:
        return column_name
    else:
        return CellFormat.default


#
#
#
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

    def __add_processing_stats(self):
        stats_worksheet = self.__workbook.add_worksheet('Logs Processing Statistics')
        stats_worksheet.tab_color = "96FF33"
        stats_worksheet.set_column('A:A', 200)
        rowpos= 0
        for stat in self.__log_folder_parser.processing_stats:
            stats_worksheet.write(rowpos, 0, str(stat))
            rowpos += 1

    def __add_session_stats(self):
        stats_worksheet = self.__workbook.add_worksheet('Load Statistics')
        stats_worksheet.tab_color = "1072BA"
        stats_worksheet.set_column('A:A', 70)
        stats_worksheet.set_column('B:C', 20)
        stats_worksheet.set_column('D:F', 15)
        stats_worksheet.write('A1', 'Folder')
        stats_worksheet.write('B1', 'User')
        stats_worksheet.write('C1', 'Application')
        stats_worksheet.write('D1', 'Date')
        stats_worksheet.write('E1', 'Start Time')
        stats_worksheet.write('F1', 'End Time')
        format_date = self.__workbook.add_format({'num_format': 'yyyy-mm-dd'})
        format_time = self.__workbook.add_format({'num_format': 'hh:mm:ss.000;@'})
        rowpos = 1
        for stat in self.__log_folder_parser.session_stats.items.values():
            stats_worksheet.write(rowpos, 0, stat.folder)
            stats_worksheet.write(rowpos, 1, stat.user)
            stats_worksheet.write(rowpos, 2, stat.application)
            stats_worksheet.write(rowpos, 3, stat.date, format_date)
            stats_worksheet.write(rowpos, 4, stat.start_time, format_time)
            stats_worksheet.write(rowpos, 5, stat.end_time, format_time)
            rowpos += 1
        stats_worksheet.autofilter(0, 0, rowpos, 5)

    #
    def __write_dict(self, starting_row, stats_worksheet, title, grid_dict):
        row_pos = starting_row
        total_start_pos = starting_row

        format = self.__style_manager.get_format(RowTypes.file, StyleType.default, '')
        stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 0) + ':' + xl_rowcol_to_cell(row_pos, 4), title, format)

        for category_type, category_value in grid_dict.items():
            row_pos += 1
            format = self.__style_manager.get_format(RowTypes.session, StyleType.default, '')
            stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 1) + ':' + xl_rowcol_to_cell(row_pos, 4), category_type, format)

            section_idx = 0
            for subcategory_type, subcategory_value in category_value.items():
                row_pos += 1
                section_idx += 1
                format = self.__style_manager.get_format(RowTypes.line, StyleType.alt1 if section_idx % 2 == 1 else StyleType.alt2, '')
                stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 2) + ':' + xl_rowcol_to_cell(row_pos, 4), subcategory_type, format)
                total_start_pos = row_pos + 1
                for name, value in subcategory_value.items():
                    row_pos += 1
                    stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), name)
                    stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4), value)

                row_pos += 1
                format = self.__style_manager.get_format(RowTypes.session, StyleType.crashed, '')
                stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), 'Total:', format)
                stats_worksheet.write_formula(xl_rowcol_to_cell(row_pos, 4), '=SUM(E{0}:E{1})'.format(total_start_pos, row_pos), format)

        return row_pos + 1      # +1 for some space

    #
    def __add_machine_user_stats(self):
        stats_worksheet = self.__workbook.add_worksheet('Crossed stats')
        stats_worksheet.tab_color = "FFBF00"
        stats_worksheet.set_column('A:A', 15)
        stats_worksheet.set_column('B:B', 15)
        stats_worksheet.set_column('C:C', 15)
        stats_worksheet.set_column('D:D', 15)
        stats_worksheet.set_column('E:E', 15)
        rowpos = self.__write_dict(0, stats_worksheet, 'Applications', self.__log_folder_parser.machine_user_stats.applications)
        rowpos = self.__write_dict(rowpos, stats_worksheet, 'Users', self.__log_folder_parser.machine_user_stats.users)
        rowpos = self.__write_dict(rowpos, stats_worksheet, 'Machines', self.__log_folder_parser.machine_user_stats.machines)

    def __append_file(self, parsed_file):
        row = parsed_file.as_csv_row
        self.append_row(row, RowTypes.file, StyleType.default)
        self.__row_count += 1

    def __append_session(self, session):
        row = session.as_csv_row
        self.append_row(row, RowTypes.session,
                        StyleType.crashed if row[Headers.has_crashed] else StyleType.default)
        self.__row_count += 1

    def __append_line(self, line_as_csv):
        self.append_row(line_as_csv, RowTypes.line,
                        StyleType.alt1 if line_as_csv[Headers.group] % 2 == 0 else StyleType.alt2)
        self.__row_count += 1

    def __add_log_entries(self):
        try:
            # dump the file
            for parsed_file in self.__log_folder_parser.parsed_files:
                self.__append_file(parsed_file)
                for session in parsed_file.sessions:
                    self.__append_session(session)
                    # dump the lines
                    for line in session.lines:
                        row = line.as_csv_row
                        row[Headers.file] = parsed_file.parsed_file_info.fullname
                        row[Headers.user] = parsed_file.log_infos.user
                        row[Headers.application] = parsed_file.log_infos.application
                        row[Headers.machine] = parsed_file.log_infos.machine
                        row[Headers.message] = clean_up_text_for_excel(row[Headers.message])
                        row[Headers.context] = clean_up_text_for_excel(row[Headers.context])
                        row[Headers.session] = session.session_id
                        self.__append_line(row)
        except:
            logging.exception('Unable to add line to excel file:' + str(row))

    def save(self):
        self.__worksheet.set_column('A:A', 40)
        self.__worksheet.set_column('B:F', 12)
        self.__worksheet.set_column('G:J', 8)
        self.__worksheet.set_column('K:M', 15)
        self.__worksheet.set_column('N:N', 55)
        self.__worksheet.set_column('O:O', 55)

        self.__worksheet.autofilter(0, 0, self.__log_folder_parser.files_and_sessions_and_lines_count , len(Headers) - 1)

        self.__add_log_entries()
        self.__add_session_stats()
        self.__add_machine_user_stats()
        self.__add_processing_stats()

        self.__workbook.close()


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
        LogXlsxWriter(log_folder_parser, xlsx_file_name).save()

        return xlsx_file_name
    except Exception:
        logging.exception('')
