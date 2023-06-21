#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Servo parameters
int servoPin = 5;
int servoMin = 150;   // Minimum servo pulse length
int servoMax = 600;   // Maximum servo pulse length

void setup() {
  pwm.begin();
  pwm.setPWMFreq(50); // Set the PWM frequency (adjust if needed)
}

void loop() {
  // Move the servo to 0 degrees
  pwm.setPWM(servoPin, 0, servoMin);

  delay(2000); // Pause for 2 seconds

  // Move the servo to 90 degrees
  int servoPosition = map(90, 0, 180, servoMin, servoMax);
  pwm.setPWM(servoPin, 0, servoPosition);

  delay(2000); // Pause for 2 seconds

  // Move the servo to 180 degrees
  pwm.setPWM(servoPin, 0, servoMax);

  delay(2000); // Pause for 2 seconds
}
