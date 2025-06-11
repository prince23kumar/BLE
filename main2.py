#!/usr/bin/env python3
"""
BLE Receiver for Raspberry Pi
Receives ECG data from ESP32 via Bluetooth Low Energy and plots it in real-time.
"""

import asyncio
import sys
import threading
from bleak import BleakScanner, BleakClient
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BLE Config
ESP32_DEVICE_NAME = "ESP32"
SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"

# Plotting config
SAMPLING_RATE = 50  # Hz
WINDOW_SECONDS = 5
MAX_POINTS = SAMPLING_RATE * WINDOW_SECONDS
ecg_data = deque([0]*MAX_POINTS, maxlen=MAX_POINTS)

# Global variables for coordination
ble_receiver = None
stop_event = threading.Event()
fig = None
ax = None
line = None

class BLEReceiver:
    def __init__(self):
        self.client = None
        self.device = None
        self.connected = False

    async def scan_for_esp32(self, timeout=10):
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
        try:
            message = data.decode('utf-8').strip()
            logger.debug(f"Received: {message}")
            if message.isdigit():
                ecg_value = int(message)
                ecg_data.append(ecg_value)
                logger.debug(f"Added ECG value: {ecg_value}")
        except Exception as e:
            logger.warning(f"Failed to parse data: {e}")

    async def connect_and_receive(self):
        try:
            self.device = await self.scan_for_esp32()
            if not self.device:
                logger.error("Could not find ESP32 device")
                return False

            logger.info(f"Connecting to {self.device.address}")
            self.client = BleakClient(self.device.address)
            await self.client.connect()
            logger.info("Connected successfully!")

            if not self.client.is_connected:
                logger.error("Failed to connect to device")
                return False

            self.connected = True

            logger.info("Discovering services...")
            services = await self.client.get_services()
            
            # Check if our characteristic exists
            char_found = False
            for service in services:
                for char in service.characteristics:
                    logger.debug(f"  Characteristic: {char.uuid} - Properties: {char.properties}")
                    if str(char.uuid).lower() == CHARACTERISTIC_UUID.lower():
                        char_found = True

            if not char_found:
                logger.warning(f"Characteristic {CHARACTERISTIC_UUID} not found. Available characteristics:")
                for service in services:
                    for char in service.characteristics:
                        logger.info(f"  {char.uuid} - {char.properties}")

            try:
                await self.client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)
                logger.info(f"Started notifications on {CHARACTERISTIC_UUID}")
            except Exception as e:
                logger.error(f"Notification setup failed: {e}")
                return False

            logger.info("Listening for data... Close the plot window to stop.")
            while self.client.is_connected and not stop_event.is_set():
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"BLE Error: {e}")
        finally:
            await self.disconnect()

    async def disconnect(self):
        if self.client and self.client.is_connected:
            try:
                await self.client.stop_notify(CHARACTERISTIC_UUID)
                logger.info("Stopped notifications")
            except Exception as e:
                logger.warning(f"Error stopping notifications: {e}")
            
            try:
                await self.client.disconnect()
                logger.info("Disconnected from BLE device")
            except Exception as e:
                logger.warning(f"Error disconnecting: {e}")
        
        self.connected = False

def run_ble_async():
    """Run BLE operations in a separate thread with its own event loop"""
    global ble_receiver
    
    async def ble_main():
        ble_receiver = BLEReceiver()
        await ble_receiver.connect_and_receive()
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(ble_main())
    except Exception as e:
        logger.error(f"BLE thread error: {e}")
    finally:
        loop.close()

def update_plot(frame):
    """Update the plot with new ECG data"""
    global line, ax, ble_receiver
    
    # Update the line data
    line.set_ydata(list(ecg_data))
    
    # Auto-scale y-axis based on data
    if len(ecg_data) > 0:
        data_list = list(ecg_data)
        data_min = min(data_list)
        data_max = max(data_list)
        if data_max > data_min:
            margin = (data_max - data_min) * 0.1
            ax.set_ylim(data_min - margin, data_max + margin)
    
    # Update connection status in title
    if ble_receiver and ble_receiver.connected:
        ax.set_title(f"Real-Time ECG Signal - Connected (Latest: {ecg_data[-1]})")
    else:
        ax.set_title("Real-Time ECG Signal - Disconnected")
    
    return line,

def on_close(event):
    """Handle plot window close event"""
    logger.info("Plot window closed, stopping BLE operations...")
    stop_event.set()

def main():
    global fig, ax, line
    
    print("ESP32 BLE Receiver for Raspberry Pi")
    print("=" * 40)
    print("Starting BLE connection...")
    
    # Setup matplotlib to use a backend that works well with threading
    plt.ion()  # Turn on interactive mode
    
    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot(range(MAX_POINTS), list(ecg_data), 'b-', linewidth=1)
    ax.set_ylim(0, 4095)
    ax.set_xlim(0, MAX_POINTS)
    ax.set_title("Real-Time ECG Signal - Connecting...")
    ax.set_xlabel("Samples")
    ax.set_ylabel("ECG Value (0-4095)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Connect close event
    fig.canvas.mpl_connect('close_event', on_close)
    
    # Start BLE operations in a separate thread
    ble_thread = threading.Thread(target=run_ble_async, daemon=True)
    ble_thread.start()
    
    # Start the animation with proper interval for real-time updates
    ani = animation.FuncAnimation(fig, update_plot, interval=20, blit=False, cache_frame_data=False)
    
    # Show the plot (this blocks until window is closed)
    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    # Signal BLE thread to stop
    stop_event.set()
    
    # Wait for BLE thread to finish
    if ble_thread.is_alive():
        ble_thread.join(timeout=2)
    
    print("Program finished")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        stop_event.set()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
