@echo off
title Not-a-Doom
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"
echo Starting Not-a-Doom...
call .\venv\Scripts\activate
python src\main.py
pause
