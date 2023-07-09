#include <SoftwareSerial.h>

String state; // String to store incoming message from Bluetooth

void setup() {
  Serial3.begin(9600); // Bluetooth serial communication will happen on pins 2 and 3
  Serial.begin(9600); // Serial communication to check the data on the Serial Monitor
  pinMode(13, OUTPUT); // LED connected to pin 13
}

void loop() {
      while (Serial3.available()){
        delay(10);
        char c = Serial3.read();
        state += c;
      }

  if (state.length() > 0) 
  {
    Serial.println(state);

    // Check if the word "bottle" is present in the received string
    if (state.indexOf("bottle") != -1) {
      Serial.println("bottle");
      // Execute your code here if "bottle" is found
    }
    
    else if (state.indexOf("watch") != -1) {
      Serial.println("watch");
      // Execute your code here if "watch" is found
    } 

    else if (state.indexOf("medicine") != -1) {
      Serial.println("medicine");
      // Execute your code here if "medicine" is found
    } 

    else if (state.indexOf("lipstick") != -1) {
      Serial.println("lipstick");
      // Execute your code here if "lipstick" is found
    } 

     //else { }
  

    state = "";
  }
}
