#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>

const char *ssid = "DESKTOP_TS_";
const char *password = "tshotspot1";

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

  if (client == 1){

        String request = client.readStringUntil('\r');
        client.flush();

        // Extract parameters from the request
        String parameter1 = extractParameter(request, "m_init");
        String parameter2 = extractParameter(request, "err");

        // Print the extracted parameters
        // NodeMCU.print("m_init : ");
        // NodeMCU.println(parameter1);
        NodeMCU.print("err:");
        NodeMCU.println(parameter2);

    // String request = client.readStringUntil('\n');
    // client.flush();
    // int spaceIndex = request.indexOf(" HTTP");
    // String method = request.substring(5, spaceIndex);
    // Serial.println(method);
    // NodeMCU.println(method);
  }
}

String extractParameter(String request, String paramName) {
  int paramStart = request.indexOf(paramName + "=");
  if (paramStart != -1) {
    paramStart += paramName.length() + 1;
    int paramEnd = request.indexOf('&', paramStart);
    if (paramEnd == -1) {
      paramEnd = request.length();
    }
    return request.substring(paramStart, paramEnd);
  }
  return "";
}