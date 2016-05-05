import click
from datetime import datetime, timedelta

import LogParserGUI
import log_parser_engine


@click.command()
@click.option('--path', default=None, type=click.Path(exists=True), help='Path containing the log files to parse')
@click.option('--fromdate', default=str(datetime.now().date() - timedelta(days=7)),
              help='Log entries before that date will be ignored. Format: yyyy-mm-dd')
@click.option('--todate', default=str(datetime.now().date() + timedelta(days=1)),
              help='Log entries after that date will be ignored. Format: yyyy-mm-dd')
@click.option('--output', default=None,
              help='Indicates the output file name (with or without extention - by default it''s xlsx). If no this option is not specified then a file name is generated. If the path is relative, the file is saved in the same folder than this tool')
@click.option('--splitfilename/--no-splitfilename', is_flag=True, default=True, help='Try to split the file path and name to extract the user name and the machine (TS).')
@click.option('--autoopen/--no-autoopen', is_flag=True, default=True, help='Open the resulting excel file. Auto-open is true by default.')
def show_it(path=None, fromdate=None, todate=None, output=None, splitfilename=True, autoopen=True):
    mainwindow = LogParserGUI.LogParserMainWindows(path, fromdate, todate, output, splitfilename, autoopen)
    mainwindow.ShowMainWindow()


@click.command()
@click.option('--path', default=None, type=click.Path(exists=True), help='Path containing the log files to parse')
@click.option('--fromdate', default=str(datetime.now().date() - timedelta(days=7)),
              help='Log entries before that date will be ignored. Format: yyyy-mm-dd')
@click.option('--todate', default=str(datetime.now().date() + timedelta(days=1)),
              help='Log entries after that date will be ignored. Format: yyyy-mm-dd')
@click.option('--output', default=None,
              help='Indicates the output file name (with or without extention - by default it''s xlsx). If no this option is not specified then a file name is generated. If the path is relative, the file is saved in the same folder than this tool')
@click.option('--splitfilename/--no-splitfilename', is_flag=True, default=True, help='Try to split the file path and name to extract the user name and the machine (TS).')
@click.option('--autoopen/--no-autoopen', is_flag=True, help='Open the resulting excel file. Auto-open is true by default.')
def do_it(path=None, fromdate=None, todate=None, output=None, splitfilename=True, autoopen=True):
    flp = log_parser_engine.FolderLogParser()
    flp.parse(path, None, fromdate, todate, output, splitfilename, autoopen)
