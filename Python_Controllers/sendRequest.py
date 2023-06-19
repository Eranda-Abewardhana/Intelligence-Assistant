import requests

root_url = "http://172.20.10.5"

try:
    payload = {
        'stop': 0,
        'x_err': 0,
        'y_err': 0,
        'm_init': 0,
        # 'servo_base': 85,
        # 'servo_grip': 0, # MAX 65
        # 'servo_1': 80,
        # 'servo_2': 50,
    }
    response = requests.get(root_url, params=payload, timeout=1)
    if response.status_code == 200:
        print("Response content:")
        print(response.text)
    else:
        print("Request failed with status code:", response.status_code)
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
