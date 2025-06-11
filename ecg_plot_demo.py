#!/usr/bin/env python3
"""
ECG Real-time Plotting Demo
This script demonstrates the ECG plotting functionality with simulated data
"""

import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import math

# ECG Plot configuration
PLOT_WINDOW_SIZE = 1000  # Number of data points to display
SAMPLING_RATE = 250  # Sampling rate in Hz
TIME_WINDOW = 4  # Time window in seconds to display

class ECGPlotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5)
        
        # Data storage
        self.ecg_data = deque(maxlen=PLOT_WINDOW_SIZE)
        self.time_data = deque(maxlen=PLOT_WINDOW_SIZE)
        self.start_time = time.time()
        
        # Setup plot
        self.setup_plot()
        
        # Animation
        self.animation = animation.FuncAnimation(
            self.fig, self.update_plot, interval=40, blit=False
        )
        
    def setup_plot(self):
        """Setup the ECG plot appearance"""
        self.ax.set_title('Real-time ECG Signal Demo', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('Time (seconds)', fontsize=12)
        self.ax.set_ylabel('ECG Amplitude (mV)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(0, TIME_WINDOW)
        self.ax.set_ylim(-1.5, 1.5)
        
        # Add some styling
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('#f8f8f8')
        
        # Add heart rate display
        self.heart_rate_text = self.ax.text(0.02, 0.95, 'Heart Rate: -- BPM', 
                                          transform=self.ax.transAxes, 
                                          fontsize=12, fontweight='bold',
                                          bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
    def add_data_point(self, value, timestamp=None):
        """Add a new ECG data point"""
        if timestamp is None:
            timestamp = time.time() - self.start_time
            
        self.ecg_data.append(value)
        self.time_data.append(timestamp)
        
    def calculate_heart_rate(self):
        """Simple heart rate calculation from ECG peaks"""
        if len(self.ecg_data) < 100:
            return None
            
        # Find peaks (simple threshold-based)
        data_array = np.array(list(self.ecg_data))
        time_array = np.array(list(self.time_data))
        
        # Find peaks above threshold
        threshold = np.mean(data_array) + 0.5 * np.std(data_array)
        peaks = []
        
        for i in range(1, len(data_array) - 1):
            if (data_array[i] > threshold and 
                data_array[i] > data_array[i-1] and 
                data_array[i] > data_array[i+1]):
                peaks.append(time_array[i])
        
        if len(peaks) >= 2:
            # Calculate average time between peaks
            intervals = np.diff(peaks)
            if len(intervals) > 0:
                avg_interval = np.mean(intervals)
                heart_rate = 60.0 / avg_interval  # Convert to BPM
                return int(heart_rate)
        
        return None
        
    def update_plot(self, frame):
        """Update the plot with new data"""
        if len(self.ecg_data) > 1:
            # Update line data
            self.line.set_data(list(self.time_data), list(self.ecg_data))
            
            # Update x-axis to show rolling window
            if len(self.time_data) > 0:
                current_time = max(self.time_data)
                self.ax.set_xlim(max(0, current_time - TIME_WINDOW), current_time + 0.5)
            
            # Update heart rate
            heart_rate = self.calculate_heart_rate()
            if heart_rate:
                self.heart_rate_text.set_text(f'Heart Rate: {heart_rate} BPM')
            else:
                self.heart_rate_text.set_text('Heart Rate: Calculating...')
        
        return self.line,
    
    def start_plotting(self):
        """Start the plotting"""
        plt.show()
        
    def close(self):
        """Close the plot"""
        plt.close(self.fig)

class ECGSimulator:
    def __init__(self, plotter):
        self.plotter = plotter
        self.running = False
        self.thread = None
        
    def generate_ecg_sample(self, t):
        """Generate a realistic ECG waveform sample"""
        # Basic ECG parameters
        heart_rate = 75  # BPM
        period = 60.0 / heart_rate  # Period in seconds
        
        # Normalize time to period
        t_norm = (t % period) / period
        
        # Generate ECG components
        # P wave
        p_wave = 0.1 * np.exp(-((t_norm - 0.15) * 20)**2) if abs(t_norm - 0.15) < 0.1 else 0
        
        # QRS complex
        if abs(t_norm - 0.35) < 0.05:
            qrs = 1.0 * np.sin(np.pi * (t_norm - 0.3) / 0.1)
        else:
            qrs = 0
            
        # T wave
        t_wave = 0.3 * np.exp(-((t_norm - 0.7) * 8)**2) if abs(t_norm - 0.7) < 0.15 else 0
        
        # Combine components
        ecg_value = p_wave + qrs + t_wave
        
        # Add some noise
        noise = 0.05 * np.random.normal()
        
        return ecg_value + noise
    
    def simulate_data(self):
        """Simulate ECG data generation"""
        start_time = time.time()
        sample_interval = 1.0 / SAMPLING_RATE
        
        while self.running:
            current_time = time.time() - start_time
            ecg_value = self.generate_ecg_sample(current_time)
            
            self.plotter.add_data_point(ecg_value, current_time)
            
            time.sleep(sample_interval)
    
    def start(self):
        """Start the ECG simulation"""
        self.running = True
        self.thread = threading.Thread(target=self.simulate_data)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop the ECG simulation"""
        self.running = False
        if self.thread:
            self.thread.join()

def main():
    print("ECG Real-time Plotting Demo")
    print("=" * 40)
    print("📊 This demo shows how the real-time ECG plotting works")
    print("💓 Simulated ECG data with realistic heart rate")
    print("📈 Heart rate calculation from ECG peaks")
    print("🎯 Close the plot window to exit")
    print("=" * 40)
    
    try:
        # Create plotter
        plotter = ECGPlotter()
        
        # Create and start simulator
        simulator = ECGSimulator(plotter)
        simulator.start()
        
        # Start plotting (this will block until window is closed)
        plotter.start_plotting()
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    finally:
        if 'simulator' in locals():
            simulator.stop()
        if 'plotter' in locals():
            plotter.close()

if __name__ == "__main__":
    main()