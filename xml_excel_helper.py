from math import trunc

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
StyleType = ListEnum(['default', 'crashed', 'alt1', 'alt2', 'percent_alt1', 'percent_alt2', 'url_alt1', 'url_alt2', 'url_crashed'])
RowLevels = {RowTypes.error: {'level': 0}, RowTypes.file: {'level': 1, 'collapsed': True},
             RowTypes.session: {'level': 2}, RowTypes.line: {'level': 3}}
WarningLevel = ListEnum(['low', 'medium', 'high'])


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
        self.__error_style = {'valign': 'top', 'text_wrap': True, 'top': 1, 'border_color': 'orange',
                              'font_color': 'white'}
        self.__error_style = {'valign': 'top', 'text_wrap': True, 'top': 1, 'border_color': 'red',
                              'font_color': 'white'}
        self.__hyperlink_style = {'underline': 1}
        self.__date_format = {'num_format': 'yyyy-mm-dd'}
        self.__time_format = {'num_format': 'hh:mm:ss.000;@'}
        self.__file_style = {'bold': True, 'bg_color': '0066cc', 'font_color': 'white'}
        self.__session_style = {'italic': True, 'bg_color': '80bfff', 'font_color': 'black'}
        self.__crahsed_style = {'italic': True, 'bg_color': 'ff9900', 'font_color': 'white'}
        self.__url_crahsed_style = {'italic': True, 'bg_color': 'ff9900', 'font_color': 'blue', 'underline': 1}
        self.__alt_color_1 = {'bg_color': 'ffffb3', 'font_color': 'black'}
        self.__alt_color_2 = {'bg_color': 'ffffcc', 'font_color': 'black'}
        self.__percent_alt_color_1 = {'num_format': '0%', 'bg_color': 'ffffb3', 'font_color': 'black'}
        self.__percent_alt_color_2 = {'num_format': '0%', 'bg_color': 'ffffcc', 'font_color': 'black'}
        self.__url_alt_color_1 = {'bg_color': 'ffffb3', 'font_color': 'blue', 'underline': 1}
        self.__url_alt_color_2 = {'bg_color': 'ffffcc', 'font_color': 'blue', 'underline': 1}

        self.__styles = {}
        self.__prepare_styles()

        self.__warning_styles = {}
        self.__prepare_warning_styles()

    def __prepare_styles(self):
        self.__styles = {RowTypes.error:
            {
                StyleType.default: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                    CellFormat.time: None},
            },
            RowTypes.file:
                {
                    StyleType.default: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                        CellFormat.time: None},
                },
            RowTypes.session:
                {
                    StyleType.default: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                        CellFormat.time: None},
                    StyleType.crashed: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                        CellFormat.time: None},
                    StyleType.url_crashed: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                            CellFormat.time: None}
                },
            RowTypes.line:
                {
                    StyleType.alt1: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                     CellFormat.time: None},
                    StyleType.alt2: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                     CellFormat.time: None},
                    StyleType.percent_alt1: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                         CellFormat.time: None},
                    StyleType.percent_alt2: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                         CellFormat.time: None},
                    StyleType.url_alt1: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                         CellFormat.time: None},
                    StyleType.url_alt2: {CellFormat.default: None, CellFormat.file: None, CellFormat.date: None,
                                         CellFormat.time: None}
                }
        }

        self.__build_style()

    #
    def __build_style(self):
        for rowtype, stylegroup in self.__styles.items():
            for styletype, stylelist in stylegroup.items():
                style = self.__default_style.copy()

                if rowtype == RowTypes.error:
                    style.update(self.__error_style)
                if rowtype == RowTypes.file:
                    style.update(self.__file_style)
                elif rowtype == RowTypes.session:
                    if styletype == StyleType.crashed:
                        style.update(self.__crahsed_style)
                    elif styletype == StyleType.url_crashed:
                        style.update(self.__crahsed_style)
                    else:
                        style.update(self.__session_style)
                elif rowtype == RowTypes.line:
                    if styletype == StyleType.alt1:
                        style.update(self.__alt_color_1)
                    elif styletype == StyleType.alt2:
                        style.update(self.__alt_color_2)
                    elif styletype == StyleType.percent_alt1:
                        style.update(self.__percent_alt_color_1)
                    elif styletype == StyleType.percent_alt2:
                        style.update(self.__percent_alt_color_2)
                    elif styletype == StyleType.url_alt1:
                        style.update(self.__url_alt_color_1)
                    else:
                        style.update(self.__url_alt_color_2)

                for cellformat in stylelist.keys():
                    final_style = style.copy()
                    if cellformat == CellFormat.file:
                        final_style.update(self.__hyperlink_style)
                    elif cellformat == CellFormat.date:
                        final_style.update(self.__date_format)
                    elif cellformat == CellFormat.time:
                        final_style.update(self.__time_format)

                    stylelist[cellformat] = self.__workbook.add_format(final_style)

    #
    def __prepare_warning_styles(self):
        self.__warning_styles = {WarningLevel.low: self.__workbook.add_format(
            {'valign': 'top', 'text_wrap': True, 'bold': True, 'font_color': 'FAAC58'}),
                                 WarningLevel.medium: self.__workbook.add_format(
                                     {'valign': 'top', 'text_wrap': True, 'bold': True, 'font_color': 'FF8000'}),
                                 WarningLevel.high: self.__workbook.add_format(
                                     {'valign': 'top', 'text_wrap': True, 'bold': True, 'font_color': 'DF0101'})}

    #
    def get_format(self, row_type, style_type, column_name):
        cellformat = get_cell_format(column_name)
        return self.__styles[row_type][style_type][cellformat]

    def get_warning_format(self, level):
        return self.__warning_styles[level]


#
#
#
class LogXlsxWriter(object):
    def __init__(self, log_folder_parser, filename):
        self.__log_folder_parser = log_folder_parser
        self.__row_count = 0
        self.__workbook = xlsxwriter.Workbook(filename)
        self.__style_manager = StyleManager(self.__workbook)
        self.__url_added_to_excel = 0
        self.__url_count = 0

    def __create_worksheet(self, name, color):
        worksheet = self.__workbook.add_worksheet(name)
        worksheet.tab_color = color
        worksheet.set_paper(17)
        worksheet.fit_to_pages(1, 0)
        worksheet.set_landscape()
        worksheet.set_margins(0.5, 0.5, 0.5, 0.5)
        return worksheet

    def __cell_coord(self, col_name, rowtype, row=None):
        if row is None:
            row = self.__row_count
        col = IndexedHeaders[col_name]
        cell = xl_rowcol_to_cell(row, col - 1)
        if rowtype == RowTypes.session and col_name == Headers.message:
            cell1 = xl_rowcol_to_cell(row, col)
            cell = cell + ':' + cell1
        return cell

    def __add_header(self, worksheet):
        header = '&L{0}&Rfrom: {1} to : {2}'.format(self.__log_folder_parser.folder, self.__log_folder_parser.from_date,
                                                    self.__log_folder_parser.to_date)
        worksheet.set_header(header)

        if self.__log_folder_parser.files_and_sessions_and_lines_count < 16384:
            worksheet.autofilter(3, 0, self.__log_folder_parser.files_and_sessions_and_lines_count, len(Headers) - 1)
        self.__row_count = 3

        header_style = self.__workbook.add_format(
            {'bold': True, 'bg_color': '4169FF', 'font_color': 'white', 'align': 'center'})
        for header in Headers:
            worksheet.write(self.__cell_coord(header, None), header.replace('_', ' ').title(), header_style)
        self.__row_count += 1

    def __append_row(self, worksheet, row_as_csv, rowtype, styletype):
        for column_name in Headers:
            cell = self.__cell_coord(column_name, rowtype)

            format = self.__style_manager.get_format(rowtype, styletype, column_name)
            if column_name in row_as_csv.keys():
                value = row_as_csv[column_name]
                if column_name == Headers.file:
                    # use only 16384 links on files and sessions because excel supports only 64k urls and we need a
                    # bunch for the similarities
                    if rowtype == RowTypes.line and self.__log_folder_parser.files_and_sessions_and_lines_count > 16384:
                        worksheet.write(cell, value, format)
                    else:
                        worksheet.write_url(cell, r'external:' + value, format)
                elif rowtype == RowTypes.session and column_name == Headers.message:
                    worksheet.merge_range(cell, str(value) if type(value) is bytes else value, format)
                else:
                    worksheet.write(cell, str(value) if type(value) is bytes else value, format)
            else:
                worksheet.write(cell, "", format)

        cell = self.__cell_coord(Headers.message, rowtype)
        worksheet.set_row(self.__row_count, None, None, RowLevels[rowtype])
        return cell

    def __add_processing_stats(self):
        stats_worksheet = self.__create_worksheet('Logs Processing Statistics', "96FF33")
        stats_worksheet.set_column('A:A', 200)
        rowpos = 0
        for stat in self.__log_folder_parser.processing_stats:
            stats_worksheet.write(rowpos, 0, str(stat))
            rowpos += 1

    def __add_session_stats(self):
        stats_worksheet = self.__create_worksheet('Load Statistics', "1072BA")
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
        if rowpos < 16384:
            stats_worksheet.autofilter(0, 0, rowpos, 5)

    #
    def __write_dict(self, starting_row, stats_worksheet, title, grid_dict):
        row_pos = starting_row
        total_start_pos = starting_row

        format = self.__style_manager.get_format(RowTypes.file, StyleType.default, '')
        stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 0) + ':' + xl_rowcol_to_cell(row_pos, 5), title, format)

        for category_type, category_value in grid_dict.items():
            row_pos += 1
            format = self.__style_manager.get_format(RowTypes.session, StyleType.default, '')
            stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 1) + ':' + xl_rowcol_to_cell(row_pos, 5),
                                        category_type, format)

            section_idx = 0
            for subcategory_type, subcategory_value in category_value.items():
                row_pos += 1
                section_idx += 1
                value_is_multiple_columns = False
                format = self.__style_manager.get_format(RowTypes.line,
                                                         StyleType.alt1 if section_idx % 2 == 1 else StyleType.alt2, '')

                for name, value in subcategory_value.items():
                    if type(value) is dict:
                        value_is_multiple_columns = True
                    break

                if value_is_multiple_columns:
                    i = 0
                    stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 2) + ':' + xl_rowcol_to_cell(row_pos, 3),
                                                subcategory_type, format)
                    for x in value.keys():
                        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4 + i), x.replace('_', ' '), format)
                        i += 1
                else:
                    stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 2) + ':' + xl_rowcol_to_cell(row_pos, 5),
                                                subcategory_type, format)

                total_start_pos = row_pos + 1
                for name, value in subcategory_value.items():
                    row_pos += 1
                    stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), name)
                    if type(value) is dict:
                        i = 0
                        for x in value.values():
                            warning_format = self.__style_manager.get_warning_format(WarningLevel.high) if x > 15 \
                                else self.__style_manager.get_warning_format(WarningLevel.medium) if x > 10 \
                                else self.__style_manager.get_warning_format(WarningLevel.low) if x > 5 else None
                            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4 + i), x, warning_format)
                            i += 1
                    else:
                        warning_format = self.__style_manager.get_warning_format(WarningLevel.high) if value > 15 \
                            else self.__style_manager.get_warning_format(WarningLevel.medium) if value > 10 \
                            else self.__style_manager.get_warning_format(WarningLevel.low) if value > 5 else None
                        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4), value, warning_format)

                row_pos += 1
                stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), 'Total:', format)
                stats_worksheet.write_formula(xl_rowcol_to_cell(row_pos, 4),
                                              '=SUM(E{0}:E{1})'.format(total_start_pos, row_pos), format)
                if value_is_multiple_columns:
                    stats_worksheet.write_formula(xl_rowcol_to_cell(row_pos, 5),
                                                  '=SUM(F{0}:F{1})'.format(total_start_pos, row_pos), format)
                else:
                    stats_worksheet.write(xl_rowcol_to_cell(row_pos, 5), '', format)

        return row_pos + 1  # +1 for some space

    #
    def __write_similarities_header(self, stats_worksheet):
        format = self.__style_manager.get_format(RowTypes.file, StyleType.default, '')
        stats_worksheet.set_column('A:A', 10)
        stats_worksheet.write('A1', 'Count', format)
        stats_worksheet.set_column('B:B', 15)
        stats_worksheet.write('B1', 'Message', format)
        stats_worksheet.set_column('C:C', 10)
        stats_worksheet.write('C1', 'Ratio (%)', format)
        stats_worksheet.set_column('D:D', 130)
        stats_worksheet.write('D1', 'Matched Message (identical, similar, maybe in cascade)', format)
        stats_worksheet.set_column('E:E', 30)
        stats_worksheet.write('E1', 'Reference', format)

    #
    def __write_similiarities_block_master(self, stats_worksheet, similarity, row_pos):
        format = self.__style_manager.get_format(RowTypes.session, StyleType.crashed, '')
        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 0), len(similarity.matches), format)
        stats_worksheet.merge_range(xl_rowcol_to_cell(row_pos, 1) + ':' + xl_rowcol_to_cell(row_pos, 3),
                                    similarity.message, format)
        stats_worksheet.set_row(row_pos, 30)
        format = self.__style_manager.get_format(RowTypes.session, StyleType.url_crashed, '')
        stats_worksheet.write_formula(xl_rowcol_to_cell(row_pos, 4),
                                      '=HYPERLINK("#\'Log Compilation\'!{0}","Click to go to original extracted line")'.format(
                                          similarity.log_line.excel_cell), format)
        self.__url_count += 1
        self.__url_added_to_excel += 1
        row_pos += 1
        return row_pos

    #
    def __write_similiarities_block_detailled(self, stats_worksheet, similarity, row_pos):
        count = 0
        for match in similarity.matches:
            format = self.__style_manager.get_format(RowTypes.line,
                                                     StyleType.alt1 if match.ratio == 100 else StyleType.alt2,
                                                     Headers.date)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 0), match.log_line.date, format)
            format = self.__style_manager.get_format(RowTypes.line,
                                                     StyleType.alt1 if match.ratio == 100 else StyleType.alt2,
                                                     Headers.time)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 1), match.log_line.time, format)
            format = self.__style_manager.get_format(RowTypes.line,
                                                     StyleType.percent_alt1 if match.ratio == 100 else StyleType.percent_alt2, '')
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 2), match.ratio / 100, format)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), match.message, format)
            format = self.__style_manager.get_format(RowTypes.line,
                                                     StyleType.url_alt1 if match.ratio == 100 else StyleType.url_alt2,
                                                     '')
            if self.__url_count <= 16384 and (similarity.limit is None or count < similarity.limit):
                stats_worksheet.write_formula(xl_rowcol_to_cell(row_pos, 4),
                                              '=HYPERLINK("#\'Log Compilation\'!{0}","Click to go to original extracted line")'.format(
                                                  match.log_line.excel_cell), format)
                self.__url_added_to_excel += 1
            else:
                stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4),
                                      'Log Compilation Tab, Cell : {0}'.format(match.log_line.excel_cell), format)
            self.__url_count += 1
            count += 1
            row_pos += 1
        return row_pos

    #
    def __set_similiarities_limit(self):
        # excel can have until 65536 hyperlinks, still the file is not anymore manageable (cannot change a column size
        # or even cannot save successfully). Therefore we must limit to a certain number of items to log in excel.
        if self.__log_folder_parser.log_similiatities.similarities_count > 16384:
            max_capacity = trunc(16384 / self.__log_folder_parser.log_similiatities.block_count)
            logging.info("URL limit fixed to: {0}".format(max_capacity))
            for similiarity in self.__log_folder_parser.log_similiatities.similarities:
                setattr(similiarity, 'limit', min(max_capacity, similiarity.count))
        else:
            for similiarity in self.__log_folder_parser.log_similiatities.similarities:
                setattr(similiarity, 'limit', None)

    def __add_similarities_compilation(self, stats_worksheet, row_pos):
        format = self.__style_manager.get_format(RowTypes.session, StyleType.crashed, '')
        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 0), 'Matches', format)
        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 1), 'Similar', format)
        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 2), 'Total', format)
        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), 'Message', format)
        stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4), 'Link', format)
        row_pos += 1

        count = 0
        for similarity in self.__log_folder_parser.log_similiatities.similarities:
            match_count = 1
            similarity_count = 0
            for match in similarity.matches:
                if match.ratio == 100:
                    match_count += 1
                else:
                    similarity_count += 1

            format = self.__style_manager.get_format(RowTypes.line,
                                                     StyleType.alt1 if count % 2 == 0 else StyleType.alt2,
                                                     '')
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 0), match_count, format)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 1), similarity_count, format)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 2), match_count + similarity_count, format)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 3), match.message, format)
            stats_worksheet.write(xl_rowcol_to_cell(row_pos, 4), '', format)
            count += 1
            row_pos += 1

        row_pos += 3
        return row_pos

    def __update_similarity_compilation_with_links(self, stats_worksheet):
        row_pos = 4
        count = 0
        for similarity in self.__log_folder_parser.log_similiatities.similarities:
            format = self.__style_manager.get_format(RowTypes.line,
                                                     StyleType.url_alt1 if count % 2 == 0 else StyleType.url_alt2,
                                                     '')
            stats_worksheet.write_formula(xl_rowcol_to_cell(row_pos, 4),
                                          '=HYPERLINK("#\'Log Similarities\'!B{0}","Details")'.format(
                                              similarity.row_pos), format)
            row_pos += 1
            count += 1

    #
    def __add_similarities(self):
        if self.__log_folder_parser.log_similiatities is None:
            return
        stats_worksheet = self.__create_worksheet('Log Similarities', "FF9900")
        self.__write_similarities_header(stats_worksheet)

        format = self.__style_manager.get_format(RowTypes.session, StyleType.crashed, '')
        stats_worksheet.merge_range("A1:E1",
                                    "Log extracted from: {0} to: {1}".format(self.__log_folder_parser.from_date,
                                                                             self.__log_folder_parser.to_date),
                                    format)
        # excel can have until 65536 hyperlinks, still even with less, when there are too much link then the file is not
        # anymore manageable (cannot change a column size or save successfully). Therefore we must limit to a certain
        # number of items to log in excel.
        self.__set_similiarities_limit()

        row_pos = 3
        row_pos = self.__add_similarities_compilation(stats_worksheet, row_pos)

        last_row = self.__log_folder_parser.log_similiatities.similarities_count
        if last_row < 16384:
            stats_worksheet.autofilter(row_pos, 0, row_pos + last_row, 4)

        for similarity in self.__log_folder_parser.log_similiatities.similarities:
            row_pos = self.__write_similiarities_block_master(stats_worksheet, similarity, row_pos)
            setattr(similarity, 'row_pos', row_pos)
            row_pos = self.__write_similiarities_block_detailled(stats_worksheet, similarity, row_pos)

        self.__update_similarity_compilation_with_links(stats_worksheet)
    #
    def __add_machine_user_stats(self):
        stats_worksheet = self.__create_worksheet('Crossed stats', "FFFF00")
        stats_worksheet.set_column('A:A', 15)
        stats_worksheet.set_column('B:B', 15)
        stats_worksheet.set_column('C:C', 15)
        stats_worksheet.set_column('D:D', 15)
        stats_worksheet.set_column('E:E', 25)
        stats_worksheet.set_column('F:F', 25)

        format = self.__style_manager.get_format(RowTypes.session, StyleType.crashed, '')
        stats_worksheet.merge_range("A1:F1", "Log extracted from: {0} to: {1}".format(self.__log_folder_parser.from_date,
                                                                                self.__log_folder_parser.to_date),
                              format)

        rowpos = self.__write_dict(2, stats_worksheet, 'Applications',
                                   self.__log_folder_parser.machine_user_stats.applications)
        rowpos = self.__write_dict(rowpos, stats_worksheet, 'Users', self.__log_folder_parser.machine_user_stats.users)
        rowpos = self.__write_dict(rowpos, stats_worksheet, 'Machines',
                                   self.__log_folder_parser.machine_user_stats.machines)

    def __append_file(self, worksheet, parsed_file):
        row = parsed_file.as_csv_row
        self.__append_row(worksheet, row, RowTypes.file, StyleType.default)
        self.__row_count += 1

    def __append_session(self, worksheet, session):
        row = session.as_csv_row
        self.__append_row(worksheet, row, RowTypes.session,
                          StyleType.crashed if row[Headers.has_crashed] else StyleType.default)
        self.__row_count += 1

    def __append_line(self, worksheet, line_as_csv):
        cell = self.__append_row(worksheet, line_as_csv, RowTypes.line,
                                 StyleType.alt1 if line_as_csv[Headers.group] % 2 == 0 else StyleType.alt2)
        self.__row_count += 1
        return cell

    def __add_log_entries(self, worksheet):
        row = {}
        try:
            # dump the file
            for parsed_file in self.__log_folder_parser.parsed_files:
                self.__append_file(worksheet, parsed_file)
                for session in parsed_file.sessions:
                    self.__append_session(worksheet, session)
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
                        cell = self.__append_line(worksheet, row)
                        setattr(line, 'excel_cell', cell)

        except:
            logging.exception('Unable to add line to excel file:' + str(row))

    def __add_log_compilation(self):
        worksheet = self.__create_worksheet("Log Compilation", "FF3300")
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:F', 12)
        worksheet.set_column('G:J', 8)
        worksheet.set_column('K:N', 15)
        worksheet.set_column('O:O', 60)
        worksheet.set_column('P:P', 300)

        format = self.__style_manager.get_format(RowTypes.session, StyleType.crashed, '')
        worksheet.merge_range("A1:P1", "Log extracted from: {0} to: {1}".format(self.__log_folder_parser.from_date,
                                                                                self.__log_folder_parser.to_date),
                              format)

        self.__add_header(worksheet)
        self.__add_log_entries(worksheet)

    def save(self):
        self.__add_log_compilation()
        self.__add_similarities()
        self.__add_machine_user_stats()
        self.__add_session_stats()
        self.__add_processing_stats()

        self.__workbook.close()
        logging.info("{0}/{1} URLs added to the excel file.".format(self.__url_added_to_excel, self.__url_count))


#
#
#
def GetOutputXlsxFileName(source_path, xlsx_file_name=None):
    if xlsx_file_name is None:
        xlsx_file_name = os_path_helper.generate_file_name('Log Compilation - ', '.xlsx',
                                                           source_path if source_path is not None else None)
    elif not os.path.isabs(xlsx_file_name):
        xlsx_file_name = os.path.join(source_path if source_path is not None else os.path.curdir, xlsx_file_name)

    if not xlsx_file_name.endswith('.xlsx'):
        xlsx_file_name = xlsx_file_name + '.xlsx'

    return xlsx_file_name


def WriteLogFolderParserToXSLX(log_folder_parser, xlsx_file_name=None):
    try:
        # xlsx_file_name = GetOutputXlsxFileName(xlsx_file_name)

        # Create a workbook and add a worksheet.
        LogXlsxWriter(log_folder_parser, xlsx_file_name).save()

        return xlsx_file_name
    except Exception:
        logging.exception('')
