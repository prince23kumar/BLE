#!/usr/bin/env python3
"""
Simple BLE Scanner to find ESP32 devices
"""
import asyncio
import sys
from bleak import BleakScanner

async def scan_for_devices():
    print("🔍 Starting BLE scan for 10 seconds...")
    print("Looking for ESP32 devices...")
    print("-" * 50)
    
    try:
        # Scan for devices
        devices = await BleakScanner.discover(timeout=10.0)
        
        if not devices:
            print("❌ No BLE devices found!")
            return
        
        print(f"✅ Found {len(devices)} device(s):")
        print("=" * 70)
        
        esp32_devices = []
        
        for i, device in enumerate(devices, 1):
            # Get device info safely
            address = device.address if hasattr(device, 'address') else 'Unknown'
            name = device.name if hasattr(device, 'name') and device.name else 'Unknown'
            rssi = device.rssi if hasattr(device, 'rssi') else 'Unknown'
            
            print(f"📱 Device {i}:")
            print(f"   Name: {name}")
            print(f"   Address: {address}")
            print(f"   RSSI: {rssi} dBm")
            
            # Check if this might be an ESP32
            is_esp32 = False
            if name and name != 'Unknown':
                name_lower = name.lower()
                if any(keyword in name_lower for keyword in ['esp32', 'esp', 'arduino', 'devkit']):
                    is_esp32 = True
                    esp32_devices.append(device)
                    print(f"   🎯 POTENTIAL ESP32 DEVICE!")
            
            # Check manufacturer data for ESP32 signatures
            if hasattr(device, 'metadata') and device.metadata:
                manufacturer_data = device.metadata.get('manufacturer_data', {})
                if manufacturer_data:
                    print(f"   Manufacturer Data: {manufacturer_data}")
                    # Espressif company ID is 741 (0x02E5)
                    if 741 in manufacturer_data:
                        is_esp32 = True
                        esp32_devices.append(device)
                        print(f"   🎯 ESP32 DETECTED (Espressif manufacturer)!")
            
            print("-" * 50)
        
        if esp32_devices:
            print(f"\n🎉 Found {len(esp32_devices)} potential ESP32 device(s)!")
            print("Try connecting to these devices.")
        else:
            print("\n❓ No obvious ESP32 devices found.")
            print("Your ESP32 might be using a generic name or not advertising properly.")
            
    except Exception as e:
        print(f"❌ Error during scanning: {e}")
        return False
    
    return True

def main():
    print("ESP32 BLE Scanner")
    print("=" * 30)
    
    # Check if we need to suggest sudo
    try:
        result = asyncio.run(scan_for_devices())
        if not result:
            print("\n💡 If you're having permission issues, try:")
            print("sudo python3 simple_scanner.py")
    except Exception as e:
        print(f"❌ Scanner failed: {e}")
        print("\n💡 Try running with sudo:")
        print("sudo python3 simple_scanner.py")

if __name__ == "__main__":
    main()