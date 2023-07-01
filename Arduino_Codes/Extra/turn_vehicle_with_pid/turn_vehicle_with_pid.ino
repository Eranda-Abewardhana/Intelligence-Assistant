// M1-red GRD-black C1-yellow Vcc-blue C2-green M2-white

// This alternate version of the code does not require
// atomic.h. Instead, interrupts() and noInterrupts()
// are used. Please use this code if your
// platform does not support ATOMIC_BLOCK.
//12 14A 15A 0RX 1TX 

#define ENCA 2 // M1C1 yellow
#define ENCB 3 // M1C2 green
#define PWM1 11
#define IN1 12
#define IN2 13

#define ENCC 4 // M2C1 yellow
#define ENCD 5 // M2C2 green
#define PWM2 6
#define IN3 8
#define IN4 9

// set target position
float target1[5][3] = {
  {900, 0, 0.4},
  {0, 200, 0.6},
  {-900, 0, 0.5},
  {0, 200, 0.6},
  {0, 0, 0}
};

volatile int posi1 = 0;
volatile int posi2 = 0;
long prevT = 0;
float e1prev = 0;
float e2prev = 0;
float eintegral1 = 0;
float eintegral2 = 0;
int i = 0;
bool reachedFinalTarget = false;

// PID constants
float kp = 1;
float kd = 0.025;
float ki = 0.0;

void setup() {
  Serial.begin(9600);
  pinMode(ENCA, INPUT);
  pinMode(ENCB, INPUT);
  attachInterrupt(digitalPinToInterrupt(ENCA), readEncoder1, RISING);

  pinMode(ENCC, INPUT);
  pinMode(ENCD, INPUT);
  attachInterrupt(digitalPinToInterrupt(ENCC), readEncoder2, RISING);

  pinMode(PWM1, OUTPUT);
  pinMode(PWM2, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.println("target pos");
}

void loop() {
  if (reachedFinalTarget) {
    // Stop the motors completely
    setMotor(0, 0, PWM1, IN1, IN2, 0);
    setMotor(0, 0, PWM2, IN3, IN4, 0);
    return; // Exit the loop
  }

  float* target = target1[i];

  // time difference
  long currT = micros();
  float deltaT = ((float)(currT - prevT)) / (1.0e6);
  prevT = currT;

  // Read the position
  int pos1 = 0;
  noInterrupts(); // disable interrupts temporarily while reading
  pos1 = posi1;
  interrupts(); // turn interrupts back on

  // Read the position
  int pos2 = 0;
  noInterrupts(); // disable interrupts temporarily while reading
  pos2 = posi2;
  interrupts(); // turn interrupts back on

  // errorM1
  float e1 = pos1 - target[0];

  // errorM2
  float e2 = pos2 - target[1];

  // derivative
  float dedt1 = (e1 - e1prev) / deltaT;

  // derivative
  float dedt2 = (e2 - e2prev) / deltaT;

  // integral
  eintegral1 = eintegral1 + e1 * deltaT;

  // integral
  eintegral2 = eintegral2 + e2 * deltaT;

  // control signal
  float u1 = kp * e1 + kd * dedt1 + ki * eintegral1;

  // control signal
  float u2 = kp * e2 + kd * dedt2 + ki * eintegral2;

  // motor1 power
  float pwr1 = fabs(u1);
  // motor2 power
  float pwr2 = fabs(u2);
  if (pwr1 > 255) {
    pwr1 = 255;
  }
  if (pwr2 > 255) {
    pwr2 = 255;
  }
  // motor1 direction
  int dir1 = 1;
  // motor2 direction
  int dir2 = 1;
  if (u1 < 0) {
    dir1 = -1;
  }
  if (u2 < 0) {
    dir2 = -1;
  }
  // signal the motor
  setMotor(dir1, pwr1, PWM1, IN1, IN2, target[2]);
  // signal the motor
  setMotor(dir2, pwr2, PWM2, IN3, IN4, target[2]);

  // store previous error
  e1prev = e1;
  // store previous error
  e2prev = e2;

  Serial.print(target[0]);
  Serial.print(" ");
  Serial.print(pos1);
  Serial.println();

  Serial.print(target[1]);
  Serial.print(" ");
  Serial.print(pos2);
  Serial.println();

  i++;
  if (i >= 5) {
    reachedFinalTarget = true;
  }
}

void setMotor(int dir, int pwmVal, int pwm, int in1, int in2, float delay1) {
  analogWrite(pwm, pwmVal);
  if (dir == 1) {
    digitalWrite(in1, HIGH);
    delay((int)(delay1 * 1000));
    digitalWrite(in2, LOW);
  }
  else if (dir == -1) {
    digitalWrite(in1, LOW);
    delay((int)(delay1 * 1000));
    digitalWrite(in2, HIGH);
  }
  else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
  }
}

void readEncoder1() {
  int b = digitalRead(ENCB);
  if (b > 0) {
    posi1++;
  }
  else {
    posi1--;
  }
}

void readEncoder2() {
  int c = digitalRead(ENCD);
  if (c > 0) {
    posi2++;
  }
  else {
    posi2--;
  }
}
