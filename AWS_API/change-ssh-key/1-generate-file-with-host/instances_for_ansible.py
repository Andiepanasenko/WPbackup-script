"""
A tool get IP's for non-cluster instances
"""

import boto3
import os

from ignored_mask import *
exclude_start_paterns = eval(os.environ['AWS_ACCOUNT'])

ecs = boto3.client('ecs')

clusters = ecs.list_clusters(maxResults=1)
next_token = (clusters['clusterArns'])

paginator = ecs.get_paginator('list_clusters')

page_iterator = paginator.paginate(
  PaginationConfig={
        'PageSize': 100,
        'nextToken': next_token
    })

clusters_name = []
for page in page_iterator:
    for arn in page['clusterArns']:
        cluster_name = arn.split("/",1)[1]
        clusters_name.append(cluster_name)


ec2 = boto3.resource('ec2')

# Get information for all running instances
running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

with open('hosts', 'w') as hosts:
    hosts.write('\
[servers:vars]\n\
ansible_user="' + os.environ['USER'] + '"\n\
ssh_key_name="' + os.environ['SSH_KEY'] + '"\n\n\
[servers]\n\
')

    for instance in running_instances:
        try:
            for tag in instance.tags:
                if 'Name' in tag['Key']:
                    name = tag['Value']
        except:
            name = instance.private_ip_address

        non_cluster_host = True
        for cluster_name in clusters_name:
            if cluster_name == name:
                non_cluster_host = False
                break

        if os.environ['USER'] == 'ec2-user':
            non_cluster_host = not non_cluster_host

        if (non_cluster_host):

            not_skip = True
            for patern in exclude_start_paterns:
                if (name.startswith(patern)):
                    not_skip = False
                    break

            if (not_skip):
                name = name.replace(' ', '_') + instance.private_ip_address
                if instance.vpc_id == os.environ['BASTION_VPC']:
                    hosts.write(name + ' ansible_host="' + instance.private_ip_address + '"\n')
                else:
                    hosts.write(name + ' ansible_host="' + instance.public_ip_address + '"\n')
