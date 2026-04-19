/*
  ESP32 - Button 5 and Buzzer
  When button 5 is pressed buzzer beeps
*/

#define BUTTON5 14
#define BUZZER  25

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

void beep(int duration = 200) {
  digitalWrite(BUZZER, HIGH);
  delay(duration);
  digitalWrite(BUZZER, LOW);
}

void setup() {
  Serial.begin(9600);
  pinMode(BUTTON5, INPUT_PULLUP);
  pinMode(BUZZER,  OUTPUT);
  digitalWrite(BUZZER, LOW);

  // startup beep
  beep(1000);
  Serial.println("Ready");
}

void loop() {
  if (digitalRead(BUTTON5) == LOW && debounce()) {
    Serial.println("BUTTON5 pressed - world description");
    beep(200);
  }
  delay(10);
}