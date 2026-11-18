@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo আগে install.bat চালিয়ে প্রয়োজনীয় প্যাকেজ ইনস্টল করুন।
  pause
  exit /b 1
)
.venv\Scripts\python.exe vox_bangla.py
if errorlevel 1 pause
