#define TRIGGER 4
#define BUTTON1 5
#define BUTTON2 18
#define BUTTON3 19
#define BUTTON4 21
#define BUTTON5 22


void setup() {
  // begin serial communication
  Serial.begin(9600);

  // setup input buttons
  pinMode(TRIGGER, INPUT_PULLUP);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  pinMode(BUTTON3, INPUT_PULLUP);
  pinMode(BUTTON4, INPUT_PULLUP);
  pinMode(BUTTON5, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (digitalRead(TRIGGER) == HIGH){
    Serial.println("Trigger pressed");
  }
  else if (digitalRead(BUTTON1) == HIGH){
    Serial.println("button1 pressed");
  }
  else if (digitalRead(BUTTON2) == HIGH){
    Serial.println("button2 pressed");
  }
  else if (digitalRead(BUTTON3) == HIGH){
    Serial.println("button3 pressed");
  }
  else if (digitalRead(BUTTON4) == HIGH){
    Serial.println("button4 pressed");
  }
  else if (digitalRead(BUTTON5) == HIGH){
    Serial.println("button5 pressed");
  }
  else{
    Serial.println("Nothing pressed");
  }
  delay(100);
}
