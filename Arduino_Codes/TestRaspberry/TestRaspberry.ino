void setup() {
  Serial.begin(9600);
}


void loop() {
  if (Serial.available() > 0) {
    String receivedData = Serial.readStringUntil('\n');
    // Process the receivedData string as per your requirement
    // Here, we are simply sending back a response with mx_err and my_err values

    // Extracting mx_err value from receivedData
    int mx_err_start = receivedData.indexOf("mx_err:") + 7;
    int mx_err_end = receivedData.indexOf(",", mx_err_start);
    String mx_err_str = receivedData.substring(mx_err_start, mx_err_end);
    int mx_err = mx_err_str.toInt();

    // Extracting my_err value from receivedData
    int my_err_start = receivedData.indexOf("my_err:") + 7;
    int my_err_end = receivedData.indexOf(",", my_err_start);
    String my_err_str = receivedData.substring(my_err_start, my_err_end);
    int my_err = my_err_str.toInt();

    // Prepare the response string
    String response = "mx_err:" + String(mx_err) + " and my_err:" + String(my_err);

    // Send the response back to Python
    Serial.println(response);
  }
}
