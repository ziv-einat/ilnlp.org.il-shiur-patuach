@echo off
cd /d "%~dp0"
echo מפרסם עדכונים לאתר...
"C:\Program Files\Git\cmd\git.exe" add lessons_data.json settings.json
"C:\Program Files\Git\cmd\git.exe" commit -m "עדכון שיעורים והגדרות"
"C:\Program Files\Git\cmd\git.exe" push
echo.
echo הפרסום הושלם! האתר יתעדכן תוך כדקה.
pause
