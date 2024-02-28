@echo off
setlocal enabledelayedexpansion

REM 指定待搜索的文件名
set "FileName=ui_main.py"
set "FoundPath="

REM 在当前目录及其子目录中搜索文件
for /r %%i in (%FileName%) do (
    set "FoundPath=%%i"
    goto :FoundFile
)

:NotFound
echo Error! not found ui_main.py: !FileName! not execute any command!
goto :EOF

:FoundFile
echo find path dir: !FoundPath!.
python !FoundPath!
echo program already exited!
goto :EOF

endlocal
