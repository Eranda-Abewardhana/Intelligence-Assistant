// #include <SoftwareSerial.h>
#include <Servo.h>

// SoftwareSerial NodeMCU(2,3);

Servo servo_base, servo_1, servo_2, servo_grip;
int servoPos_Base, servoPos_grip, servoPos_1, servoPos_2;

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
int servoRelax = 0;

void setup() {
  Serial.begin(9600);
  // NodeMCU.begin(9600);

  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  servoPos_Base = 100;
  servoPos_1 = 78;
  servoPos_2 = 26;
  servoPos_grip = 55;
  
}

void loop() {

  if (Serial.available()) {
    String receivedString = Serial.readStringUntil('\n');
    
    int delimiterIndex;
    while ((delimiterIndex = receivedString.indexOf(',')) != -1) {
      String parameter = receivedString.substring(0, delimiterIndex);

      int colonIndex = parameter.indexOf(':');
      String paramName = parameter.substring(0, colonIndex);
      String paramValue = parameter.substring(colonIndex + 1);
      
      int intValue = paramValue.toInt();

      Serial.print(paramName + " : ");
      Serial.println(intValue);

      if(paramName == "m_stop"){
        stopVal = intValue;
      }
      else if(paramName == "m_init"){
        initSpeed = intValue;
      }
      else if(paramName == "mx_err"){
        X_errFunction(intValue);
      }
      else if(paramName == "my_err"){
        ;
      }
      else if(paramName == "servo_relax"){
        servoRelax = intValue;
        if (servoRelax == 1){
          Serial.println("Servo relax");
          servo_base.detach();
          servo_1.detach();
          servo_2.detach();
          servo_grip.detach();
        }
      }
      else if(paramName == "servo_base" && paramValue != "" && servoRelax!=1){
        response += "servo_base : " + String(intValue) + ", ";

        servo_base.attach(4);

        if(intValue >= 0){
          while(intValue >= 0){
            servoPos_Base += 1;
            intValue -= 1;
            servo_base.write(servoPos_Base);
            delay(15);
          }
        }else{
          while(intValue < 0){
            servoPos_Base -= 1;
            intValue += 1;
            servo_base.write(servoPos_Base);
            delay(15);
          }
        }

        // servo_base.write(100);
        // servo_grip.write(0);
        // servo_1.write(80);
        // servo_2.write(50);

      }
      else if(paramName == "servo_grip" && paramValue != "" && servoRelax!=1){
        response += "servo_grip : " + String(intValue) + ", ";
        
        servo_grip.attach(5);

        if(servoPos_grip < intValue){
          for (int pos = servoPos_grip; pos <= intValue; pos += 1) {
            servo_grip.write(pos);
            delay(20);
          }
        }else{
          for (int pos = servoPos_grip; pos >= intValue; pos -= 1) {
            servo_grip.write(pos);
            delay(20);
          }
        }
        servoPos_grip = intValue;

      }
      else if(paramName == "servo_1" && paramValue != "" && servoRelax!=1){
        response += "servo_1 : " + String(intValue) + ", ";
        
        servo_1.attach(6);

        if(intValue >= 0){
          while(intValue >= 0){
            servoPos_1 += 1;
            intValue -= 1;
            servo_1.write(servoPos_1);
            delay(25);
          }
        }else{
          while(intValue < 0){
            servoPos_1 -= 1;
            intValue += 1;
            servo_1.write(servoPos_1);
            delay(25);
          }
        }

      }
      else if(paramName == "servo_2" && paramValue != "" && servoRelax!=1){
        response += "servo_2 : " + String(intValue) + ", ";
        
        servo_2.attach(7);

        if(intValue >= 0){
          while(intValue >= 0){
            servoPos_2 += 1;
            intValue -= 1;
            servo_2.write(servoPos_2);
            delay(25);
          }
        }else{
          while(intValue < 0){
            servoPos_2 -= 1;
            intValue += 1;
            servo_2.write(servoPos_2);
            delay(25);
          }
        }
        
      }

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
      // NodeMCU.println(response);
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
