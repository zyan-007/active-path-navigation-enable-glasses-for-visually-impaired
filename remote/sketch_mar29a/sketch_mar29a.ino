/*
  ESP32 Remote - Button Test
  Press any button - serial monitor shows which one
*/

// ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
#define TRIGGER  4   // ok / confirm button
#define BUTTON1  5   // active path navigation
#define BUTTON2  18  // face registration and recognition
#define BUTTON3  13  // currency identification
#define BUTTON4  32  // text-to-speech
#define BUTTON5  14  // world description
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

void setup() {
  Serial.begin(9600);

  pinMode(TRIGGER, INPUT_PULLUP);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  pinMode(BUTTON3, INPUT_PULLUP);
  pinMode(BUTTON4, INPUT_PULLUP);
  pinMode(BUTTON5, INPUT_PULLUP);

  Serial.println("Button test ready - press any button");
}

void loop() {
  if (digitalRead(TRIGGER) == LOW && debounce()) {
    Serial.println("TRIGGER pressed - ok / confirm");
  }
  else if (digitalRead(BUTTON1) == LOW && debounce()) {
    Serial.println("BUTTON1 pressed - active path navigation");
  }
  else if (digitalRead(BUTTON2) == LOW && debounce()) {
    Serial.println("BUTTON2 pressed - face registration and recognition");
  }
  else if (digitalRead(BUTTON3) == LOW && debounce()) {
    Serial.println("BUTTON3 pressed - currency identification");
  }
  else if (digitalRead(BUTTON4) == LOW && debounce()) {
    Serial.println("BUTTON4 pressed - text-to-speech");
  }
  else if (digitalRead(BUTTON5) == LOW && debounce()) {
    Serial.println("BUTTON5 pressed - world description");
  }

  delay(10);
}