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
int initSpeed = 40; // Desired motor speed
int measuredSpeed = 0;
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
  if (voice.length() > 0) {
      int get = voice.indexOf(":");
      String data1 = voice.substring(0,get);
      String data2 = voice.substring(get+1, voice.length());
      Serial.println(data1);
      Serial.println(data2);
    //   if (voiceHistory == "on" && voice == "light1"){
    //       digitalWrite(LM1,HIGH);
    //   }
    voiceHistory = voice;
    voice = "";
    long error = atol(data2.c_str());
    function(data1,error);
  }
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
  if(x == "err"){
    // digitalWrite(trig,LOW);
    // delayMicroseconds(2);
    // digitalWrite(trig,HIGH);
    // delayMicroseconds(2);

    // long t      = pulseIn(echo,HIGH);
    // long inches = t / 74 / 2;
    // long cm = t / 29 / 2;  

    // if(cm > 30) {        
    // Apply output to motors

      int newError = constrain(error, -1000, 1000);
      int motorVal = map(newError, -1000, 1000, -250, 250);

      if(motorVal<0){
        motorControl('l', motorVal);
        motorControl('r', -motorVal);
      }else{
        motorControl('l', motorVal);
        motorControl('r', -motorVal);
      }

      // Serial.println("Distance in inch : "+inches);
      // Serial.println("Distance in cm : "+cm);
    // }
    
  }
}

void motorControl(char motor, int speed){
  int finalSpeed = speed + initSpeed;
  if(finalSpeed>0){
    int motorSpeed = constrain(finalSpeed, 0, 255);
    if(motor == 'l'){
      // myMotor2->setSpeed(motorSpeed);
      // myMotor2->run(FORWARD);
      Serial.print("Motor Left F : ");
      Serial.println(motorSpeed);
    }else if(motor == 'r'){
      // myMotor1->setSpeed(motorSpeed);
      // myMotor1->run(FORWARD);
      Serial.print("Motor Right F : ");
      Serial.println(motorSpeed);
    }
  }else{
    finalSpeed = -finalSpeed;
    int motorSpeed = constrain(finalSpeed, 0, 255);
    if(motor == 'l'){
      // myMotor2->setSpeed(motorSpeed);
      // myMotor2->run(BACKWARD);
      Serial.print("Motor Left B : ");
      Serial.println(motorSpeed);
    }else if(motor == 'r'){
      // myMotor1->setSpeed(motorSpeed);
      // myMotor1->run(BACKWARD);
      Serial.print("Motor Right B : ");
      Serial.println(motorSpeed);
    }
  }
}
