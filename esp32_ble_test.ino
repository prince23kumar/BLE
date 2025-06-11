/*
  ESP32 BLE Test Code
  This code makes your ESP32 visible and connectable via BLE
  Upload this to your ESP32 to test BLE functionality
*/

#include "BLEDevice.h"
#include "BLEServer.h"
#include "BLEUtils.h"
#include "BLE2902.h"

// BLE Server and Service variables
BLEServer* pServer = NULL;
BLECharacteristic* pTxCharacteristic;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// UUIDs for our service and characteristics
#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // UART service UUID
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("Device connected!");
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("Device disconnected!");
    }
};

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      String rxValue = pCharacteristic->getValue();

      if (rxValue.length() > 0) {
        Serial.println("*********");
        Serial.print("Received Value: ");
        for (int i = 0; i < rxValue.length(); i++)
          Serial.print(rxValue[i]);
        Serial.println();
        Serial.println("*********");
      }
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP32 BLE Test...");

  // Create the BLE Device
  BLEDevice::init("ESP32-BLE-Test"); // This name will appear in BLE scans
  Serial.println("BLE Device initialized with name: ESP32-BLE-Test");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic for TX (sending data)
  pTxCharacteristic = pService->createCharacteristic(
                    CHARACTERISTIC_UUID_TX,
                    BLECharacteristic::PROPERTY_NOTIFY
                  );
                      
  pTxCharacteristic->addDescriptor(new BLE2902());

  // Create a BLE Characteristic for RX (receiving data)
  BLECharacteristic * pRxCharacteristic = pService->createCharacteristic(
                       CHARACTERISTIC_UUID_RX,
                       BLECharacteristic::PROPERTY_WRITE
                     );

  pRxCharacteristic->setCallbacks(new MyCallbacks());

  // Start the service
  pService->start();
  Serial.println("BLE Service started");

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
  
  Serial.println("🎯 BLE ADVERTISING STARTED!");
  Serial.println("📱 Look for 'ESP32-BLE-Test' in BLE scanners");
  Serial.println("✅ ESP32 is now discoverable and connectable");
}

void loop() {
  // Send a test message every 5 seconds if connected
  if (deviceConnected) {
    String testMessage = "Hello from ESP32! Time: " + String(millis());
    pTxCharacteristic->setValue(testMessage.c_str());
    pTxCharacteristic->notify();
    Serial.println("Sent: " + testMessage);
    delay(5000);
  }
  
  // Restart advertising if disconnected
  if (!deviceConnected && oldDeviceConnected) {
    delay(500); // give the bluetooth stack time to get things ready
    pServer->startAdvertising(); // restart advertising
    Serial.println("Restarting advertising...");
    oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }
  
  delay(1000);
}