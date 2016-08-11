@echo off

echo READ THIS TO BE ABLE TO INSTALL SUCCESULLY:
echo ===========================================
echo .
echo    When instailling Python (next step), there is a checkbox 
echo    at the bottom of the first screen to add the Python 
echo    installation path to the Windows PATH Environment variable
echo . 
echo    To succeed installing the LogParser you must check this checkbox
echo                      "Add Python 3.5 to PATH"
echo    before clicking the install button.
echo .
echo .
set /p ask="DO YOU UNDERSTAND? (y/n)"
echo .
if %ask%==y (echo "Let's do it then...") else goto ABORT

echo .

REM Install Python
echo Install Python...
wget --no-check-certificate https://www.python.org/ftp/python/3.5.1/python-3.5.1-amd64.exe
python-3.5.1-amd64.exe
del python-3.5.1-amd64.exe
echo Python installed!
echo .

REM Install PyQt5
echo Install PyQt5 ...
wget --no-check-certificate "http://heanet.dl.sourceforge.net/project/pyqt/PyQt5/PyQt-5.6/PyQt5-5.6-gpl-Py3.5-Qt5.6.0-x64-2.exe"
call PyQt5-5.6-gpl-Py3.5-Qt5.6.0-x64-2.exe
del PyQt5-5.6-gpl-Py3.5-Qt5.6.0-x64-2.exe
echo PyQt5 installed!!!
echo .

cd ..

echo INSTALLATION DONE!!!!!!!
echo Run LogParser.bat to start the application...
echo .

goto EOF

:ABORT
echo .
echo "Ask someone to help you or ... forget it!"
echo .
goto EOF

:EOF
