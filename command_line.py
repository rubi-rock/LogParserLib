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
def show_it(path=None, fromdate=None, todate=None):
    mainwindow = LogParserGUI.LogParserMainWindows(path, fromdate, todate)
    mainwindow.ShowMainWindow()


@click.command()
@click.option('--path', default=None, type=click.Path(exists=True), help='Path containing the log files to parse')
@click.option('--fromdate', default=str(datetime.now().date() - timedelta(days=7)),
              help='Log entries before that date will be ignored. Format: yyyy-mm-dd')
@click.option('--todate', default=str(datetime.now().date() + timedelta(days=1)),
              help='Log entries after that date will be ignored. Format: yyyy-mm-dd')
def do_it(path=None, fromdate=None, todate=None):
    flp = log_parser_engine.FolderLogParser()
    flp.parse(path, None, fromdate, todate)
