#define enA 10 // PWN1
#define in1 A2 // L F
#define in2 A3 // L B

#define enB 11 // PWN2
#define in3 A4 // R F
#define in4 A5 // R B

void setup() {
  // Set the motor control pins as outputs
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  
  // Set the initial motor direction
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}

void loop() {
  // Set the motor speed
  analogWrite(enA, 255); // Adjust the speed as needed
  analogWrite(enB, 255); // Adjust the speed as needed
  
  // Rotate the motors clockwise
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  
  delay(2000); // Rotate for 2 seconds
  
  // Stop the motors
  analogWrite(enA, 0);
  analogWrite(enB, 0);
  
  delay(1000); // Pause for 1 second
  
  // Rotate the motors counterclockwise
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  
  delay(2000); // Rotate for 2 seconds
  
  // Stop the motors
  analogWrite(enA, 0);
  analogWrite(enB, 0);
  
  delay(1000); // Pause for 1 second
}
