#!/bin/bash
# Activate the virtual environment
echo "Activating BLE receiver virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo "You can now run:"
echo "  python3 scanner.py  - to scan for ESP32 devices"
echo "  python3 main.py     - to start the BLE receiver"
echo ""
echo "To deactivate, type: deactivate"
