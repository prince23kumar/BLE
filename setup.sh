#!/bin/bash
echo "Setting up BLE Receiver for Raspberry Pi"
echo "========================================"

# Update system packages
echo "Updating system packages..."
sudo apt update

# Install required system packages for BLE
echo "Installing BLE dependencies..."
sudo apt install -y python3-pip bluetooth bluez libbluetooth-dev

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Enable and start Bluetooth service
echo "Enabling Bluetooth service..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Check Bluetooth status
echo "Checking Bluetooth status..."
sudo systemctl status bluetooth --no-pager

echo ""
echo "Setup complete!"
echo "To run the BLE receiver: python3 main.py"
echo ""
echo "Make sure to update the following in main.py:"
echo "1. ESP32_DEVICE_NAME - Set to your ESP32's advertised name"
echo "2. SERVICE_UUID - Set to match your ESP32's service UUID"
echo "3. CHARACTERISTIC_UUID - Set to match your ESP32's characteristic UUID"
