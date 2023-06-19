#include <SoftwareSerial.h>
#include <Servo.h>

SoftwareSerial NodeMCU(2,3);

Servo servo_base;
Servo servo_1;
Servo servo_2;
Servo servo_grip;

int enA = 10;
int in1 = A2; // L F
int in2 = A3; // L B

int enB = 11;
int in3 = A4; // R F
int in4 = A5; // R B

String response = "";

int trig = 8;
int echo = 9;
int initSpeed = 0;

int stopVal = 0;

void setup() {
  Serial.begin(9600);
  NodeMCU.begin(9600);

  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  // servo_base.attach(4);
  // servo_grip.attach(5);
  // servo_1.attach(6);
  // servo_2.attach(7);

  // servo_base.write(110);
  // servo_grip.write(0);
  // servo_1.write(80);
  // servo_2.write(50);
}

void loop() {

  if (NodeMCU.available()) {
    String receivedString = NodeMCU.readStringUntil('\n');
    
    int delimiterIndex;
    while ((delimiterIndex = receivedString.indexOf(',')) != -1) {
      String parameter = receivedString.substring(0, delimiterIndex);

      int colonIndex = parameter.indexOf(':');
      String paramName = parameter.substring(0, colonIndex);
      String paramValue = parameter.substring(colonIndex + 1);
      
      int intValue = paramValue.toInt();

      Serial.print(paramName + " : ");
      Serial.println(intValue);

      if(paramName == "stop"){
        stopVal = intValue;
      }
      else if(paramName == "m_init"){
        initSpeed = intValue;
      }
      else if(paramName == "x_err"){
        X_errFunction(intValue);
      }
      else if(paramName == "y_err"){
        ;
      }
      // else if(paramName == "servo_base" && paramValue != "" ){
      //   response += "servo_base : " + String(intValue) + ", ";
      //   servo_base.write(intValue);
      // }
      // else if(paramName == "servo_grip" && paramValue != "" ){
      //   response += "servo_grip : " + String(intValue) + ", ";
      //   servo_grip.write(intValue);
      // }
      // else if(paramName == "servo_1" && paramValue != "" ){
      //   response += "servo_1 : " + String(intValue) + ", ";
      //   servo_1.write(intValue);
      // }
      // else if(paramName == "servo_2" && paramValue != "" ){
      //   response += "servo_2 : " + String(intValue) + ", ";
      //   servo_2.write(intValue);
      // }

      receivedString = receivedString.substring(delimiterIndex + 1);
    }
  }

}

void X_errFunction(int error){
    // digitalWrite(trig,LOW);
    // delayMicroseconds(2);
    // digitalWrite(trig,HIGH);
    // delayMicroseconds(2);

    // long t      = pulseIn(echo,HIGH);
    // long inches = t / 74 / 2;
    // long cm = t / 29 / 2;  

    // if(cm > 30) {        
    // Apply output to motors

      if (stopVal==1){
        analogWrite(enA, 0);
        analogWrite(enB, 0);
        response += "Stopped !";
      } else {
        int newError = constrain(error, -1000, 1000);
        int motorVal = map(newError, -1000, 1000, -250, 250);

        if( abs(motorVal) >= initSpeed ){
          if( motorVal >= 0 ){
            motorControl('R', 'B', motorVal-initSpeed);
            motorControl('L', 'F', motorVal+initSpeed);
          }else{
            motorControl('L', 'B', -motorVal-initSpeed);
            motorControl('R', 'F', -motorVal+initSpeed);
          }
        }else{
          motorControl('R', 'F', -motorVal+initSpeed);
          motorControl('L', 'F', motorVal+initSpeed);
        }
        
      }
      NodeMCU.println(response);
      Serial.println(response);
      response = "";
      // Serial.println("Distance in inch : "+inches);
      // Serial.println("Distance in cm : "+cm);
    // }
    
}

void motorControl(char pos, char dir, int speed){
  speed = constrain(speed, 0, 255);
  response += "  | " + String(pos) + " " + String(dir) + " : " + String(speed);
  if( pos == 'R' ){
    analogWrite(11, speed);
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
    if( dir == 'F' )
      digitalWrite(in3, HIGH);
    else if( dir == 'B' )
      digitalWrite(in4, HIGH);
  }
  else if( pos == 'L' ){
    analogWrite(10, speed);
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    if( dir == 'F' )
      digitalWrite(in1, HIGH);
    else if( dir == 'B' )
      digitalWrite(in2, HIGH);
  }
}
