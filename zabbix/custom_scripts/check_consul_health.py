import requests
try:
    SERVICE = requests.get('http://localhost:8500/v1/health/service/consul').json()
except requests.exceptions.ConnectionError:
    print(0)
    exit(0)

nodes_work = 0

for node in SERVICE:
    if node['Checks'][0]['Status'] == 'passing':
        nodes_work += 1

print(nodes_work)
