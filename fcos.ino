#include "BLEDevice.h"
#include "BLEServer.h"
#include "BLEUtils.h"
#include "BLE2902.h"

// BLE Variables
BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// UUIDs (must match with the client Python side)
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-cba987654321"

// ECG and lead-off pin configuration
#define ECG_PIN A0
#define LO_PLUS 12
#define LO_MINUS 13

// Callback to handle BLE connection state
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("Device connected");
    };
    
    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("Device disconnected");
      // Don't restart advertising here - do it in main loop
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE ECG device");
  
  pinMode(ECG_PIN, INPUT);
  pinMode(LO_PLUS, INPUT);
  pinMode(LO_MINUS, INPUT);
  
  // Initialize BLE with name
  BLEDevice::init("ESP32_ECG");
  
  // Create BLE server and set callbacks
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  // Create BLE service and characteristic
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  pCharacteristic->addDescriptor(new BLE2902());
  
  // Start BLE service and advertising
  pService->start();
  
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  pAdvertising->setMaxPreferred(0x0);
  
  BLEDevice::startAdvertising();
  Serial.println("BLE ECG device ready and advertising...");
}

void loop() {
  // Handle BLE connection state changes
  if (!deviceConnected && oldDeviceConnected) {
    // Device just disconnected
    Serial.println("Restarting advertising...");
    delay(500); // Give some time for cleanup
    pServer->startAdvertising();
    oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected && !oldDeviceConnected) {
    // Device just connected
    oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected) {
    int loPlus = digitalRead(LO_PLUS);
    int loMinus = digitalRead(LO_MINUS);
    
    if (loPlus == HIGH || loMinus == HIGH) {
      // If electrodes are not properly connected
      pCharacteristic->setValue("Leads off");
      Serial.println("Leads off");
    } else {
      // Read ECG data
      int ecg = analogRead(ECG_PIN); // ADC value (0-4095 for ESP32 12-bit ADC)
      String ecgStr = String(ecg);
      pCharacteristic->setValue(ecgStr.c_str());
      Serial.println("ECG: " + ecgStr);
    }
    
    pCharacteristic->notify();  // Send data to BLE client
    delay(50); // ~20 Hz sampling rate
  } else {
    Serial.println("Waiting for device to connect...");
    delay(1000);
  }
}
