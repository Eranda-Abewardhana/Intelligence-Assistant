// M1-red GRD-black C1-yellow Vcc-blue C2-green M2-white

#include <util/atomic.h>

#define C1 4 //yellow
#define C2 5 //green
#define PWM 11
#define IN1 A4
#define IN2 A5

volatile int posi = 0;

void setup() {
  Serial.begin(9600);

  pinMode(C1, INPUT);
  pinMode(C2, INPUT);
  attachInterrupt(digitalPinToInterrupt(C1), readEncoder, RISING);
   
  pinMode(PWM,OUTPUT);
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
}

void loop() {
   
  int pos = 0;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    pos = posi;
  }

  setMotor(1, 150, PWM, IN1, IN2);
  delay(200);
   Serial.println(pos);
  setMotor(-1, 150, PWM, IN1, IN2);
  delay(200);
  Serial.println(pos);
  setMotor(0, 150, PWM, IN1, IN2);
  delay(20);
   Serial.println(pos);
}

void setMotor(int dir,int pwmVal,int pwm,int in1,int in2){
  analogWrite(pwm, pwmVal);

  if(dir==1){
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  }

  else if(dir==-1){
    digitalWrite(in2, HIGH);
    digitalWrite(in1, LOW);
  }

  else {
    digitalWrite(in2, LOW);
    digitalWrite(in1, LOW);
  }

}

void readEncoder(){
  int b = digitalRead(C2);
  if(b>0){
    posi++;
  }
  else{
    posi--;
  }

}
