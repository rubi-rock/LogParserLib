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
C:\Python34\Scripts\pyinstaller --clean gui_main.spec > build.log 2>&1

REM ........ Check build
cd dist\
if exist include rmdir /s /q include
if not exist LogParserLib.exe (
	REM Build failed, log file opening...!?!?!?
	GOTO END
)

cd ..\..


REM .
REM ............ Build done!
REM ................ Package available in : dist\LogParserLib
REM .
REM =================== Finish !!! ===================

:END
if exist build.log start notepad.exe build.log

cd ..
