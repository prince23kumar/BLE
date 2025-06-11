#!/usr/bin/env python3
"""
Enhanced BLE Scanner with troubleshooting features
"""

import asyncio
import sys
from bleak import BleakScanner
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def enhanced_scan():
    """Enhanced scan with more detailed output and troubleshooting"""
    print("Enhanced BLE Scanner - Troubleshooting Mode")
    print("=" * 60)
    
    try:
        print("1. Checking BLE adapter availability...")
        
        # Try a longer scan with more verbose output
        print("2. Starting extended scan (15 seconds)...")
        print("   Make sure your ESP32 is powered on and advertising!")
        print("   Scanning...")
        
        devices = await BleakScanner.discover(timeout=15, return_adv=True)
        
        print(f"\n3. Scan completed! Found {len(devices)} device(s)")
        print("-" * 60)
        
        if not devices:
            print("❌ No BLE devices found!")
            print("\nTroubleshooting steps:")
            print("1. Make sure your ESP32 is powered on")
            print("2. Ensure your ESP32 is running BLE advertising code")
            print("3. Check if ESP32 is in range (try moving closer)")
            print("4. Verify ESP32 BLE code is actually advertising")
            print("5. Try scanning with your phone's BLE scanner app")
            return
        
        # Display all found devices with detailed info
        for i, (device, adv_data) in enumerate(devices.items(), 1):
            print(f"\n📱 Device {i}:")
            print(f"   Name: {device.name or 'Unknown/Hidden'}")
            print(f"   Address: {device.address}")
            print(f"   RSSI: {adv_data.rssi} dBm")
            
            # Show service UUIDs if available
            if adv_data.service_uuids:
                print(f"   Service UUIDs: {list(adv_data.service_uuids)}")
            
            # Show manufacturer data if available
            if adv_data.manufacturer_data:
                print(f"   Manufacturer Data: {dict(adv_data.manufacturer_data)}")
            
            # Show service data if available
            if adv_data.service_data:
                print(f"   Service Data: {dict(adv_data.service_data)}")
            
            # Check if this might be an ESP32
            device_indicators = []
            if device.name:
                name_lower = device.name.lower()
                if any(keyword in name_lower for keyword in ['esp32', 'esp', 'arduino', 'microcontroller']):
                    device_indicators.append("Name suggests ESP32")
            
            if adv_data.manufacturer_data:
                # ESP32 often uses Espressif's manufacturer ID
                if 0x02E5 in adv_data.manufacturer_data:  # Espressif's manufacturer ID
                    device_indicators.append("Espressif manufacturer ID detected")
            
            if device_indicators:
                print(f"   🎯 POSSIBLE ESP32: {', '.join(device_indicators)}")
            
            print("-" * 40)
    
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        print(f"\n❌ Error: {e}")
        print("\nThis might be a permissions issue. Try running with sudo:")
        print("sudo python3 enhanced_scanner.py")

async def test_basic_ble():
    """Test basic BLE functionality"""
    print("\n🔧 Testing basic BLE functionality...")
    
    try:
        # Quick test scan
        devices = await BleakScanner.discover(timeout=3)
        print(f"✅ BLE is working - quick scan found {len(devices)} devices")
        return True
    except Exception as e:
        print(f"❌ BLE test failed: {e}")
        return False

if __name__ == "__main__":
    print("ESP32 BLE Enhanced Scanner & Troubleshooter")
    print("This will help diagnose why your ESP32 isn't being found")
    print()
    
    try:
        asyncio.run(test_basic_ble())
        print()
        asyncio.run(enhanced_scan())
        
        print("\n" + "=" * 60)
        print("💡 TIPS:")
        print("1. If no devices found, try running: sudo python3 enhanced_scanner.py")
        print("2. Make sure ESP32 is advertising (check your ESP32 code)")
        print("3. ESP32 should have code like: BLEDevice::init(\"ESP32-Device\");")
        print("4. Try using a BLE scanner app on your phone to verify ESP32 is advertising")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scan stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)