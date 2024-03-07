@echo off
setlocal enabledelayedexpansion

set "current_directory=%cd%"
set "output_file=folders.txt"

dir /ad /b "%current_directory%" | findstr /v /c:".\" /c:"..\" > "%output_file%"

echo Folders have been listed in: %output_file%