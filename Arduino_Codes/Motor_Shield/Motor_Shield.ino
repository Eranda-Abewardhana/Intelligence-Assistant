#include <Servo.h>
#include <util/atomic.h>

Servo servo_base, servo_1, servo_2, servo_grip;
int servoPos_Base, servoPos_grip, servoPos_1, servoPos_2;

// Pin definitions for ultrasonic
const int trigPin = 13;
const int echoPin = 12;

// Variables
long duration;
int distance;

#define C1 2 // YELLOW
#define C2 3 // GREEN
#define enA 10 //PWN1
#define in1 A2 // L F
#define in2 A3 // L B

#define C3 4 // YELLOW
#define C4 5 // GREEN
#define enB 11//PWN2
#define in3 A4 // R F
#define in4 A5 // R B

// set target position
int target1[5][3] = {{900, 0, 0.4}, {0, 200, 0.6}, {-900, 0, 0.5}, {0, 200, 0.6}, {0, 0, 0}};


volatile int posi[] = {0,0};
long prevT = 0;
float eprev[] = {0,0};
float eintegral[] = {0,0};
int m1pos=0;
int m2pos=0;

float kp[] = {3, 3};
float kd[] = {0.45, 0.45};
float ki[] = {0.001, 0.001};

String response = "";

int trig = 8;
int echo = 9;
int initSpeed = 0;

int stopVal = 0;
int servoRelax = 0;
int i = 0;
int x = 100;

void setMotorPos(int dir, int pwmVal, int pwm, int in1, int in2){
  analogWrite(pwm,pwmVal);
  if(dir == 1){
    digitalWrite(in1,HIGH);
    digitalWrite(in2,LOW);
    delay(1000);
  }
  else if(dir == -1){
    digitalWrite(in1,LOW);
    digitalWrite(in2,HIGH);
    delay(1000);
  }
  else{
    digitalWrite(in1,LOW);
    digitalWrite(in2,LOW);
  }  
}

void setup() {
  Serial.begin(9600);

   // Define pin modes
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(C1,INPUT);
  pinMode(C2,INPUT);
  attachInterrupt(digitalPinToInterrupt(C1),readEncoder1,RISING);
  
  pinMode(C3,INPUT);
  pinMode(C4,INPUT);
  attachInterrupt(digitalPinToInterrupt(C3),readEncoder2,RISING);
  
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

    // Clear the trigger pin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Set the trigger pin high for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Measure the duration of the echo pulse
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance in centimeters
  distance = duration * 0.034 / 2;

  //  Print the distance
  Serial.print("distance(cm): "+ distance);
  Serial.print(distance);

  // if(distance < 20 && i < 5 && (-2 < x < 2)) {
  // int* target = target1[i];
  // m1pos = target[0];
  // m2pos = target[1];
  // Serial.println(String(m1pos));
  // Serial.println(String(m2pos));
  // i++;
  // }

  if (Serial.available()) {
    String receivedString = Serial.readStringUntil('\n');
    
    int delimiterIndex;
    while ((delimiterIndex = receivedString.indexOf(':')) != -1) {
      String parameter = receivedString.substring(0, delimiterIndex);
      
      int colonIndex = parameter.indexOf(':');
      String paramName = parameter.substring(0, colonIndex);
      String paramValue = parameter.substring(colonIndex + 1);

       if(paramName.indexOf('/')) != -1) {
        int colonIndex = parameter.indexOf('/');
        String param1 = parameter.substring(0, colonIndex);
        String param2 = parameter.substring(colonIndex + 1);
      }
       if(paramValue.indexOf(',')) != -1) {
        int colonIndex = parameter.indexOf('/');
        int value1 = parameter.substring(0, colonIndex).toInt();
        int value2 = parameter.substring(colonIndex + 1).toInt();
      }
      
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
        x = intValue;
      }
      else if(param1 == "m1_pos"){
        m1pos = value1;
      }
      else if(param2 == "m2_pos"){
        m2pos = value2;
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

  // time difference
  long currT = micros();
  float deltaT = ((float) (currT - prevT))/( 1.0e6 );
  prevT = currT;

  int pos[] = {0,0}; 
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    pos[0] = posi[0];
    pos[1] = posi[1];
  }

  // error
  int e1 = pos[0] - m1pos;
  int e2 = pos[1] - m2pos;

  // derivative
  float dedt1 = (e1-eprev[0])/(deltaT);
  float dedt2 = (e2-eprev[1])/(deltaT);

  // integral
  eintegral[0] = eintegral[0] + e1*deltaT;
  eintegral[1] = eintegral[1] + e1*deltaT;

  // control signal
  float u1 = kp[0]*e1 + kd[0]*dedt1 + ki[0]*eintegral[0];
  float u2 = kp[1]*e2 + kd[1]*dedt2 + ki[1]*eintegral[1];

  // motor power
  float pwr1 = fabs(u1);
  pwr1 = constrain(pwr1, 0, 255);
  float pwr2 = fabs(u2);
  pwr2 = constrain(pwr2, 0, 255);

  setMotorPos( u1<0 ? -1: 1,pwr1,enA,in1,in2);
  setMotorPos( u2<0 ? -1: 1,pwr2,enB,in3,in4);

  // store previous error
  eprev[0] = e1;
  eprev[1] = e2;
}

void X_errFunction(int error){
   
 
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

void readEncoder1(){
  int b = digitalRead(C2);
  if(b > 0){
    posi[0]++;
  }
  else{
    posi[0]--;
  }
}
void readEncoder2(){
  int b = digitalRead(C4);
  if(b > 0){
    posi[1]++;
  }
  else{
    posi[1]--;
  }
}
