// M1-red GRD-black C1-yellow Vcc-blue C2-green M2-white

#define C1 2 //yellow
#define C2 3 //green

void setup() {
  Serial.begin(9600);
  pinMode(C1, INPUT);
  pinMode(C2, INPUT);

}

void loop() {
   int a = digitalRead(C1);
   int b = digitalRead(C2);
   Serial.print(a*5);
   Serial.print(" ");
   Serial.print(b*5);
   Serial.print(" ");
   Serial.println("");
   delay(300);



}
