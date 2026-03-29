#define TRIGGER 4
#define BUTTON1 5
#define BUTTON2 18
#define BUTTON3 19
#define BUTTON4 21
#define BUTTON5 22


void setup() {
  // begin serial communication
  Serial.begin(9600);
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
