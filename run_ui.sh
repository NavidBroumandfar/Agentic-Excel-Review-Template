#!/bin/bash
# Quick launcher for Excel Review Streamlit UI
# This script starts the Streamlit web interface for the Excel Review Assistant
#
# FIRST TIME SETUP (Mac/Linux):
# Make this script executable by running:
#   chmod +x run_ui.sh
#
# Then run with:
#   ./run_ui.sh
# or
#   bash run_ui.sh

echo "================================================"
echo "Excel Review Agentic Assistant - Streamlit UI"
echo "================================================"
echo ""
echo "Starting Streamlit application..."
echo "The app will open in your browser automatically."
echo ""
echo "Press Ctrl+C to stop the server when done."
echo "================================================"
echo ""

streamlit run src/ui/excel_review_app.py


