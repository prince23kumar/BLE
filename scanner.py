#!/usr/bin/env python3
"""
BLE Scanner for discovering ESP32 devices
Run this first to find your ESP32's details
"""

import asyncio
from bleak import BleakScanner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scan_ble_devices():
    """Scan for all BLE devices and show their details"""
    print("Scanning for BLE devices...")
    print("=" * 50)
    
    devices = await BleakScanner.discover(timeout=10)
    
    if not devices:
        print("No BLE devices found")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"{i}. Device: {device.name or 'Unknown'}")
        print(f"   Address: {device.address}")
        print(f"   RSSI: {device.rssi} dBm")
        print(f"   Details: {device.details}")
        print("-" * 30)

if __name__ == "__main__":
    print("ESP32 BLE Device Scanner")
    print("This will help you find your ESP32's advertised name and address")
    print()
    
    try:
        asyncio.run(scan_ble_devices())
    except Exception as e:
        logger.error(f"Error: {e}")
        print("Make sure Bluetooth is enabled and you have the required permissions")