#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>

const char *ssid = "Xiaomi";
const char *password = "CHANNA2001";

const int led = 4;
WiFiServer server(80);
SoftwareSerial NodeMCU(D2,D3);

void setup()
{
  pinMode(led, OUTPUT);
  Serial.begin(115200);	
	NodeMCU.begin(9600);
	pinMode(D2,INPUT);
	pinMode(D3,OUTPUT);
  Serial.print("Connecting to.");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print("..");
  }
  Serial.println("Nodemcu(esp8266) is connected to the ssid");
  Serial.println(WiFi.localIP());
  server.begin();
  delay(1000);
}

void loop()
{
  WiFiClient client;
  client = server.available();

  if (client){

    String request = client.readStringUntil('\n');
    if (request.startsWith("GET")) {
      int paramStart = request.indexOf("?") + 1;
      int paramEnd = request.indexOf(" ", paramStart);
      String params = request.substring(paramStart, paramEnd);
      
      String errValueX = getValue(params, "x_err");
      String errValueY = getValue(params, "y_err");
      String mInitValue = getValue(params, "m_init");

      Serial.print("err X = ");
      Serial.println(errValueX);
      Serial.print("err Y = ");
      Serial.println(errValueY);
      Serial.print("m_init = ");
      Serial.println(mInitValue);

      String parameterList = "x_err:" + String(errValueX) + ",y_err:" + String(errValueY) + ",m_init:" + String(mInitValue)+ ",##:0";
      NodeMCU.println(parameterList);

      // sendResponse(client, "200OK");
    }
    delay(10);
  }

  if (NodeMCU.available()) {
    String receivedString = NodeMCU.readStringUntil('\n');

    int colonIndex = receivedString.indexOf(':');
    if (colonIndex != -1) {
      String paramName = receivedString.substring(0, colonIndex);
      String paramValue = receivedString.substring(colonIndex + 1);

      int intValue = paramValue.toInt();

      String content = (paramName + ":" + intValue);

      sendResponse(client, content);
    }
  }

}

void sendResponse(WiFiClient client, String content) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/plain");
  client.println();
  client.println(content);
}

String getValue(String data, String key) {
  String separator = "=";
  int keyStart = data.indexOf(key + separator);
  if (keyStart != -1) {
    keyStart += key.length() + separator.length();
    int keyEnd = data.indexOf("&", keyStart);
    if (keyEnd == -1) {
      keyEnd = data.length();
    }
    return data.substring(keyStart, keyEnd);
  }
  return "";
}