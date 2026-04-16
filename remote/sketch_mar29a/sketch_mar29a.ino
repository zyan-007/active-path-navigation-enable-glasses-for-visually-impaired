/*
  ESP32 Remote - Classic Bluetooth RFCOMM
  Simple serial over Bluetooth to Raspberry Pi
*/

#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

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

// ── SEND SIGNAL ───────────────────────────────────────────────────────────────
void sendSignal(const char* signal) {
  if (SerialBT.connected()) {
    SerialBT.println(signal);
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

  // ── BUTTON PINS ───────────────────────────────────────────────────────────
  pinMode(TRIGGER, INPUT_PULLUP);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  pinMode(BUTTON3, INPUT_PULLUP);
  pinMode(BUTTON4, INPUT_PULLUP);
  pinMode(BUTTON5, INPUT_PULLUP);
  // ─────────────────────────────────────────────────────────────────────────

  // ── LED + BUZZER ──────────────────────────────────────────────────────────
  pinMode(LED_RED,   OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER,    OUTPUT);

  digitalWrite(LED_RED,   HIGH);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(BUZZER,    LOW);

  longBeep();
  // ─────────────────────────────────────────────────────────────────────────

  // ── BLUETOOTH INIT ────────────────────────────────────────────────────────
  SerialBT.begin("Assistive-Glasses-Remote");
  Serial.println("Bluetooth started - waiting for Pi...");
  // ─────────────────────────────────────────────────────────────────────────
}

void loop() {
  // ── UPDATE LEDS BASED ON CONNECTION ───────────────────────────────────────
  if (SerialBT.connected()) {
    digitalWrite(LED_RED,   LOW);
    digitalWrite(LED_GREEN, HIGH);
  } else {
    digitalWrite(LED_RED,   HIGH);
    digitalWrite(LED_GREEN, LOW);
  }
  // ─────────────────────────────────────────────────────────────────────────

  // ── READ BUTTONS ──────────────────────────────────────────────────────────
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
  // ─────────────────────────────────────────────────────────────────────────

  delay(10);
}