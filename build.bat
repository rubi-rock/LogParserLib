@echo on
cls

cd ExePackager

REM =================== Cleanup ===================
if exist build.log del /f build.log
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del *.py
del *.pyc

if "%1%" == "clean" GOTO END
if "%1%" == "CLEAN" GOTO END
if "%1%" == "Clean" GOTO END

REM =================== Check requirements ===================
if not exist gui_main.spec REM Missing required file: patient_kiosk.spec
cd requirements\DLLs
if not exist msvcm90.dll REM Missing required file: requirements\DLLs\msvcm90.dll
if not exist msvcp90.dll REM Missing required file: requirements\DLLS\msvcp90.dll
if not exist msvcr90.dll REM  Missing required file: requirements\DLLS\msvcr90.dll
if not exist Microsoft.VC90.CRT.manifest REM Missing required file: requirements\DLLS\Microsoft.VC90.CRT.manifest
cd ..\..

REM =================== Sart the build ===================
REM .... Copy source files
copy ..\*.py

REM =================== Sart the build ===================
REM .... Run PyInstaller
REM pyinstaller --clean ..\patient_kiosk.py > build.log 2>&1
C:\Python34\Scripts\pyinstaller --clean gui_main.spec > build.log 2>&1

REM ........ Check build
cd dist\patient_kiosk
if exist include rmdir /s /q include
if not exist gui_main.exe (
	REM Build failed, log file opening...!?!?!?
	GOTO END
)
ren gui_main.exe LogParserLib.exe
cd ..\..


REM =================== Add required files ===================
REM copy .\requirements\DLLs\*.* dist\patient_kiosk > nul
REM xcopy /Q /I /E ..\static dist\patient_kiosk\static
REM xcopy /Q /I /E ..\templates dist\patient_kiosk\templates
REM xcopy /Q /I /E ..\translations dist\patient_kiosk\translations

REM .
REM ............ Build done!
REM ................ Package available in : dist\patient_kiosk
REM .
REM =================== Finish !!! ===================
REM .
REM .
REM ********************************* WARNING *********************************
REM If you get an error about the uuid module (related to _mssqpl.pyx) when you
REM run patient_kiosk.exe then you need to copy the file from
REM requirements\PyInstaller\hook-_mssql.py to the Python' library package path
REM .
REM This path looks like
REM   C:\Python27\Lib\site-packages\PyInstaller-2.1-py2.7.egg\PyInstaller\hooks
REM but it depends on your python version and instalation path (c:\Python27),
REM yourversion of PyInstaller (PyInstaller-2.1-py2.7.egg) and eventually it
REM depends how you installed PyInstaller (windows installer or manually).
REM ********************************* WARNING *********************************


:END
if exist build.log start notepad.exe build.log
