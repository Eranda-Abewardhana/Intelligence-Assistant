#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Arduino_JSON.h>

/////////////////////////////////////////

const char* ssid = "SLT_Fiber_TS_HOME"; // Your Wifi Name
const char* password = "tshotspot0"; // Your Wifi Password
int AlarmPin = 5; //Your Siren Alarm pin

/////////////////////////////////////////

const char* serverName = "http://tharindusathsara.000webhostapp.com/esp-outputs-action.php?action=outputs_state";

unsigned long interval = 500;
unsigned long previousMillis = 0;

unsigned long lastTime = 0;
long AlarmTimerDelay = 300;

String outputsState;

void setup() {
  Serial.begin(115200);
  delay(10);
  
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Connected to WiFi");
}

void loop() {
  if(millis() - previousMillis > interval) {
     // Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      outputsState = httpGETRequest(serverName);
      //Serial.println(outputsState);
      JSONVar myObject = JSON.parse(outputsState);
  
      // JSON.typeof(jsonVar) can be used to get the type of the var
      if (JSON.typeof(myObject) == "undefined") {
        Serial.println("Parsing input failed!");
        return;
      }
      JSONVar keys = myObject["Main"].keys();
      //Serial.print("JSON object = ");
      //Serial.println(myObject);
      Serial.print("Delay : ");
      Serial.println(myObject["Delay"]);
      AlarmTimerDelay = atoi(myObject["Delay"]);
      for (int i = 0; i < keys.length(); i++) {
        JSONVar value = myObject["Main"][keys[i]];
        Serial.print("SwitchID : ");
        Serial.print(keys[i]);
        Serial.print(" | Switch State : ");
        Serial.println(value);
        pinMode(atoi(keys[i]), OUTPUT);
        digitalWrite(atoi(keys[i]), atoi(value));
        digitalWrite(AlarmPin, HIGH);
        lastTime = millis();
      }
      // save the last HTTP GET Request
      previousMillis = millis();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
  }
  if ((millis() - lastTime) > AlarmTimerDelay) {
      digitalWrite(AlarmPin, LOW);
  }
}

String httpGETRequest(const char* serverName) {
  WiFiClient client;
  HTTPClient http;
    
  // Your IP address with path or Domain name with URL path 
  http.begin(client, serverName);
  
  // Send HTTP POST request
  int httpResponseCode = http.GET();
  
  String payload = "{}"; 
  
  if (httpResponseCode>0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  // Free resources
  http.end();

  return payload;
}
