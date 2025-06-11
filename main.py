#!/usr/bin/env python3
"""
BLE Receiver for Raspberry Pi
Receives data from ESP32 nano via Bluetooth Low Energy
"""

import asyncio
import sys
from bleak import BleakScanner, BleakClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ESP32 BLE configuration
ESP32_DEVICE_NAME = "ESP32"  # Change this to match your ESP32's advertised name
SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"  # Change to match ESP32
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"  # Change to match ESP32

class BLEReceiver:
    def __init__(self):
        self.client = None
        self.device = None
        
    async def scan_for_esp32(self, timeout=10):
        """Scan for ESP32 device"""
        logger.info(f"Scanning for ESP32 device: {ESP32_DEVICE_NAME}")
        
        devices = await BleakScanner.discover(timeout=timeout)
        
        for device in devices:
            logger.info(f"Found device: {device.name} - {device.address}")
            if device.name and ESP32_DEVICE_NAME in device.name:
                logger.info(f"Found ESP32: {device.name} ({device.address})")
                return device
                
        logger.warning("ESP32 device not found")
        return None
    
    async def notification_handler(self, sender, data):
        """Handle incoming BLE notifications"""
        try:
            # Decode the received data
            message = data.decode('utf-8')
            logger.info(f"Received: {message}")
            print(f"ESP32 Data: {message}")
        except UnicodeDecodeError:
            # Handle binary data
            logger.info(f"Received binary data: {data.hex()}")
            print(f"ESP32 Binary: {data.hex()}")
    
    async def connect_and_receive(self):
        """Connect to ESP32 and start receiving data"""
        try:
            # Scan for ESP32
            self.device = await self.scan_for_esp32()
            if not self.device:
                logger.error("Could not find ESP32 device")
                return False
            
            # Connect to the device
            logger.info(f"Connecting to {self.device.address}")
            self.client = BleakClient(self.device.address)
            
            await self.client.connect()
            logger.info("Connected successfully!")
            
            # Check if device is connected
            if not self.client.is_connected:
                logger.error("Failed to connect to device")
                return False
            
            # Get services and characteristics
            logger.info("Discovering services...")
            services = await self.client.get_services()
            
            for service in services:
                logger.info(f"Service: {service.uuid}")
                for char in service.characteristics:
                    logger.info(f"  Characteristic: {char.uuid} - Properties: {char.properties}")
            
            # Start notifications if characteristic supports it
            try:
                await self.client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)
                logger.info(f"Started notifications on {CHARACTERISTIC_UUID}")
            except Exception as e:
                logger.warning(f"Could not start notifications: {e}")
                logger.info("Trying to read characteristic instead...")
                
                # Alternative: Read characteristic periodically
                while self.client.is_connected:
                    try:
                        data = await self.client.read_gatt_char(CHARACTERISTIC_UUID)
                        await self.notification_handler(CHARACTERISTIC_UUID, data)
                        await asyncio.sleep(1)  # Read every second
                    except Exception as read_error:
                        logger.error(f"Error reading characteristic: {read_error}")
                        break
            
            # Keep connection alive
            logger.info("Listening for data... Press Ctrl+C to stop")
            while self.client.is_connected:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect from the device"""
        if self.client and self.client.is_connected:
            try:
                await self.client.stop_notify(CHARACTERISTIC_UUID)
            except:
                pass
            await self.client.disconnect()
            logger.info("Disconnected")

async def main():
    """Main function"""
    print("ESP32 BLE Receiver for Raspberry Pi")
    print("=" * 40)
    
    receiver = BLEReceiver()
    await receiver.connect_and_receive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)