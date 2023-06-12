import requests
      
url = "http://192.168.234.76/?x_err=1&y_err=0&m_init=0"

    
response = requests.get(url)

if response.status_code == 200:  # Successful response
    print("Request successful!")
    print("Response content:")
    print(response.text)
else:
    print("Request failed with status code:", response.status_code)