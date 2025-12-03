@echo off
REM Quick launcher for Excel Review Streamlit UI
REM This script starts the Streamlit web interface for the Excel Review Assistant

echo ================================================
echo Excel Review Agentic Assistant - Streamlit UI
echo ================================================
echo.
echo Starting Streamlit application...
echo The app will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo ================================================
echo.

streamlit run src/ui/excel_review_app.py

pause


