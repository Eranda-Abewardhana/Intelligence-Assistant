#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

SoftwareSerial SerialRoom(2,3);
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 

Adafruit_DCMotor *myMotor1 = AFMS.getMotor(3);
Adafruit_DCMotor *myMotor2 = AFMS.getMotor(4);


int encoderPin1 = 10; //Encoder Output 'A' must connected with intreput pin of arduino.
int encoderPin2 = 11; //Encoder Otput 'B' must connected with intreput pin of arduino.
volatile int lastEncoded = 0; // Here updated value of encoder store.
volatile long encoderValue = 0; // Raw encoder value
int trig = 2;
int echo = 4;
double targetSpeed = 150.0; // Desired motor speed
double measuredSpeed = 0.0; // Measured motor speed
String voice="";
String voiceHistory="";
long error = 0;

void setup() {
	AFMS.begin();
  Serial.begin(9600);
  SerialRoom.begin(9600);

  pinMode(encoderPin1, INPUT_PULLUP); 
  pinMode(encoderPin2, INPUT_PULLUP);

  digitalWrite(encoderPin1, HIGH); //turn pullup resistor on
  digitalWrite(encoderPin2, HIGH); //turn pullup resistor on

  //call updateEncoder() when any high/low changed seen
  //on interrupt 0 (pin 2), or interrupt 1 (pin 3) 
  attachInterrupt(0, updateEncoder, CHANGE); 
  attachInterrupt(1, updateEncoder, CHANGE);
}

void loop() {
  while(SerialRoom.available()) {
      delay(10);
      char c = (char)SerialRoom.read();
      voice += c;
  }
    int get = voice.indexOf(":");
    String data1 = voice.substring(1,get);
    String data2 = voice.substring(get+1, voice.length());
    Serial.println(data1);
    Serial.println(data2);
  // if (voice.length() > 0) {
  //   if (voiceHistory == "on" && voice == "light1"){
  //       digitalWrite(LM1,HIGH);
  //   }
  //   Serial.println(voice);
  //   voiceHistory = voice;
  //   voice = "";
  // }
  long error = atol(data2.c_str());
   function(data1,error);

  delay(100);
}

void updateEncoder() {
  int MSB = digitalRead(encoderPin1);
  int LSB = digitalRead(encoderPin2);
  int encoded = (MSB << 1) | LSB;
  int sum = (lastEncoded << 2) | encoded;

  if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
    encoderValue--;
  if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
    encoderValue++;

  lastEncoded = encoded;

  // Calculate the measured speed based on the encoder value
  measuredSpeed = (encoderValue * 60.0) / 64.0;
}


void function(String x,long error){
  if(x == "m"){

    digitalWrite(trig,LOW);
    delayMicroseconds(2);
    digitalWrite(trig,HIGH);
    delayMicroseconds(2);

    long t      = pulseIn(echo,HIGH);
    long inches = t / 74 / 2;
    long cm = t / 29 / 2;  

    if(cm > 30) {        
    // Apply output to motors
    int motorSpeed = constrain(error, -105, 105);
    myMotor2->setSpeed(targetSpeed + motorSpeed);
    myMotor2->run(FORWARD);
    myMotor1->setSpeed(targetSpeed - motorSpeed);
    myMotor1->run(FORWARD);

    Serial.print("Target Speed Left : ");
    Serial.print(targetSpeed + motorSpeed);
    Serial.print(", Measured Speed Right : ");
    Serial.print(targetSpeed - motorSpeed);
    Serial.println("Distance in inch : "+inches);
    Serial.println("Distance in cm : "+cm);
    }
    
  }
}
