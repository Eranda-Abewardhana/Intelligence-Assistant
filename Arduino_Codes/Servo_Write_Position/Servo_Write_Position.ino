#include <Boards.h>
#include <Firmata.h>
#include <FirmataConstants.h>
#include <FirmataDefines.h>
#include <FirmataMarshaller.h>
#include <FirmataParser.h>

#include <Servo.h> // include server library

Servo ser;
Servo ser2;
int val,val3;

void setup() {
  Serial.begin(9600); // Serial comm begin at 9600bps
  ser.attach(8);// server is connected at pin 9
  ser2.attach(9);// server is connected at pin 9
  ser.write(0);
  ser2.write(0);
}

void loop() {
  if (Serial.available())
  {
    int val2 = Serial.parseInt();
    if (val2!=0){
      val = val2;
    }
    Serial.println(val);
    if(val3<val){
      for (int pos = val3; pos <= val; pos += 2) {
        ser2.write(pos);
        delay(20);
      }
    }else{
      for (int pos = val3; pos >= val; pos -= 2) {
        ser2.write(pos);
        delay(20);
      }
    }
    val3 = val;
  }
}
