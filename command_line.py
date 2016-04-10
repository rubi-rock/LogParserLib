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
def show_it(path=None, fromdate=None, todate=None, output=None):
    mainwindow = LogParserGUI.LogParserMainWindows(path, fromdate, todate, output)
    mainwindow.ShowMainWindow()


@click.command()
@click.option('--path', default=None, type=click.Path(exists=True), help='Path containing the log files to parse')
@click.option('--fromdate', default=str(datetime.now().date() - timedelta(days=7)),
              help='Log entries before that date will be ignored. Format: yyyy-mm-dd')
@click.option('--todate', default=str(datetime.now().date() + timedelta(days=1)),
              help='Log entries after that date will be ignored. Format: yyyy-mm-dd')
@click.option('--output', default=None,
              help='Indicates the output file name (with or without extention - by default it''s xlsx). If no this option is not specified then a file name is generated. If the path is relative, the file is saved in the same folder than this tool')
def do_it(path=None, fromdate=None, todate=None, output=None):
    flp = log_parser_engine.FolderLogParser()
    flp.parse(path, None, fromdate, todate, output)
