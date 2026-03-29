void setup() {
  // put your setup code here, to run once:
  pinMode(4, INPUT_PULLUP); // enable internal pull-up
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
