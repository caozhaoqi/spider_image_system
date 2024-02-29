@echo off
setlocal

REM 删除dist和build目录
if exist "dist" (
    rmdir /s /q "dist"
)
if exist "build" (
    rmdir /s /q "build"
)

REM 运行pyinstaller main_sis.spec进行打包
pyinstaller main_sis.spec

endlocal