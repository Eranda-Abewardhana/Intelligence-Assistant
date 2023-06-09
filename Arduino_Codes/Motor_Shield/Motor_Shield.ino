#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 

Adafruit_DCMotor *myMotor1 = AFMS.getMotor(3);
Adafruit_DCMotor *myMotor2 = AFMS.getMotor(4);


int encoderPin1 = 10; //Encoder Output 'A' must connected with intreput pin of arduino.
int encoderPin2 = 11; //Encoder Otput 'B' must connected with intreput pin of arduino.
volatile int lastEncoded = 0; // Here updated value of encoder store.
volatile long encoderValue = 0; // Raw encoder value


void setup() {

	AFMS.begin();

  Serial.begin(9600); //initialize serial comunication

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

for (int i = 0; i <= 255; i++){
	myMotor2->setSpeed(i);
	myMotor2->run(FORWARD);
	myMotor1->setSpeed(i);
	myMotor1->run(FORWARD);
  // myMotor2->RELEASE();
  Serial.print("Forward  ");
  Serial.println(encoderValue);
  delay(1);

}

delay(1000);

for (int i = 0; i <= 255; i++){
	myMotor2->setSpeed(i);
	myMotor2->run(BACKWARD);
	myMotor1->setSpeed(i);
	myMotor1->run(BACKWARD);
  Serial.print("Reverse  ");
  Serial.println(encoderValue);
  delay(1);
}

delay(1000);

} 

void updateEncoder(){
  int MSB = digitalRead(encoderPin1); //MSB = most significant bit
  int LSB = digitalRead(encoderPin2); //LSB = least significant bit

  int encoded = (MSB << 1) |LSB; //converting the 2 pin value to single number
  int sum  = (lastEncoded << 2) | encoded; //adding it to the previous encoded value

  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderValue --;
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderValue ++;

  lastEncoded = encoded; //store this value for next time

}