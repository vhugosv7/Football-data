import requests


uri = 'https://api.football-data.org/v4/teams/'
headers = {'X-Auth-Token': '963f590057a946a0b7d805f94569c899'}

response = requests.get(uri, headers=headers)
data = response.json()
for item in data['teams']:
    print(item['crest'])