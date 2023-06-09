
#include <SoftwareSerial.h>

SoftwareSerial SerialRoom(2,3);



String voice="";
String voiceHistory="";

////////////////////////
int LM1 = 11;         ///
int LM2 = 12;         ///
int LO = 13;         ///
////////////////////////

void setup() {
  Serial.begin(9600);
  SerialRoom.begin(9600);
  pinMode(LM1,OUTPUT);
  pinMode(LM2,OUTPUT);
  pinMode(LO,OUTPUT);
}

void loop() {
  while(SerialRoom.available()) {
      delay(10);
      char c = (char)SerialRoom.read();
      if(c==' '){break; }
      voice += c;
  }
  if (voice.length() > 0) {
    if (voiceHistory == "on" && voice == "light1"){
        digitalWrite(LM1,HIGH);
    }
    if (voiceHistory == "off" && voice == "light1"){
        digitalWrite(LM1,LOW);
    }
    if (voiceHistory == "on" && voice == "light2"){
        digitalWrite(LM2,HIGH);
    }
    if (voiceHistory == "off" && voice == "light2"){
        digitalWrite(LM2,LOW);
    }
    if (voiceHistory == "on" && voice == "lightOut"){
        digitalWrite(LO,HIGH);
    }
    if (voiceHistory == "off" && voice == "lightOut"){
        digitalWrite(LO,LOW);
    }
    voiceHistory = voice;
    voice = "";
  }
}
