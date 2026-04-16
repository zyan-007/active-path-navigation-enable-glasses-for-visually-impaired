/*
  ESP32 Remote - BLE Button Transmitter
  Sends button press over BLE to Raspberry Pi automatically
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

#define LED_RED   26  // red led  - not connected
#define LED_GREEN 27  // green led - connected to pi
#define BUZZER    25  // buzzer
// ─────────────────────────────────────────────────────────────────────────────

// ── BLE DEFINITIONS ───────────────────────────────────────────────────────────
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "abcd1234-ab12-ab12-ab12-abcdef123456"

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;
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

// ── BUZZER HELPERS ────────────────────────────────────────────────────────────
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

// ── BLE CONNECTION CALLBACKS ──────────────────────────────────────────────────
class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    digitalWrite(LED_RED,   LOW);
    digitalWrite(LED_GREEN, HIGH);
    longBeep();  // long beep on connection
    Serial.println("Pi Connected");
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED,   HIGH);
    beep(500);  // short beep on disconnection
    Serial.println("Pi Disconnected - restarting advertising");
    BLEDevice::startAdvertising();  // auto reconnect
  }
};
// ─────────────────────────────────────────────────────────────────────────────

// ── SEND SIGNAL OVER BLE ──────────────────────────────────────────────────────
void sendSignal(const char* signal) {
  if (deviceConnected) {
    pCharacteristic->setValue(signal);
    pCharacteristic->notify();
    Serial.print("Sent: ");
    Serial.println(signal);
    beep(100);  // short beep on button press
  } else {
    Serial.println("Not connected to Pi");
  }
}
// ─────────────────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(9600);

  // ── BUTTON PINS ───────────────────────────────────────────────────────────
  pinMode(TRIGGER, INPUT_PULLUP);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  pinMode(BUTTON3, INPUT_PULLUP);
  pinMode(BUTTON4, INPUT_PULLUP);
  pinMode(BUTTON5, INPUT_PULLUP);
  // ─────────────────────────────────────────────────────────────────────────

  // ── LED + BUZZER PINS ─────────────────────────────────────────────────────
  pinMode(LED_RED,   OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER,    OUTPUT);

  digitalWrite(LED_RED,   HIGH);  // red on at startup
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(BUZZER,    LOW);

  longBeep();  // startup beep
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
  BLEDevice::startAdvertising();

  Serial.println("BLE started - waiting for Pi...");
  // ─────────────────────────────────────────────────────────────────────────
}

void loop() {
  // INPUT_PULLUP - pressed = LOW
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

  delay(10);
}