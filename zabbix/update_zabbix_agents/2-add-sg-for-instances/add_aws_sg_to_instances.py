import boto3
import os
from ast import literal_eval

"""
A tool for add default AWS Security Group for instances by IP.
"""

ec2 = boto3.resource('ec2')

default_sg = literal_eval(os.environ['SECURITY_GROUP'])

hosts_ip =[]
with open('hosts') as f:
    lines = f.readlines()

    for string in lines:
        if string.find('ansible_host="') != -1:
            ip = string.split('ansible_host="')[1].split('"')[0]
            hosts_ip.append(ip)

running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

for instance in running_instances:
    for ip in hosts_ip:
        if instance.private_ip_address == ip:
            all_sg_ids = [sg['GroupId'] for sg in instance.security_groups]

            default_sg_not_exist = True
            for sg_id in all_sg_ids:
                try:
                    if sg_id == default_sg[instance.vpc_id]:
                        default_sg_not_exist = False
                        break
                except KeyError:
                    print(f'KeyError for {ip}, VPC {instance.vpc_id}, All SG {all_sg_ids}')

            try:
                if (default_sg_not_exist):
                    all_sg_ids.append(default_sg[instance.vpc_id])
                    instance.modify_attribute(Groups=all_sg_ids)
                    print(f'Add SG "{default_sg[instance.vpc_id]}" for {ip}')
            except KeyError:
                pass # VPC is None
