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
  if (digitalRead(4) == HIGH){
    Serial.println("YES");
  }
  else{
    Serial.println("NO");
  }
  delay(100);
}
