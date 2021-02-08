#!/usr/bin/env python3


import os
import sys

from kubernetes import client, config

import migration
import update

NAMESPACE = os.environ.get('NAMESPACE')
APP_NAME_KEY = os.environ.get('APP_NAME_KEY', 'app')
APP_NAME = os.environ.get('APP_NAME')
IMAGE = os.environ.get('IMAGE')
GRACE_PERIOD = os.environ.get('GRACE_PERIOD', 10)
DELAY = os.environ.get('DELAY', 5)
RETRIES = os.environ.get('RETRIES', 20)
FORCE_UPDATE = os.environ.get('FORCE_UPDATE', 'false')

# Text formatting
text_format = {
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'DARKCYAN': '\033[36m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}

modes = ('migrate', 'update')
info = 'Please, check documentation for additional info.'

try:
    mode = sys.argv[1]
except IndexError:
    print(f'Need to specify parameter - {", ".join(modes)}!', info)
    sys.exit(3)
else:
    if mode not in modes:
        print(f'You set wrong parameter - not one of {", ".join(modes)}!', info)
        sys.exit(3)

if not NAMESPACE or not APP_NAME or not IMAGE:
    print(f'Need to specify all mandatory env vars - NAMESPACE,APP_NAME,IMAGE!', info)
    sys.exit(3)


config.load_kube_config()


def run_migration():
    job_name = APP_NAME + '-batch-job'
    parent_pod_spec = migration.get_spec_pod(client, NAMESPACE,
                                             app_name_label=APP_NAME)
    job_object = migration.create_job_object(client, job_name,
                                             app_name_label=APP_NAME,
                                             image=IMAGE,
                                             pod_spec=parent_pod_spec)
    migration.create_job(client, NAMESPACE,
                         body=job_object)
    status = migration.check_job_status(client, config, NAMESPACE, job_name,
                                        app_name_label=APP_NAME,
                                        grace_period=int(GRACE_PERIOD),
                                        delay=int(DELAY))

    if status['job_pod_waiting'] is not None:
        print('#' * 32, f'Migration container cannot start, reason - {status["job_pod_waiting"]}', sep='\n')
        migration.delete_job(client, NAMESPACE, job_name)
        sys.exit(2)

    if status['job_success']:
        print(migration.get_job_pod_log(client, NAMESPACE,
                                        app_name_label=APP_NAME))
        print('#' * 32, 'Migration succeeded.', sep='\n')
        migration.delete_job(client, NAMESPACE, job_name)
    else:
        print(migration.get_job_pod_log(client, NAMESPACE,
                                        app_name_label=APP_NAME))
        print('#' * 32, 'Migration failed.', sep='\n')
        migration.delete_job(client, NAMESPACE, job_name)
        sys.exit(1)


def run_update():
    force_update = True if FORCE_UPDATE == 'true' else False
    apps_v1_client = client.AppsV1Api()
    components = update.get_service_components(apps_v1_client, NAMESPACE,
                                               app_name_key=APP_NAME_KEY,
                                               app_name_label=APP_NAME)

    for component in components:
        resp_list = []
        for d in component:
            resp = update.update_deployment(apps_v1_client, NAMESPACE, IMAGE,
                                            deployment=d,
                                            force_update=force_update)
            resp_list.append(resp)
        for r in resp_list:
            if r is None:
                print(f'You try to deploy the same image tag {IMAGE} and force_deploy is disabled!')
            else:
                status = update.check_rs_status(apps_v1_client, NAMESPACE,
                                                deployment=r,
                                                grace_period=int(GRACE_PERIOD),
                                                delay=int(DELAY),
                                                retries=int(RETRIES))
                if status:
                    print(f'Update is successful for {r.metadata.name} deployment.')
                else:
                    print(f'Update is failed for {r.metadata.name} deployment.')
                    print('Stop deployment process!!!')
                    sys.exit(1)
        if component:
            print('Service component is updated.', '#' * 32, sep='\n')


if mode == 'migrate':
    run_migration()
elif mode == 'update':
    run_update()
