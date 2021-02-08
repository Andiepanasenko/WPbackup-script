# Moduls
import requests
import os
import json
#++++Input data++++
url_source = raw_input("Enter url source:")
authorization_source = raw_input("Enter authorization token source \"Bearer **********\":")
url_sorce_req = str(url_source)
###############
url_destination = raw_input("Enter url destination:")
authorization_dest = raw_input("Enter authorization token destenation \"Bearer **********\":")

url_destination_req = str(url_destination)
##########
project = raw_input("Enter project name:")
project = project + str(" / ")
#++++folder migrait process++++++
#upload response in file
headers = {'Content-Type': 'application/json', 'Authorization': ''+authorization_source+'',}
response = requests.get(url_sorce_req+'api/folders', headers=headers)
#response = requests.get('https://grafana.airslate-stage.xyz/api/folders', headers = headers)
with open('response_folder.json', 'w') as outfile:
    outfile.write(response.content)
print response
#parsing file
items = open('response_folder.json')
data = json.load(items)
items.close()
length = len(data)
i = 0
while i < length:
    id = data[i]['id']
    title =  project + data[i]['title']
    uid = data[i]['uid']
    i+=1
    #create new items in grafana
    headers = {'Content-Type': 'application/json', 'Authorization': ''+authorization_dest+'',}
    data_items = '{  "uid": "'+uid+'", "title": "'+title+'"}'
    response = requests.post(url_destination_req+'api/folders', headers=headers, data=data_items)
    if response.status_code == 200:
        print ( "Create folder", title )
    else:
        print ( "Can't create folder", title, response )
print ("finish foldr")
#++++Teams migrait process++++++
#Get team
i=1
while i < 100:
    headers = {'Content-Type': 'application/json', 'Authorization': ''+authorization_source+'',}
    url = (url_sorce_req+'api/teams/'+str(i))
    response = requests.get(url, headers=headers)
    #Get team name
    data_teams = json.loads(response.content)
    data_teams_test = data_teams.values()
    print data_teams_test
    if data_teams_test[0] == "Team not found":
        print ("Team not found")
    else:
        name = project + data_teams['name']
        print name
        #create new items in grafana
        headers = {'Content-Type': 'application/json', 'Authorization': ''+authorization_dest+'',}
        data_team_name = '{"name": "'+name+'"}'
        response = requests.post(url_destination_req+'api/teams', headers=headers, data=data_team_name)
        if response.status_code == 200:
            print ( "Create team", name)
        else:
            print ( "Can't create team", response )
    i+=1
"""#++++datasource migrait datasources++++++
response = requests.get(url_sorce_req+'/api/datasources')
with open('response_datasources.json', 'w') as outfile:
    outfile.write(response.content)
#parsing file
items = open('response_datasources.json')
data = json.load(items)
items.close()
length = len(data)
i = 0
while i < length:
    name = project + data[i]['name']
    type =  data[i]['type']
    url = data[i]['url']
    access = data[i]['access']
    basicAuth = data[i]['basicAuth']
    i+=1
    #create new items in grafana
    headers = {'Authorization': ''+authorization_dest+'',}
    data_datasources ='{"name":"'+name+'", "type":"'+type+'", "url":"'+url+'", "access":"'+access+'"}'
    response = requests.post(url_destination_req+'/api/datasources', headers=headers, data=data_datasources)
    if response.status_code == 200:
        print ( title, "Create datasources", type )
    else:
        print ( "Can't create datasources", name, url, response )"""
