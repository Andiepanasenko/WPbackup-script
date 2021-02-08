import os
import json
from urllib.error import HTTPError

# consul_kv for work with key-value storage in Consul
from consul_kv import Connection

CONN = Connection(endpoint='http://' + os.environ['CONSUL_HTTP_ADDR'] + '/v1/kv')

data = str(CONN.get_dict(os.environ['PATH_TO_KEYS']))

with open('/app/keys.py', 'w') as f:
    f.write(data)
