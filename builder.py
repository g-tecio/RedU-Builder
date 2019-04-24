import json
import requests

api_token = 'da2-fp2jl3o5vbeujik2p6k26sbshi'
api_url_base = 'https://cs7ammbpdrfmjay76wqwkjuemi.appsync-api.us-east-1.amazonaws.com/graphql'
index_html = ''

with open('index.html', 'r') as f:
    index_html= f.read()

headers = {
    'Content-Type': 'application/json',
    'x-api-key': api_token
}

query = {
    'query': 'query getPage{ getPage(id:"14e9b426-854d-4a86-a4f2-5e220e37e582" ) { title summary } }'
}

response = requests.post(url=api_url_base, json=query, headers=headers)
response_json = json.loads(json.dumps(response.json()))
obj = response_json["data"]["getPage"]

for key, value in obj.items():
    index_html = index_html.replace("{{" + key + "}}", value)
    print(key)

print(obj)
print(index_html)