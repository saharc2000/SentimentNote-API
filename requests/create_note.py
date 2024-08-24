import requests

url = 'http://127.0.0.1:3500/auth/login'
headers = {
    'Content-Type': 'application/json'
}
data = {
    'username': 'Sahar',
    'password': '123'
}

response = requests.post(url, json=data)

# Check the response
print(f'Status Code: {response.status_code}')  
print('Response Body:', response.json())  
if(response.status_code == 200):
    token = response.json().get('token')
    print('Token:', token)
    headers['Authorization'] = token
    url = 'http://127.0.0.1:3500/notes'
    data = {
        "title": "first note",
        "body": "Main dishes were really bad"
    }
    response = requests.post(url, headers=headers, json=data)
    print(f'Status Code: {response.status_code}')  
    print('Response Body:', response.json()) 