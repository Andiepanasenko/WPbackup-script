# pip3 install boto3
import boto3
import json
import re
from collections import defaultdict

SERVICE_REGION = 'us-east-1'
SERVICE_NAME = 'prod-remote-monitor'
SERVICE_ENV = 'prod'

nested_dict = lambda: defaultdict(nested_dict)
SETTINGS = nested_dict()

CLIENT = boto3.client('elasticache')


# Find primary shards
ES = CLIENT.describe_replication_groups()

for i in range(len(ES['ReplicationGroups'])):
    name = ES['ReplicationGroups'][i]['ReplicationGroupId']
    if name == 'mm-t2' or \
       name == 'worker-dev-redis':
        continue

    host = ES['ReplicationGroups'][i]['NodeGroups'][0]['PrimaryEndpoint']['Address']
    port = ES['ReplicationGroups'][i]['NodeGroups'][0]['PrimaryEndpoint']['Port']
    SETTINGS[name]['host'] = host
    SETTINGS[name]['port'] = port

# Find non-cluster endpoint
ES = CLIENT.describe_cache_clusters(
    ShowCacheNodeInfo=True,
    # ShowCacheClustersNotInReplicationGroups=True
)

for i in range(len(ES['CacheClusters'])):
    name = ES['CacheClusters'][i]['CacheClusterId']

    # Skip non PrimaryEndpoints (Cluster primary/replica endpoints)
    # Skip not Redis (Memcached)
    if re.search('-[0-9]{3}$', name) or ES['CacheClusters'][i]['Engine'] != 'redis':
        continue

    host = ES['CacheClusters'][i]['CacheNodes'][0]['Endpoint']['Address']
    port = ES['CacheClusters'][i]['CacheNodes'][0]['Endpoint']['Port']
    SETTINGS[name]['host'] = host
    SETTINGS[name]['port'] = port


CONSUL = nested_dict()
for name in SETTINGS:
    CONSUL[SERVICE_REGION]['AWS-services']['elasticache']['redis'][name]['host'] = SETTINGS[name]['host']

with open('/app/configs/dev_conf5.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))


CONSUL = nested_dict()
for name in SETTINGS:
    CONSUL[SERVICE_REGION]['AWS-services']['elasticache']['redis'][name]['port'] = SETTINGS[name]['port']

with open('/app/configs/dev_conf6.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))

CONSUL = nested_dict()
for name in SETTINGS:
    CONSUL[SERVICE_REGION]["apps"][SERVICE_NAME][SERVICE_ENV]['zabbix']['hostnames']['redis'][name] = 'remote-monitor-redis'

with open('/app/configs/dev_conf7.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))
