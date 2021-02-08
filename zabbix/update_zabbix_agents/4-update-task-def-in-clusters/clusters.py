"""
A tool get cluster name and ARN
"""

import boto3
import os

ecs = boto3.client('ecs')

unneeded_keys = ('taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'compatibilities')
updated_TD = []

clusters = ecs.list_clusters(
    maxResults=100
)


for cluster_arn in clusters['clusterArns']:
    cluster_name = cluster_arn.split("/",1)[1]

    # for das
    if (cluster_name.find('dev') != -1 and
        cluster_name.find('dev-as-') == -1):
        continue

    if (cluster_name.find('prod-as') == -1 and
        cluster_name.find('prod-mas-') == -1):
        continue

    services = ecs.list_services(cluster=cluster_arn)['serviceArns']
    for service_arn in services:
        if service_arn.find('zabbix-agent') != -1:
            service_name = service_arn.split("/",1)[1]

            ###Get current task definiton
            response = ecs.describe_task_definition(taskDefinition=service_name)
            current_definition = response['taskDefinition']
            current_revision = current_definition['family'] + ':' + str(current_definition['revision'])

            ###Remove invalid keys for creating new task definition revision
            for key in unneeded_keys:
                try:
                    current_definition.pop(key)
                except:
                    print(f'Not found {key} in {cluster_name}')

            ### Change definition

            current_definition['containerDefinitions'][0]['image'] = 'zabbix/zabbix-agent:alpine-3.4-latest'
            current_definition['containerDefinitions'][0]['environment'] = [
                {'name': 'ZBX_DEBUGLEVEL', 'value': os.environ['ZBX_DEBUGLEVEL']},
                {'name': 'ZBX_METADATA', 'value': os.environ['ZBX_METADATA']},
                {'name': 'ZBX_SERVER_HOST', 'value': os.environ['ZBX_SERVER_HOST']}
            ]

            deregister_TD = True
            for TD in updated_TD:
                if current_definition['family'] == TD:
                    deregister_TD = False
                    break


            if (deregister_TD):
                ###Create new task definition revision
                response_new = ecs.register_task_definition(**current_definition)

                new_definition = response_new['taskDefinition']
                new_revision = new_definition['family'] + ':' + str(new_definition['revision'])

                ###Update service by new task definition revision
                service_info = {'cluster': cluster_name, 'service': service_name, 'taskDefinition': new_revision}
                ecs.update_service(**service_info)

                print(f"Revisions {current_definition['family']}. Previous: {current_revision.split(':',1)[1]}. New: {new_revision.split(':',1)[1]}. Cluster: {cluster_name}")

                # ###Derigister old task definition revision
                # ecs.deregister_task_definition(taskDefinition=current_revision)

                updated_TD.append(new_definition['family'])

            else:
                service_info = {'cluster': cluster_name, 'service': service_name, 'taskDefinition': current_revision}
                ecs.update_service(**service_info)
                print(f"Revisions {current_definition['family']}. Previous: {current_revision.split(':',1)[1]}. New: {current_revision.split(':',1)[1]}. Cluster: {cluster_name}")
