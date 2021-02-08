# Moduls
import requests
import os
import json

#++++Input data++++
url_source = raw_input("Enter url_source with out http:") #('localhost:3000')
login_sourse = raw_input("Enter login:") #('admin')
password_source = raw_input("Enter password:")#('admin')
url_sorce_req = 'http://'+str(login_sourse)+':'+str(password_source)+'@'+str(url_source)+''
###############
url_destination = raw_input("Enter url_destination with out http:")#('localhost:3001')
login_dest = raw_input("Enter login:") #('admin')
password_dest = raw_input("Enter password:")#('admin')
url_destination_req = 'http://'+str(login_dest)+':'+str(password_dest)+'@'+str(url_destination)+''
##########
project = raw_input("Enter project name:")
project = project + str("/")
#++++folder migrait process++++++
#upload response in file
response = requests.get(url_sorce_req+'/api/folders')
with open('response_folder.json', 'w') as outfile:
    outfile.write(response.content)

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
    headers = {'Content-Type': 'application/json',}
    data_items = '{  "uid": "'+uid+'", "title": "'+title+'"}'
    response = requests.post(url_destination_req+'/api/folders', headers=headers, data=data_items)
    if response.status_code == 200:
        print ( "Create folder", title )
    else:
        print ( "Can't create folder", title, response )

#++++Teams migrait process++++++
#Get team
i=1
while i < 100:
    url = (url_sorce_req+'/api/teams/'+str(i))
    response = requests.get(url)
    #Get team name
    data_teams = json.loads(response.content)
    data_teams_test = data_teams.values()
    if data_teams_test[0] == "Team not found":
        print ("Team not found")
    else:
        name = project + data_teams["name"]
        print name
        #create new items in grafana
        headers = {'Content-Type': 'application/json',}
        data_team_name = '{"name": "'+name+'"}'
        response = requests.post(url_destination_req+'/api/teams', headers=headers, data=data_team_name)
        if response.status_code == 200:
            print ( "Create team", name)
        else:
            print ( "Can't create team", response )
    i+=1
"""response = requests.get(url_sorce_req+'/api/datasources')
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
    headers = {'Content-Type': 'application/json',}
    data_datasources ='{"name":"'+name+'", "type":"'+type+'", "url":"'+url+'", "access":"'+access+'"}'
    response = requests.post(url_destination_req+'/api/datasources', headers=headers, data=data_datasources)
    if response.status_code == 200:
        print ( title, "Create datasources", type )
    else:
        print ( "Can't create datasources", name, url, response )"""
