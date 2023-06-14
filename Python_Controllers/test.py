import requests
      
url = "http://192.168.112.76/?stop=0&x_err=100&y_err=0&m_init=0"

    
response = requests.get(url)

if response.status_code == 200:  # Successful response
    print("Response content : ")
    print(response.text)
else:
    print("Request failed with status code:", response.status_code)