import requests

url = 'http://127.0.0.1:3500/auth/login'
headers = {
    'Content-Type': 'application/json'
}
data = {
    'username': 'hi',
    'password': '123'
}

response = requests.post(url, json=data)

# Check the response
print(f'Status Code: {response.status_code}')  
if(response.status_code == 200):
    token = response.json().get('token')
    headers['Authorization'] = token
    url = 'http://127.0.0.1:3500/notes'
    response = requests.get(url, headers=headers)
    print(f'Status Code: {response.status_code}')  
    print('Response Body:', response.json()) 