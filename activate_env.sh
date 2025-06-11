#!/bin/bash
# Activation script for BLE receiver

echo "Activating virtual environment and starting BLE receiver..."
cd /home/hp/Desktop/ble_rec
source venv/bin/activate
python3 main.py
