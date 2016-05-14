# -*- mode: python -*-
a = Analysis(['gui_main.py'],
             #pathex=[r'..\setup'],
             hiddenimports = ['uuid'],
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='LogParserLib.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
		  icon=r'..\LogParserGUI\icons\log_oxigen_32.ico',
		  version=r'..\version.txt')

def addRequiredFiles(srcFolder, dstFolder, dataType):
    import os

    extraDatas = []
    absoluteSrcPath = os.path.abspath(srcFolder)
    splitter = srcFolder.replace('..', '').replace('\\', '')
    for (root, dirnames, filenames) in os.walk(absoluteSrcPath):
        for filename in filenames:
            splittedPath = root.split(splitter)
            newPath = dstFolder
            if len(splittedPath) == 2:
                newPath = dstFolder + splittedPath[1].lstrip( '\\')
            srcFile = os.path.join(root, filename)
            dstFile = os.path.join(newPath, filename)
            print('    copy ' + srcFile + ' to ' + dstFile)
            extraDatas.append(( dstFile, srcFile, dataType))
    return extraDatas


# append required DLL from microsoft
a.binaries += addRequiredFiles( 'requirements\\DLLs\\', '', 'BINARY')
# append the translations directory
a.datas = None
#a.datas += addRequiredFiles( '..\\translations\\', 'translations\\', 'DATA')
#a.datas += addRequiredFiles( '..\\static\\', 'static\\', 'DATA')
#a.datas += addRequiredFiles( '..\\templates\\', 'templates\\', 'DATA')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='LogParserLib')

