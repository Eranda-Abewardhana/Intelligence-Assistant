#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>

const char *ssid = "DESKTOP_TS_";
const char *password = "tshotspot1";

const int led = 4;
WiFiServer server(80);
SoftwareSerial NodeMCU(D2,D3);

void setup()
{
  // put your setup code here, to run once:
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
  // put your main code here, to run repeatedly:
  WiFiClient client;
  client = server.available();

  if (client == 1)
  {
    String request = client.readStringUntil('\n');
    client.flush();
    int spaceIndex = request.indexOf(" HTTP");
    String method = request.substring(5, spaceIndex);
    Serial.println(method);
    NodeMCU.print(method);
	  NodeMCU.println("\n");
    // int get = method.indexOf("-");
    // String data1 = method.substring(1,get);
    // String data2 = method.substring(get+1, method.length());
    // Serial.println(data1);
    // Serial.println(data2);
    // if (request.indexOf("ledon") != -1)
    // {
    //   digitalWrite(led, HIGH);
      
    //   Serial.println("LED IS ON NOW");
    //   // Serial.println(data1);
    //   // Serial.println(data2);
    //   NodeMCU.print("LED IS ON NOW");
	  //   NodeMCU.println("\n");
    // }
    // else if (request.indexOf("ledoff") != -1)
    // {
    //   digitalWrite(led, LOW);

    //   client.println("HTTP/1.1 200 OK");
    //   Serial.println("LED IS OFF NOW");
    //   NodeMCU.print("LED IS OFF NOW");
	  //   NodeMCU.println("\n");
    // }
    // Serial.print("Client Disconnected");
    // Serial.println("===========================================================");
    // Serial.println("                              ");
  }
}