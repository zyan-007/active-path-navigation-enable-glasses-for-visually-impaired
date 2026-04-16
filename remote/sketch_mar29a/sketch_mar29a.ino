/*
  ESP32 Remote - WiFi Hotspot + TCP Server
  ESP32 creates hotspot, Pi connects to it
  Button presses sent to Pi over TCP socket
*/

#include <WiFi.h>

// ── HOTSPOT CREDENTIALS ───────────────────────────────────────────────────────
const char* AP_SSID     = "GlassesAP";
const char* AP_PASSWORD = "glasses123";
const int   PORT        = 8080;
// ─────────────────────────────────────────────────────────────────────────────

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

WiFiServer server(PORT);
WiFiClient client;

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
  if (client && client.connected()) {
    client.println(signal);
    Serial.print("Sent: ");
    Serial.println(signal);
    beep(100);  // short beep on button press
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

  // ── LED + BUZZER PINS ─────────────────────────────────────────────────────
  pinMode(LED_RED,   OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER,    OUTPUT);

  digitalWrite(LED_RED,   HIGH);  // red on at startup
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(BUZZER,    LOW);

  longBeep();  // startup beep
  // ─────────────────────────────────────────────────────────────────────────

  // ── START HOTSPOT ─────────────────────────────────────────────────────────
  Serial.println("Starting hotspot...");
  WiFi.softAP(AP_SSID, AP_PASSWORD);

  Serial.print("Hotspot IP: ");
  Serial.println(WiFi.softAPIP());  // always 192.168.4.1

  server.begin();
  Serial.println("Server started - waiting for Pi to connect...");
  // ─────────────────────────────────────────────────────────────────────────
}

void loop() {
  // ── CHECK FOR NEW CLIENT ──────────────────────────────────────────────────
  if (!client || !client.connected()) {
    client = server.available();

    if (client) {
      Serial.println("Pi connected!");
      digitalWrite(LED_RED,   LOW);   // red off
      digitalWrite(LED_GREEN, HIGH);  // green on
      longBeep();                     // long beep on connection
    } else {
      // no client connected - red on green off
      digitalWrite(LED_RED,   HIGH);
      digitalWrite(LED_GREEN, LOW);
    }
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