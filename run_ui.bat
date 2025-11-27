@echo off
REM Quick launcher for MTCR Streamlit UI
REM This script starts the Streamlit web interface for the MTCR Assistant

echo ================================================
echo MTCR Agentic Assistant - Streamlit UI Launcher
echo ================================================
echo.
echo Starting Streamlit application...
echo The app will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo ================================================
echo.

streamlit run src/ui/mtcr_app.py

pause

