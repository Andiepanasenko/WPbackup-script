#!/usr/bin/python3

from dotenv import load_dotenv
import os
import requests
import json
from pathlib import Path
from requests.auth import HTTPBasicAuth
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

url = os.getenv("url") + ('app/rest/users/')
login = os.getenv("login")
passwd = os.getenv("passwd")
group_url = os.getenv("url") + ('app/rest/userGroups')
scope_url = os.getenv("url") + ('app/rest/userGroups/key:')
cgroup_url = os.getenv("url") + ('app/rest/users/username:')
get_group_headers = {'Accept': 'application/json'}
get_headers = {'Accept': 'application/json'}
post_headers = {'Content-Type': 'application/json'}
post_xml_headers = {'Content-Type': 'application/xml'}

# Запрашиваем ввод юзернейма и не разрешаем пустой ввод
while (True):
    tmpuser = input("Enter username (must be email like username@pdffiller.team) without spaces or other specific symbols: ")
    # Проверка введенного юзернейма. Если юзер есть - пропускаем цикл, если юзера нет - создаем.
    if(len(tmpuser) != 0):
        user_json = str("{" + (('"username":"') + tmpuser + ('","password":"xyz"')) + "}")
        response = requests.get(url+tmpuser, headers=get_headers, auth=HTTPBasicAuth(login, passwd))
        print(response)
        if response.status_code != 200:
            user_creation = requests.post(url, headers=post_headers, data=user_json, auth=HTTPBasicAuth(login, passwd))
            print("User not found and has been created")
            break
        else:
            print("User found, proceed script")
            break
    else:
        print("Incorrect input, please try again")
        tmpuser=""

# Запрос ключевого слова, по которому будет происходить выборка групп
print("Enter keyword")
keyword = input()
print("======")
groups_list = requests.get(group_url, headers=get_group_headers, auth=HTTPBasicAuth(login, passwd))

data = groups_list.json()
for i in data["group"]:
 if keyword in i["name"]:
  print("name: " + i["name"])
  print("key: " + i["key"])
  print("======")

# Ввод group key, если ввод не пустой - выводим скоуп соответствующей группы и спрашиваем продолжить или нет.
# Если нет, то гоняем по кругу, пока не найдется подходящая группа

while(True):
    print("Enter the key: ")
    group_key = input()

    if group_key != "":
        group_scope_url = scope_url + group_key + ('/roles')
        scope_info = requests.get(group_scope_url, headers=get_headers, auth=HTTPBasicAuth(login, passwd))
        scope_test=json.loads(scope_info.text)
        scope_print=json.dumps(scope_test, indent=4)
        print(scope_print)
        print("==================")
        print("Continue? y/n: ")
        cont_value = input()
 # Если ввели "y" то здесь юзер добавляется в группу и цикл завершается.
        if cont_value == "y":
            create_group_url = cgroup_url + tmpuser + ('/groups')
            post_group_data = str("<group key='" + group_key + "'/>")
            add_user_to_group = requests.post(create_group_url, headers=post_xml_headers, data=post_group_data, auth=HTTPBasicAuth(login, passwd))
            print(post_group_data)
            print(add_user_to_group)
            break
        else:
            print("return")
    else:
        print("Please enter correct key: ")
