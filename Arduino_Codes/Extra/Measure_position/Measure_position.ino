// M1-red GRD-black C1-yellow Vcc-blue C2-green M2-white

#define C1  19 //yellow
#define C2  17 //green

int pos = 0;

void setup() {
  Serial.begin(9600);
  pinMode(C1, INPUT);
  pinMode(C2, INPUT);
  attachInterrupt(digitalPinToInterrupt(C1), readEncoder, RISING);

}

void loop() {
   
   Serial.println(pos);

}

void readEncoder(){
  int b = digitalRead(C2);
  if(b>0){
    pos++;
  }
  else{
    pos--;
  }

}
