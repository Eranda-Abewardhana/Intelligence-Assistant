#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>

const char *ssid = "SLT_FIBRE";
const char *password = "19765320";

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

        // String request = client.readStringUntil('\r');
        // Serial.println(request);
        // client.flush();
       
        // Close the client connection
        // client.stop();
        // Extract parameters from the request
        // String parameter1 = extractParameter(request, "m_init");
        // String parameter2 = extractParameter(request, "err");

        // // Print the extracted parameters
        // NodeMCU.print("m_init : ");
        // NodeMCU.println(parameter1);
        // NodeMCU.print("err:");
        // NodeMCU.println(parameter2);
        // Serial.println(parameter1);
        // Serial.println(parameter2);

        String request = client.readStringUntil('\n');
        client.flush();
        int spaceIndex = request.indexOf(" HTTP");
        String method = request.substring(5, spaceIndex);
        Serial.println(method);
        NodeMCU.println(method);

         // Handle the request and send the response
        handleRequest(client);

        // Wait a short moment before closing the connection
        delay(10);
  }
}
void handleRequest(WiFiClient client) {
  int responseCode = 200; // Set the desired response code (e.g., 200 for OK)

  // Send the response headers
  client.print("HTTP/1.1 ");
  client.print(responseCode);
  client.println(" OK");
  client.println("Content-Type: text/plain");
  client.println();

  // Send the response body
  client.println("Response message");
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