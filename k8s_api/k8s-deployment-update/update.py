#!/usr/bin/env python3


import time
from datetime import datetime


def get_service_components(apps_v1_client, namespace, app_name_label, app_name_key='app', roles=('worker', 'web', 'cron')):
    """
    :type roles: tuple
    :type app_name_label: string
    :type namespace: string
    :type apps_v1_client: object
    """
    ordered_components = []
    for r in roles:
        deployment_list = apps_v1_client.list_namespaced_deployment(namespace=namespace,
                                                                    label_selector=f'{app_name_key}={app_name_label},role={r}')
        ordered_components.append(deployment_list.items)
    return ordered_components


def update_deployment(apps_v1_client, namespace, image, deployment, force_update, container_name='app'):
    """
    :type force_update: bool
    :type container_name: string
    :type image: string
    :type deployment: object
    :type namespace: string
    :type apps_v1_client: object
    """
    previous_image = None
    update_patch = {}
    annotations_patch = {}
    # Update container image
    for c in deployment.spec.template.spec.containers:
        if c.name == container_name:
            previous_image = c.image
            update_patch = {'spec': {
                '$setElementOrder/containers': [{'name': container_name}],
                'containers': [{'image': image, 'name': container_name}]}}
            break

    assert previous_image is not None, f'Container name {container_name} is not found.'

    if previous_image == image:
        if force_update:
            # kubectl rollout restart deployment
            # https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubectl/pkg/polymorphichelpers/objectrestarter.go#L41
            annotations_patch = {'metadata': {
                'annotations': {'kubectl.kubernetes.io/restartedAt': datetime.utcnow().isoformat('T') + 'Z'}}}
        else:
            return None

    # Update the deployment
    result_patch = {'spec': {'template': {**update_patch, **annotations_patch}}}
    resp = apps_v1_client.patch_namespaced_deployment(
        name=deployment.metadata.name,
        namespace=namespace,
        body=result_patch
    )

    return resp


def check_deployment_status(apps_v1_client, namespace, deployment, grace_period, delay):
    """
    :type delay: integer
    :type grace_period: integer
    :type deployment: object
    :type namespace: string
    :type apps_v1_client: object
    """
    time.sleep(grace_period)
    # Check deployment status
    while True:
        deployment_info = apps_v1_client.read_namespaced_deployment_status(deployment.metadata.name, namespace,
                                                                           pretty=True)
        if deployment_info.status.conditions[1].reason == 'NewReplicaSetAvailable':
            return True
        if deployment_info.status.conditions[1].reason == 'ProgressDeadlineExceeded':
            return False
        time.sleep(delay)


def check_rs_status(apps_v1_client, namespace, deployment, grace_period, delay, retries):
    """
    :type retries: integer
    :type delay: integer
    :type grace_period: integer
    :type deployment: object
    :type namespace: string
    :type apps_v1_client: object
    """
    time.sleep(grace_period)

    d_labels_dict = deployment.metadata.labels
    d_labels_list = [f'{k}={d_labels_dict[k]}' for k in d_labels_dict]
    d_labels_string = ','.join(d_labels_list)

    d_next_revision = int(deployment.metadata.annotations['deployment.kubernetes.io/revision']) + 1

    for i in range(0, retries):
        resp = apps_v1_client.list_namespaced_replica_set(namespace, label_selector=d_labels_string)
        for rs in resp.items:
            if rs.metadata.annotations['deployment.kubernetes.io/revision'] == str(d_next_revision):
                desired_replicas = int(rs.metadata.annotations['deployment.kubernetes.io/desired-replicas'])
                ready_replicas = rs.status.ready_replicas
                if ready_replicas == desired_replicas:
                    return True
                break
        time.sleep(delay)

    return False
