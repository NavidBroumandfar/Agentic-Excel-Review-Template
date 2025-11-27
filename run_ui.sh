#!/bin/bash
# Quick launcher for MTCR Streamlit UI
# This script starts the Streamlit web interface for the MTCR Assistant
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
echo "MTCR Agentic Assistant - Streamlit UI Launcher"
echo "================================================"
echo ""
echo "Starting Streamlit application..."
echo "The app will open in your browser automatically."
echo ""
echo "Press Ctrl+C to stop the server when done."
echo "================================================"
echo ""

streamlit run src/ui/mtcr_app.py

