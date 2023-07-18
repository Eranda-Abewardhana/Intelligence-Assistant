
#include<Servo.h>

Servo micro_servo;

int pos = 0;

const int servo_pin = 8;
const int trig_pin = 27;
const int echo_pin = 29;
const int trig_pin2 = 31;
const int echo_pin2 = 33;

float duration, distance;

void setup() {
  // put your setup code here, to run once:
  pinMode(servo_pin,OUTPUT);
  pinMode(trig_pin,OUTPUT);
  pinMode(echo_pin,INPUT);
  pinMode(trig_pin2,OUTPUT);
  pinMode(echo_pin2,INPUT);
  Serial.begin(9600);
  micro_servo.attach(servo_pin);
}

void loop() {
  // put your main code here, to run repeatedly:

  for(pos = 0;pos<=180; pos++)
  {
    read_ultrasonic_distance(pos);
    micro_servo.write(pos);
    delay(20);
  }
  for(pos = 180;pos >= 0; pos--)
  {
    read_ultrasonic_distance(pos);
    micro_servo.write(pos);
    delay(20);
  }
}


void read_ultrasonic_distance(int angle)
{
  digitalWrite(trig_pin, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin, LOW);

  duration = pulseIn(echo_pin, HIGH);
  distance = (duration * 0.0343)/2;
  Serial.print(angle);
  Serial.print(",");
  Serial.print(distance);

  digitalWrite(trig_pin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_pin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin2, LOW);

  duration = pulseIn(echo_pin2, HIGH);
  distance = (duration * 0.0343)/2;
  Serial.print(",");
  Serial.println(distance);
}

