@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher পাওয়া যায়নি। Python 3.11 64-bit ইনস্টল করুন।
  echo https://www.python.org/downloads/windows/
  pause
  exit /b 1
)
py -3.11 --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 পাওয়া যায়নি। Python 3.11 64-bit ইনস্টল করে আবার চালান।
  pause
  exit /b 1
)
if not exist .venv py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto failed
python -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo ইনস্টলেশন সম্পন্ন হয়েছে। এখন run.bat চালান।
pause
exit /b 0
:failed
echo.
echo ইনস্টলেশনে সমস্যা হয়েছে। ইন্টারনেট সংযোগ এবং Python 3.11 পরীক্ষা করুন।
pause
exit /b 1
