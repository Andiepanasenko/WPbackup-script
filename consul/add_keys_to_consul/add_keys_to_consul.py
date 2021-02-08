import os
import json
from urllib.error import HTTPError

# consul_kv for work with key-value storage in Consul
from consul_kv import Connection

CONN = Connection(endpoint='http://' + os.environ['CONSUL_HTTP_ADDR'] + '/v1/kv')

for i in range(1, 8):
    with open('/app/configs/dev_conf'+ str(i) + '.json') as json_data:
        CONSUL_CONF = json.load(json_data)

    CONN.put_dict(CONSUL_CONF)
