#define TRIGGER 4 // ok button
#define BUTTON1 5 // active path navigation
#define BUTTON2 18 // face registration and recognition
#define BUTTON3 19 // currency identification
#define BUTTON4 21 // text-to-speech 
#define BUTTON5 22 // world description


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

  if (digitalRead(TRIGGER) == HIGH){ // trigger "ok" button
    Serial.println("Trigger pressed");
  }
  else if (digitalRead(BUTTON1) == HIGH){ // button1 - active path navigation
    Serial.println("button1 pressed");
  }
  else if (digitalRead(BUTTON2) == HIGH){ // button2 - face registration
    Serial.println("button2 pressed");
  }
  else if (digitalRead(BUTTON3) == HIGH){ // button3 - currency identification
    Serial.println("button3 pressed");
  }
  else if (digitalRead(BUTTON4) == HIGH){ // button4 - test-to-speech
    Serial.println("button4 pressed");
  }
  else if (digitalRead(BUTTON5) == HIGH){ // button5 - world description (api call)
    Serial.println("button5 pressed");
  }
  else{ // nothing is pressed
    Serial.println("Nothing pressed");
  }
  delay(100); // delay of 100 ms
}
