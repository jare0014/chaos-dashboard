@echo off
echo Waking up the Chaos Dashboard...

:: Anchor the script to its current directory
cd /d "%~dp0"

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Launch the dashboard
streamlit run app.py

:: Keep the window open if an error occurs
pause