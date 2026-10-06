@echo off
REM Build a standalone Windows executable -> dist\ems.exe
python -m pip install -r requirements.txt
pyinstaller --onefile --name ems --add-data "templates;templates" --add-data "static;static" app.py
echo.
echo Done. Run dist\ems.exe  (opens http://127.0.0.1:5000)
pause
