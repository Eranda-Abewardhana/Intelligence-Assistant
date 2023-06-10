#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include <SoftwareSerial.h>

SoftwareSerial SerialRoom(2,3);

Adafruit_MotorShield AFMS = Adafruit_MotorShield();

String voice="";
String voiceHistory="";

Adafruit_DCMotor *myMotor1 = AFMS.getMotor(3);
Adafruit_DCMotor *myMotor2 = AFMS.getMotor(4); //Left 

int encoderPin1 = 10;
int encoderPin2 = 11;
volatile int lastEncoded = 0;
volatile long encoderValue = 0;
int trig = 2;
int echo = 4;

// PID constants
double kp = 0.1;  // Proportional gain
double ki = 0.05; // Integral gain
double kd = 0.01; // Derivative gain

double targetSpeed = 150.0; // Desired motor speed
double measuredSpeed = 0.0; // Measured motor speed

double errorSum = 0.0;       // Cumulative error
double lastError = 0.0;      // Last error
unsigned long lastTime = 0;  // Last time update occurred

void setup() {
  AFMS.begin();
  Serial.begin(9600);
  SerialRoom.begin(9600);
  pinMode(encoderPin1, INPUT_PULLUP);
  pinMode(encoderPin2, INPUT_PULLUP);
  pinMode(echo, OUTPUT);
  pinMode(trig, INPUT);
  digitalWrite(encoderPin1, HIGH);
  digitalWrite(encoderPin2, HIGH);
  attachInterrupt(0, updateEncoder, CHANGE);
  attachInterrupt(1, updateEncoder, CHANGE);
}

void loop() {

  while(SerialRoom.available()) {
      delay(10);
      char c = (char)SerialRoom.read();
      if(c==' '){break; }
      voice += c;
  }

  if (voice.length() > 0) {
  
    if (voiceHistory == "m1" && voice == "light1"){
        digitalWrite(LM1,HIGH);
    }
  
  }

  unsigned long currentTime = millis();
  double elapsedTime = (currentTime - lastTime) / 1000.0; // Convert to seconds

   // PID calculations
  if (Serial.available() > 0) {
    double errorx = Serial.parseFloat(); // Read the errorx value sent from Python
    errorSum += errorx * elapsedTime;
    double dError = (errorx - lastError) / elapsedTime;

    // PID output
    double output = kp * errorx + ki * errorSum + kd * dError;

    // Apply output to motors
    int motorSpeed = constrain(output, -105, 105);
    myMotor2->setSpeed(targetSpeed + motorSpeed); //Left
    myMotor2->run(FORWARD);
    myMotor1->setSpeed(targetSpeed + motorSpeed); //Right
    myMotor1->run(FORWARD);

    // Update variables for next iteration
    lastError = errorx;
    lastTime = currentTime;
  }

  digitalWrite(trig,LOW);
  delayMicroseconds(2);
  digitalWrite(trig,HIGH);
  delayMicroseconds(2);

  long t      = pulseIn(echo,HIGH);
  long inches = t / 74 / 2;
  long cm = t / 29 / 2;

  Serial.print("Target Speed Left : ");
  Serial.print(targetSpeed + motorSpeed);
  Serial.print(", Measured Speed Right : ");
  Serial.print(targetSpeed + motorSpeed);
  Serial.println("Distance in inch : "+inches);
  Serial.println("Distance in cm : "+cm);

  if(cm < 30) {
    break;
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
