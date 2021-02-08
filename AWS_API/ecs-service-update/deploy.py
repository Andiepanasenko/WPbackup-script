#!/usr/bin/env python3


import sys
import os
import time
import json
import random
import boto3


# Text formatting
text_format = {
        'PURPLE' : '\033[95m',
        'CYAN' : '\033[96m',
        'DARKCYAN' : '\033[36m',
        'BLUE' : '\033[94m',
        'GREEN' : '\033[92m',
        'YELLOW' : '\033[93m',
        'RED' : '\033[91m',
        'BOLD' : '\033[1m',
        'UNDERLINE' : '\033[4m',
        'END' : '\033[0m'
        }

# Shared vars
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
CLUSTER_NAME = os.environ.get('CLUSTER_NAME', None)
SERVICE_NAME = os.environ.get('SERVICE_NAME', None)

# AWS init connection
session = boto3.Session(region_name=AWS_REGION)
ecs_client = session.client('ecs')


def update_service(image, tag):
    # Get current task definiton
    response = ecs_client.describe_task_definition(taskDefinition=SERVICE_NAME)
    current_definition = response['taskDefinition']
    current_revision = (
        current_definition['family'] +
        ':' +
        str(current_definition['revision']))
    current_image = current_definition['containerDefinitions'][0]['image']

    print(f'Previous revision was {current_revision}')
    print(f'Previous image was {current_image}')
    print('-' * 64)

    # Remove invalid keys for creating new task definition revision
    invalid_keys = (
        'taskDefinitionArn',
        'revision',
        'status',
        'requiresAttributes',
        'compatibilities')
    for key in invalid_keys:
        current_definition.pop(key)

    # Update docker image
    current_definition['containerDefinitions'][0]['image'] = image + ':' + tag

    # Create service task definition revision
    new_response = ecs_client.register_task_definition(**current_definition)
    new_definition = new_response['taskDefinition']
    new_revision = (
        new_definition['family'] +
        ':' +
        str(new_definition['revision']))
    new_image = new_definition['containerDefinitions'][0]['image']

    # Update service by new task definition revision
    service_info = {
            'cluster': CLUSTER_NAME,
            'service': SERVICE_NAME,
            'taskDefinition': new_revision}

    ecs_client.update_service(**service_info)

    print(f'Current revision is {new_revision}')
    print(f'Current image is {new_image}')
    print('-' * 64)

    # Derigister old task definition revisions
    unused_td_list = ecs_client.list_task_definitions(
            familyPrefix=SERVICE_NAME,
            status='ACTIVE',
            sort='ASC')['taskDefinitionArns'][:-1]

    for td in unused_td_list:
        ecs_client.deregister_task_definition(taskDefinition=td)


def migration_db(
        image,
        tag,
        consul_addr,
        execution_role_name,
        log_group,
        log_prefix):

    service_td = ecs_client.describe_task_definition(taskDefinition=SERVICE_NAME)['taskDefinition']

    with open('fargate_td_tmpl.json') as f:
        migration_td = json.load(f)

    # Render template
    log_options = {
            'awslogs-group': log_group,
            'awslogs-stream-prefix': log_prefix,
            'awslogs-region': AWS_REGION
            }
    sts_client = session.client('sts')
    account_id = sts_client.get_caller_identity()['Account']

    migration_td['containerDefinitions'][0]['image'] = image + ':' + tag
    migration_td['containerDefinitions'][0]['environment'] = service_td['containerDefinitions'][0]['environment']
    migration_td['containerDefinitions'][0]['name'] = service_td['containerDefinitions'][0]['name']
    migration_td['containerDefinitions'][0]['logConfiguration']['options'] = log_options
    migration_td['family'] = service_td['family'] + '-migration'
    migration_td['executionRoleArn'] = f'arn:aws:iam::{account_id}:role/{execution_role_name}'
    
    try:
        repo_creds = service_td['containerDefinitions'][0]['repositoryCredentials']
    except KeyError:
        print(text_format['BOLD'] + 
        "Repository credentials are missing in the original TD. It seems ECR is used." + 
        text_format['END'])
    else:
        migration_td['containerDefinitions'][0]['repositoryCredentials'] =  repo_creds
        print(text_format['BOLD'] + 
        "Additional repository credentials exist, so, external docker repo is used." + 
        text_format['END'])
    
    # Create DB migration task definition revision
    reg_response = ecs_client.register_task_definition(**migration_td)

    migration_td = reg_response['taskDefinition']
    migration_revision = (
        migration_td['family'] +
        ':' +
        str(migration_td['revision']))
    migration_image = migration_td['containerDefinitions'][0]['image']

    print(f'DB migration revision is {migration_revision}')
    print(f'DB migration image is {migration_image}')
    print('-' * 64)

    # Get cluster container instances subnets and SG
    ci_arns = ecs_client.list_container_instances(cluster=CLUSTER_NAME)['containerInstanceArns']
    ci_arn_random = random.choice(ci_arns).split()
    ci_info = ecs_client.describe_container_instances(cluster=CLUSTER_NAME, containerInstances=ci_arn_random)
    ec2_id = ci_info['containerInstances'][0]['ec2InstanceId'].split()

    ec2_client = session.client('ec2')

    ec2_info = ec2_client.describe_instances(InstanceIds=ec2_id)
    task_subnet_id = ec2_info['Reservations'][0]['Instances'][0]['SubnetId']
    ec2_sg_dict = ec2_info['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Groups']
    task_sg_ids = [x['GroupId'] for x in ec2_sg_dict]

    # Run migration task
    task_response = ecs_client.run_task(
        cluster=CLUSTER_NAME,
        taskDefinition=migration_revision,
        count=1,
        launchType='FARGATE',
        overrides={
            'containerOverrides': [
                {
                    'name': SERVICE_NAME,
                    'environment': [
                        {
                            'name': 'SERVICE_ROLE',
                            'value': 'console'
                        },
                        {
                            'name': 'CONSUL_HTTP_ADDR',
                            'value': consul_addr
                        }
                    ]
                }
            ]
        },
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': task_subnet_id.split(),
                'securityGroups': task_sg_ids,
                'assignPublicIp': 'DISABLED'
                }
            }
    )

    cluster_arn = task_response['tasks'][0]['clusterArn']
    task_arn = task_response['tasks'][0]['taskArn']

    # Waiting migration task finish
    waiter = ecs_client.get_waiter('tasks_stopped')
    waiter.wait(
        cluster=cluster_arn,
        tasks=task_arn.split(),
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': 7200
        }
    )
    print("Migration Task finished.")
    ecs_client.deregister_task_definition(taskDefinition=migration_revision)

    task_info = ecs_client.describe_tasks(
            cluster=cluster_arn,
            tasks=task_arn.split()
            )
    # Check migration container exit code
    exit_code = task_info['tasks'][0]['containers'][0]['exitCode']
    if exit_code == 0:
        migration_finished = True
    else:
        migration_finished = False

    # Get log from CloudWatch
    logs_client = session.client('logs')
    
    try:
        task_id = task_arn.split('/')[2]
    except IndexError:
        task_id = task_arn.split('/')[1]

    log_stream_name = f'{log_prefix}/{SERVICE_NAME}/{task_id}'
    events_list = logs_client.get_log_events(
            logGroupName=log_group,
            logStreamName=log_stream_name)

    message_list = [x['message'] for x in events_list['events']]
    print('\n'.join(message_list))

    return migration_finished


# Check Events log
def check_service_status(grace_period, retries):
    succes_status = f'(service {SERVICE_NAME}) has reached a steady state.'
    build_finished = False
    time.sleep(int(grace_period))
    for i in range(0, int(retries)):
        print("Checking service EventLog....")
        service_info = ecs_client.describe_services(
            cluster=CLUSTER_NAME,
            services=SERVICE_NAME.split())
        last_event = service_info['services'][0]['events'][0]
        if last_event['message'] != succes_status:
            time.sleep(10)
        else:
            build_finished = True
            break
    return build_finished


modes = ('migrate', 'update', 'check')
info = "Please, check documentation for additional info."

try:
    mode = sys.argv[1]
except IndexError:
    print(f"Need to specify parameter - {', '.join(modes)}!", info)
    sys.exit(2)
else:
    if mode not in modes:
        print(f"You set wrong parameter - not one of {', '.join(modes)}!", info)
        sys.exit(2)


if mode == "update":
    IMAGE = os.environ.get('IMAGE')
    TAG = os.environ.get('TAG', 'latest')
    update_service(
        image=IMAGE,
        tag=TAG
        )

elif mode == "migrate":
    IMAGE = os.environ.get('IMAGE')
    TAG = os.environ.get('TAG', 'latest')
    LOG_GROUP = os.environ.get('LOG_GROUP', '/aws/ecs/service-migration')
    LOG_PREFIX = os.environ.get('LOG_PREFIX', 'fargate')
    CONSUL_HTTP_ADDR = os.environ.get('CONSUL_HTTP_ADDR')
    EXECUTION_ROLE_NAME = os.environ.get('EXECUTION_ROLE_NAME', 'ecsTaskExecutionRole')
    status = migration_db(
        image=IMAGE,
        tag=TAG,
        consul_addr=CONSUL_HTTP_ADDR,
        execution_role_name=EXECUTION_ROLE_NAME,
        log_group=LOG_GROUP,
        log_prefix=LOG_PREFIX
        )

    if not status:
        print("DB migration failed!")
        sys.exit(1)

    print("DB migration is successfully done.")


elif mode == "check":
    GRACE_PERIOD = os.environ.get('GRACE_PERIOD', 30)
    CHECK_COUNT = os.environ.get('CHECK_COUNT', 18)

    status = check_service_status(
        grace_period=GRACE_PERIOD,
        retries=CHECK_COUNT)

    if not status:
        print("Health check failed!")
        sys.exit(1)

    print("Service is successfully updated.")
