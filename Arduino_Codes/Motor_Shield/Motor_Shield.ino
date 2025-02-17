#include <Servo.h>
#include <util/atomic.h>
#include <NewPing.h>

const int BUFFER_SIZE = 64;

char buffer[BUFFER_SIZE];
volatile int bufferIndex = 0;
bool newCommand = false;

Servo servo_base, servo_1, servo_2, servo_grip, servo_cam;
int servoPos_Base, servoPos_grip, servoPos_1, servoPos_2, servoPos_cam;
int servoPos_Base_temp=0, servoPos_1_temp=0, servoPos_2_temp=0;

const int TRIGGER_PIN = 23;
const int ECHO_PIN = 25;

String state;

NewPing sonar(TRIGGER_PIN, ECHO_PIN, 200);

#define buzzerLed 13 // YELLOW

#define C1 18 // YELLOW
#define C2 16 // GREEN
#define enA 11 //PWN1
#define in1 A2 // L F
#define in2 A3 // L B

#define C3 19 // YELLOW
#define C4 17 // GREEN
#define enB 10//PWN2
#define in3 A4 // R F
#define in4 A5 // R B


volatile int posi[] = {0,0};
long prevT = 0;
float eprev[] = {0,0};
float eintegral[] = {0,0};
int m1pos=0;
int m2pos=0;

float kp[] = {30, 30};
float kd[] = {2, 2};
float ki[] = {0, 0};

String response = "";

int initSpeed = 0;

int stopVal = 0;
int bluetooth = 0;
int servoRelax = 0;
int  buzzer = 0;

void setMotorPos(int dir, int pwmVal, int pwm, int in1, int in2){
  analogWrite(pwm,pwmVal);
  if(dir == 1){
    digitalWrite(in1,HIGH);
    digitalWrite(in2,LOW);
  }
  else if(dir == -1){
    digitalWrite(in1,LOW);
    digitalWrite(in2,HIGH);
  }
  else{
    digitalWrite(in1,LOW);
    digitalWrite(in2,LOW);
  }  
}

void setup() {
  Serial3.begin(9600); // Bluetooth serial communication will happen on pins 2 and 3
  Serial.begin(115200); // Serial communication to check the data on the Serial Monitor
  pinMode(buzzerLed, OUTPUT); // LED connected to pin 13

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

  servoPos_Base = 25;
  servoPos_1 = 120;
  servoPos_2 = 0;
  servoPos_grip = 0;
  servoPos_cam = 0;
   
  servoPos_1_temp = servoPos_1;
  servoPos_2_temp = servoPos_2;
  servoPos_Base_temp = servoPos_Base;
  
  servo_base.attach(4);
  servo_1.attach(6);
  servo_2.attach(7);
  servo_grip.attach(5);
  servo_cam.attach(8);
  
  servo_base.write(servoPos_Base*74/70);
  servo_1.write(servoPos_1*32/45);
  servo_2.write(servoPos_2*32/45);
  servo_grip.write(servoPos_grip);
  servo_cam.write(servoPos_cam*180/168);
}

void loop() {


  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n') {
      buffer[bufferIndex] = '\0'; // Null-terminate the buffer
      newCommand = true; // Set the flag to indicate a new message is ready
      bufferIndex = 0; // Reset buffer index for the next message
    } else {
      buffer[bufferIndex] = c;
      bufferIndex = (bufferIndex + 1) % BUFFER_SIZE; // Wrap around the buffer if needed
    }
  }

  if (newCommand) {
    String receivedString = String(buffer);
    int delimiterIndex;

    while ((delimiterIndex = receivedString.indexOf(',')) != -1) {
      String parameter = receivedString.substring(0, delimiterIndex);

      int colonIndex = parameter.indexOf(':');
      String paramName = parameter.substring(0, colonIndex);
      String paramValue = parameter.substring(colonIndex + 1);
      
      int intValue = paramValue.toInt();

      // Serial.print(paramName + " : ");
      // Serial.println(intValue);

      if(paramName == "m_stop"){
        stopVal = intValue;
      }
      else if(paramName == "m_init"){
        initSpeed = intValue;
      }
      else if(paramName == "mx_err"){
        X_errFunction(intValue);
      }
      else if(paramName == "m1_pos"){
        m1pos += intValue;
        response += "M1 pos : " + String(intValue) + ", ";
      }
      else if(paramName == "m2_pos"){
        m2pos += intValue;
        response += "M2 pos : " + String(intValue) + ", ";
      }
      else if(paramName == "my_err"){
        ;
      }
      else if(paramName == "bluetooth"){
        bluetooth = intValue;
        bluetooth();
      }
       else if(paramName == "buzzer"){
        buzzer = intValue;
        buzzer();
      }
      else if(paramName == "servo_relax"){
        servoRelax = intValue;
        if (servoRelax == 1){
          response += "Servo relax, ";
          servo_base.detach();
          servo_1.detach();
          servo_2.detach();
          servo_grip.detach();
        }
      }
      else if(paramName == "servo_relax_pos" && intValue == 1){
          response += "Servo relax Pos, ";

          servo_base.attach(4);
          servo_1.attach(6);
          servo_2.attach(7);
          servo_grip.attach(5);
          
          servo_base.write(100);
          servo_1.write(78);
          servo_2.write(26);
          servo_grip.write(0);
      }
      else if(paramName == "servo_base" && paramValue != "" && servoRelax!=1){
        int servoVal = constrain(intValue, 20, 160);
        servoPos_Base_temp = int(servoVal*74/70);
        response += "servo_base : " + String(servoVal) + ", ";
      }
      else if(paramName == "servo_grip" && paramValue != "" && servoRelax!=1){
        int servoVal = constrain(intValue, 0, 60);
        servo_grip.write(servoVal);
        response += "servo_grip : " + String(servoVal) + ", ";
      }
      else if(paramName == "servo_1" && paramValue != "" && servoRelax!=1){
        int servoVal = constrain(intValue, 0, 120);
        servoPos_1_temp = int((servoVal+10)*2/3);
        response += "servo_1 : " + String(servoVal) + ", ";
      }
      else if(paramName == "servo_2" && paramValue != "" && servoRelax!=1){
        int servoVal = constrain(intValue, 0, 145);
        servoPos_2_temp = int(servoVal*32/45);
        response += "servo_2 : " + String(servoVal) + ", ";
      }
      else if(paramName == "servo_cam" && paramValue != "" && servoRelax!=1){
        int servoVal = constrain(intValue, 0, 168);
        servo_cam.write(servoVal*180/168);
        response += "servo_cam : " + String(servoVal) + ", ";
      }
      else if(paramName == "distance" && paramValue != "" && servoRelax!=1){
        unsigned int distance = sonar.ping_cm();
        response += "Distance : " + String(distance) + ", ";
      }

      receivedString = receivedString.substring(delimiterIndex + 1);
    }
    
    Serial.println(response);
    response = "";
    newCommand = false;
  }

  if(servoPos_Base < servoPos_Base_temp){
    servoPos_Base+=1;
    servo_base.write(servoPos_Base);
    delay(20);
  }else if(servoPos_Base > servoPos_Base_temp){
    servoPos_Base-=1;
    servo_base.write(servoPos_Base);
    delay(20);
  }
  
  if(servoPos_1 < servoPos_1_temp){
    servoPos_1+=1;
    servo_1.write(servoPos_1);
    delay(10);
  }else if(servoPos_1 > servoPos_1_temp){
    servoPos_1-=1;
    servo_1.write(servoPos_1);
    delay(10);
  }

  // while(servoPos_2_temp > 0){
  //   servoPos_2 += 1;
  //   servoPos_2_temp -= 1;
  //   servo_2.write(servoPos_2);
  //   // delay(25);
  // }
  // while(servoPos_2_temp < 0){
  //   servoPos_2 -= 1;
  //   servoPos_2_temp += 1;
  //   servo_2.write(servoPos_2);
  //   // delay(25);
  // }
  
  if(servoPos_2 < servoPos_2_temp){
    servoPos_2+=1;
    servo_2.write(servoPos_2);
    delay(10);
  }else if(servoPos_2 > servoPos_2_temp){
    servoPos_2-=1;
    servo_2.write(servoPos_2);
    delay(10);
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
  eintegral[1] = eintegral[1] + e2*deltaT;

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
      Serial.println(response);
      response = "";
}
void buzzer(){
  if(buzzer == 0) {
    digitalWrite(buzzerLed, LOW)
  }
  if(buzzer == 1) {
    digitalWrite(buzzerLed, HIGH)
  }
}
void bluetooth(){
      while (Serial3.available()){
        if(bluetooth == 0){
          break;
        }
        delay(10);
        char c = Serial3.read();
        state += c;
      }

  if (state.length() > 0) 
  {
    Serial.println(state);

    // Check if the word "bottle" is present in the received string
    if (state.indexOf("bottle") != -1) {
      responce = "bluetooth : bottle"
            // Execute your code here if "bottle" is found
    }
    
    else if (state.indexOf("watch") != -1) {
      responce = "bluetooth : watch"
      // Execute your code here if "watch" is found
    } 

    else if (state.indexOf("medicine") != -1) {
      responce = "bluetooth : medicine"
      // Execute your code here if "medicine" is found
    } 

    else if (state.indexOf("lipstick") != -1) {
      responce = "bluetooth : lipstick"
      // Execute your code here if "lipstick" is found
    } 

    state = "";
  }

      Serial.println(response);
      response = "";
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
