@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo আগে install.bat চালান।
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name VoxBangla --collect-all speech_recognition --collect-all pyaudio --collect-all bijoy_unicode --hidden-import pyautogui --hidden-import pyperclip vox_bangla.py
if errorlevel 1 (
  echo EXE তৈরি করা যায়নি।
  pause
  exit /b 1
)
echo.
echo তৈরি হয়েছে: dist\VoxBangla.exe
pause
