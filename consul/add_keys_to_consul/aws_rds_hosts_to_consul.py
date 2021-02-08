# pip install boto3
import boto3
import json
from collections import defaultdict

CLIENT = boto3.client('rds')

RDS = CLIENT.describe_db_instances()
SETTINGS = {}


for i in range(len(RDS['DBInstances'])):
    name = RDS['DBInstances'][i]['DBInstanceIdentifier']

    if name.startswith('denise') or \
       name.startswith('dev') or \
       name.startswith('pdf-performance') or \
       name.startswith('perf01'):
        continue

    url = RDS['DBInstances'][i]['Endpoint']['Address']

    if name == 'lb-rds-2':
        url = 'db.pdf.int'
    if name == 'lb-rds-ro':
        url = 'db-ro.pdf.int'
    if name == 'lb-rds-fast-ro':
        url = 'db-ro-fast.pdf.int'

    SETTINGS[name] = url

SERVICE_REGION = 'us-east-1'
SERVICE_NAME = 'prod-remote-monitor'
SERVICE_ENV = 'prod'


nested_dict = lambda: defaultdict(nested_dict)
CONSUL = nested_dict()


for name in SETTINGS:
    url = SETTINGS[name]
    CONSUL[SERVICE_REGION]['AWS-services']['RDS']['mysql'][name]['host'] = url

with open('/app/configs/dev_conf1.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))


CONSUL = nested_dict()
for name in SETTINGS:
    CONSUL[SERVICE_REGION]['apps'][SERVICE_NAME][SERVICE_ENV]['zabbix']['hostnames']['mysql'][name] = 'remote-monitor-mysql'

with open('/app/configs/dev_conf2.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))


CONSUL = nested_dict()
for name in SETTINGS:
    CONSUL[SERVICE_REGION]['apps'][SERVICE_NAME][SERVICE_ENV]['RDS'][name]['user'] = ''

    if name == 'lb-rds-2' or \
       name == 'lb-rds-ro' or \
       name == 'lb-rds-fast-ro':
        CONSUL[SERVICE_REGION]['apps'][SERVICE_NAME][SERVICE_ENV]['RDS'][name]['user'] = 'remote-monitor'


with open('/app/configs/dev_conf3.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))


CONSUL = nested_dict()
for name in SETTINGS:
    CONSUL[SERVICE_REGION]['apps'][SERVICE_NAME][SERVICE_ENV]['RDS'][name]['password'] = ''

with open('/app/configs/dev_conf4.json', 'w') as json_data:
    json_data.write(json.dumps(CONSUL))
