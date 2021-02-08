import json
import urllib.request
import urllib.parse
import argparse

parser = argparse.ArgumentParser(description='Process some variables.')

parser.add_argument("--host", required=True, help='Consul endpoint')
parser.add_argument("--tocken", required=True, help='Consul master tocken')
parser.add_argument("--tocken_name", required=True, help='Tocken Name to delete')

args = parser.parse_args()

url = str(args.host)+":8500/v1/acl/list"
headers = {'X-Consul-Token':str(args.tocken)}
req = urllib.request.Request(url=url, headers=headers, method='GET')

resp = urllib.request.urlopen(req)
content = resp.read().decode('utf-8')

json = json.loads(content)

for i in json:
        if i["Name"].startswith(str(args.tocken_name)):
                url_destroy = str(args.host)+':8500/v1/acl/destroy/'+str(i["ID"])
                req = urllib.request.Request(url=url_destroy, headers=headers, method='PUT')
                resp = urllib.request.urlopen(req)
                print(resp)
