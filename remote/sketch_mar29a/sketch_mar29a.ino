/*
  ESP32 Remote - BLE Button Transmitter
  Working version
*/

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
#define TRIGGER  4   // ok / confirm button
#define BUTTON1  5   // active path navigation
#define BUTTON2  18  // face registration and recognition
#define BUTTON3  13  // currency identification
#define BUTTON4  32  // text-to-speech
#define BUTTON5  14  // world description

#define LED_RED   26  // red led
#define LED_GREEN 27  // green led
#define BUZZER    25  // buzzer
// ─────────────────────────────────────────────────────────────────────────────

// ── BLE ───────────────────────────────────────────────────────────────────────
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "abcd1234-ab12-ab12-ab12-abcdef123456"

BLECharacteristic *pCharacteristic;
bool deviceConnected     = false;
bool wasConnected        = false;
// ─────────────────────────────────────────────────────────────────────────────

// ── DEBOUNCE ──────────────────────────────────────────────────────────────────
unsigned long lastPressTime = 0;
#define DEBOUNCE_MS 300

bool debounce() {
  unsigned long now = millis();
  if (now - lastPressTime > DEBOUNCE_MS) {
    lastPressTime = now;
    return true;
  }
  return false;
}
// ─────────────────────────────────────────────────────────────────────────────

// ── BUZZER ────────────────────────────────────────────────────────────────────
void beep(int duration = 200) {
  digitalWrite(BUZZER, HIGH);
  delay(duration);
  digitalWrite(BUZZER, LOW);
}

void longBeep() {
  digitalWrite(BUZZER, HIGH);
  delay(1000);
  digitalWrite(BUZZER, LOW);
}
// ─────────────────────────────────────────────────────────────────────────────

// ── BLE CALLBACKS ─────────────────────────────────────────────────────────────
class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("Pi connected");
  }
  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("Pi disconnected");
  }
};
// ─────────────────────────────────────────────────────────────────────────────

// ── SEND ──────────────────────────────────────────────────────────────────────
void sendSignal(const char* signal) {
  if (deviceConnected) {
    pCharacteristic->setValue(signal);
    pCharacteristic->notify();
    Serial.print("Sent: ");
    Serial.println(signal);
    beep(100);
  } else {
    Serial.println("Pi not connected");
  }
}
// ─────────────────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(9600);

  // ── BUTTONS ───────────────────────────────────────────────────────────────
  pinMode(TRIGGER, INPUT_PULLUP);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  pinMode(BUTTON3, INPUT_PULLUP);
  pinMode(BUTTON4, INPUT_PULLUP);
  pinMode(BUTTON5, INPUT_PULLUP);
  // ─────────────────────────────────────────────────────────────────────────

  // ── LEDS + BUZZER ─────────────────────────────────────────────────────────
  pinMode(LED_RED,   OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER,    OUTPUT);

  digitalWrite(LED_RED,   HIGH);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(BUZZER,    LOW);

  longBeep();
  // ─────────────────────────────────────────────────────────────────────────

  // ── BLE INIT ──────────────────────────────────────────────────────────────
  BLEDevice::init("Assistive-Glasses-Remote");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  BLEDevice::startAdvertising();

  Serial.println("BLE started - waiting for Pi...");
  // ─────────────────────────────────────────────────────────────────────────
}

void loop() {
  // ── LED STATUS ────────────────────────────────────────────────────────────
  if (deviceConnected) {
    digitalWrite(LED_RED,   LOW);
    digitalWrite(LED_GREEN, HIGH);
  } else {
    digitalWrite(LED_RED,   HIGH);
    digitalWrite(LED_GREEN, LOW);
  }
  // ─────────────────────────────────────────────────────────────────────────

  // ── RESTART ADVERTISING AFTER DISCONNECT ──────────────────────────────────
  if (!deviceConnected && wasConnected) {
    delay(500);
    BLEDevice::startAdvertising();
    wasConnected = false;
    Serial.println("Restarting advertising...");
  }
  if (deviceConnected && !wasConnected) {
    wasConnected = true;
  }
  // ─────────────────────────────────────────────────────────────────────────

  // ── BUTTONS ───────────────────────────────────────────────────────────────
  if (digitalRead(TRIGGER) == LOW && debounce()) {
    sendSignal("TRIGGER");
  }
  else if (digitalRead(BUTTON1) == LOW && debounce()) {
    sendSignal("BUTTON1");
  }
  else if (digitalRead(BUTTON2) == LOW && debounce()) {
    sendSignal("BUTTON2");
  }
  else if (digitalRead(BUTTON3) == LOW && debounce()) {
    sendSignal("BUTTON3");
  }
  else if (digitalRead(BUTTON4) == LOW && debounce()) {
    sendSignal("BUTTON4");
  }
  else if (digitalRead(BUTTON5) == LOW && debounce()) {
    sendSignal("BUTTON5"); 
  }
  // ─────────────────────────────────────────────────────────────────────————

  delay(10);
}