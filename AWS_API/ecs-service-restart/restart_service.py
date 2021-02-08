#!/usr/bin/env python3

import boto3
import os

exclude_service_list = ('gcp-node-exporter',
                    'registrator',
                    'dns-cache',
                    'gcp-cadvisor',
                    'jaeger-agent',
                    'zabbix-agent',
                    'consul-agent',
                    'filebeat')
# Shared vars
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
CLUSTER_NAME = os.environ.get('CLUSTER_NAME', None)
# AWS init connection
session = boto3.Session(region_name=AWS_REGION)
ecs_client = session.client('ecs')

def parse_arn(arn):
    elements = arn.split(':', 5)
    task_arn = { 'resource': elements[5] }
    try:
        task_id = task_arn['resource'].split('/')[2]
    except IndexError:
        task_id = task_arn['resource'].split('/')[1]
    return task_id

def restart_service(srvs):
    response = ecs_client.update_service(
        cluster=CLUSTER_NAME,
        service=srvs,
        forceNewDeployment=True
    )
    return response

def get_services():
    response = ecs_client.list_services(cluster=CLUSTER_NAME, maxResults=100)
    service_list = []
    for services in response['serviceArns']:
        parsed_service = parse_arn(services)
        if parsed_service not in exclude_service_list:
            service_list.append(parsed_service)
    return service_list
    
for service_name in get_services():
    restart_service(service_name)
    print("Restarting: {}".format(service_name))
print("Success!")