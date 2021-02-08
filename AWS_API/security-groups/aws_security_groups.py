import json
from collections import defaultdict
# pip3 install boto3
import boto3

REGION = 'us-east-1'
nested_dict = lambda: defaultdict(nested_dict)
CLIENT = boto3.client('ec2')

# Get data about all security groups and all instances
ES_SG = CLIENT.describe_security_groups()
ES_I = CLIENT.describe_instances()

# Create result file as "json array"
with open('/app/aws-sec-group.json', 'w') as json_data:
    json_data.write('[')


for i in range(len(ES_I['Reservations'])):
    try:
        INSTANCES_GROUP_ID = ES_I['Reservations'][i]['Instances'][0]['NetworkInterfaces'][0]['Groups'][0]['GroupId']
    except IndexError:
        pass

    for j in range(len(ES_SG['SecurityGroups'])):

        SECURITY_GROUP_ID = ES_SG['SecurityGroups'][j]['GroupId']

        # When Group ID is equal:
        # Add needing data from Security Groups and Instances to output file
        if INSTANCES_GROUP_ID == SECURITY_GROUP_ID:

            ipPermissions = nested_dict()
            for k in range(len(ES_SG['SecurityGroups'][j]['IpPermissions'])):
                try:
                    ipPermissions[k]['FromPort'] = ES_SG['SecurityGroups'][j]['IpPermissions'][k]['FromPort']
                    ipPermissions[k]['ToPort'] = ES_SG['SecurityGroups'][j]['IpPermissions'][k]['ToPort']
                    ipPermissions[k]['IpRanges'] = ES_SG['SecurityGroups'][j]['IpPermissions'][k]['IpRanges']

                # AWS return []. Usually - it's equal to "all ports open"
                except KeyError:
                    ipPermissions[k]['Look_at_AWS'] = '<a href="https://console.aws.amazon.com/ec2/v2/home?region=' + \
                                                      REGION + '#SecurityGroups:search=' + \
                                                      ES_SG['SecurityGroups'][j]['GroupId'] + ';sort=groupId">Link</a>'
                    ipPermissions[k]['FromPort'] = 'All ports'
                    ipPermissions[k]['ToPort'] = 'All ports'


            with open('/app/aws-sec-group.json', 'a') as json_data:
                json_data.write(json.dumps({
                    'InstanceTags': ES_I['Reservations'][i]['Instances'][0]['Tags'],
                    'InstanceId': ES_I['Reservations'][i]['Instances'][0]['InstanceId'],
                    'GroupName':  ES_SG['SecurityGroups'][j]['GroupName'],
                    'GroupId': ES_SG['SecurityGroups'][j]['GroupId'],
                    'IpPermissions': ipPermissions
                }))
                json_data.write(',')


with open('/app/aws-sec-group.json', 'a') as json_data:
    json_data.write('{}]')
