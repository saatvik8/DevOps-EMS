#!/bin/sh
pip install -r requirements.txt
pyinstaller --onefile --name ems --add-data "templates:templates" --add-data "static:static" app.py
echo "Done. Run ./dist/ems"
