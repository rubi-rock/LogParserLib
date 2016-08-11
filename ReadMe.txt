Scope and goals:
================
This porject parse a folder and it's subfolder looking for Purkinje log files 
(.log) and backed-up log files (.bak) to extract relevant information to 
analyze without having a human being walking through thousands - even millions 
- lines of logs.

The goal is to generate an excel file that present the errors or abnomalies
in a spreedsheet easy to manipulate that allows to jump to the original log
file when required if it is on the same machine.

With time, the excel file has been enriched and presend different statistics
on the log list collected to help. e.g.: which user has most errors, which 
machine has most problems.

How to install & use the LogParser:
===================================
	You need an internet connection because it downloads the components from
	the web.
	
	Go to the folder install then run in order:
	
		install - part I.bat
		install - part II.bat
		
	WARNING: 	When installing the path to Python must be added to the 
				Windows' PATH environment variable, thus don't forget
				to check the "Add Python 3.5 to PATH" checkbox when
				installing Python.
				
				The reason why the install process requires 2 batch files is
				that when you install Python it will update the PATH 
				environment variable, unfortunatelly the command line session
				has been started whithout this and won't be updated. So you
				must start another command line session because the path
				to python is required for part II. There is - maybe - a way 
				to workaround this limitation but I dif not spend time to 
				figure it out.
	
What Environment to use to modify it:
=====================================
This tool is built on Python 3.5 to be able to adjust it without going through 
a development process which requires overloaded resources and a long delivery 
lifecyle. This can be done by any resource able to do scripting and willing
to use/learn Python.

I strongly recommand to use PyCharm (Community Edition) to work 
on this project. It's a full Python IDE to develop and debug Python scripts.
It's much more easier than many other options + it can install all required 
python components easily (easier than pip, easy_install...).

This project is composed of 2 parts:
====================================
	UI :	
	----
		Build with Qt5 which is a fUI engine that can be used with many		
		programming languages - including Python. After experiencing it not 
		that difficult to use, still look like doing an eForm with all 
		idiosyncrasies when you do formatting with merges cells/rows.
		
		The Qt5 file is not used directly, using the gen_ui batch file, it 
		will generate the corresponding Python files. Then it you just to 
		connect the form events to your python :
			LogParserMainWindow.py
		
		NOTE: 	for a full list of required components, just open the following
				files from the install folder:
					install - part I.bat
					install - part II.bat

		NOTE: 	At run time the PyQt5 libarary is required. 
			
	Business rules:
	---------------
		The code is not that beautiful because at the beginning it was aping
		the original LogParser written in Delphi to figure out the parsing
		logic. It changed a lot since and the Python code too, but the 
		refactoring has not been done everywhere.
		
		Also, some pieces of code are neither Pythonish style nor the simpliest
		manner to do it. There is a reason for that: when the logs are full of 
		errors or when the statistic mode is ON, then the number of lines to 
		parse is huge. I got logs from sites with over 63 millions log lines
		accross 4-5 TS server. When you parse such amount of logs, then the
		parsing must be more efficient than beautiful or pythonish style.
		
		Some entry points on the main components:
			log_parser_engine.py	contains the engine that walk through the 
									folders and parses the log files
									
			log_parser_objects.py	contains the log objects, i.e.: log file, 
									session, line...

	Some useful linkes:
	-------------------
			Python:		https://www.python.org/
			pycharm:	https://www.jetbrains.com/pycharm/download/#section=windows
			Qt5:		https://www.qt.io/download/
			PyQt5:		https://www.riverbankcomputing.com/software/pyqt/download5
							
									
	Delivering:
	-----------
		To deliver the LogParser, the easiest eay is to run the Package.bat 
		file that will generate the LogParserLib.zip file.
		
		Provide the zip file with the instructions from the How to install & 
		use the LogParser" section at the beginning of this document.
		