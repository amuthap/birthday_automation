@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\vijay\OneDrive\Desktop\BirthdayAuto (FINAL) - Copy\textScrape"
"C:\Python313\python.exe" daily_job.py >> "rotasmart.log" 2>&1
