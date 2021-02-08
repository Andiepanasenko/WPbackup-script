#!/usr/bin/env python3


import time


def get_spec_pod(api_client, namespace, app_name_label, role='web', container_name='app'):
    """
    :type container_name: string
    :type role: string
    :type app_name_label: string
    :type namespace: string
    :type api_client: object
    """
    pod_configuration = {}
    apps_v1 = api_client.AppsV1Api()
    deployment = apps_v1.list_namespaced_deployment(namespace=namespace,
                                                    label_selector=f'app={app_name_label},role={role}')
    deployment_spec_pod = deployment.items[0].spec.template.spec
    pod_configuration['image_pull_secrets'] = deployment_spec_pod.image_pull_secrets
    pod_configuration['container'] = None
    for c in deployment_spec_pod.containers:
        if c.name == container_name:
            for env in c.env:
                if env.name == 'SERVICE_ROLE':
                    env.value = 'console'
                    break
            pod_configuration['container'] = c
            break

    assert pod_configuration['container'] is not None, f'Container name {container_name} is not found.'

    return pod_configuration


def create_job_object(api_client, job_name, app_name_label, image, pod_spec, container_name='app'):
    """
    :type api_client: object
    :type app_name_label: string
    :type job_name: string
    :type image: string
    :type pod_spec: dict
    :type container_name: string
    """
    container_args = ['bash', '/app/docker/provision/migration.sh']
    job_resources = {
        'requests': {'cpu': '256m', 'memory': '512Mi'},
        'limits': {'cpu': '256m', 'memory': '512Mi'}
    }
    container = api_client.V1Container(
        name=container_name,
        image_pull_policy='Always',
        image=image,
        args=container_args,
        env=pod_spec['container'].env,
        env_from=pod_spec['container'].env_from,
        resources=api_client.V1ResourceRequirements(**job_resources)
    )
    template = api_client.V1PodTemplateSpec(
        metadata=api_client.V1ObjectMeta(labels=dict(app=app_name_label, role='console')),
        spec=api_client.V1PodSpec(restart_policy='Never', image_pull_secrets=pod_spec['image_pull_secrets'],
                                  containers=[container]))

    spec = api_client.V1JobSpec(
        template=template,
        backoff_limit=0
    )
    job = api_client.V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=api_client.V1ObjectMeta(name=job_name, labels=dict(app=app_name_label, role='console')),
        spec=spec)

    return job


def create_job(api_client, namespace, body):
    """
    :type api_client: object
    :type namespace: string
    :type body: object
    """
    batch_v1 = api_client.BatchV1Api()
    api_response = batch_v1.create_namespaced_job(
        body=body,
        namespace=namespace)

    return api_response


def check_job_status(api_client, api_config, namespace, job_name, app_name_label, grace_period, delay,
                     container_name='app'):
    """
    :type container_name: string
    :type delay: integer
    :type grace_period: integer
    :type app_name_label: string
    :type job_name: string
    :type namespace: string
    :type api_config: object
    :type api_client: object
    """
    complex_status = {}
    core_v1 = api_client.CoreV1Api()
    batch_v1 = api_client.BatchV1Api()

    time.sleep(grace_period)

    # Check if job stuck (image cannot be pulled as example)
    for i in range(0, 4):
        job_pod_info = core_v1.list_namespaced_pod(namespace, label_selector=f'app={app_name_label},role=console')
        for c in job_pod_info.items[0].status.container_statuses:
            if c.name == container_name:
                job_pod_info_container_state = c.state
                break

        if job_pod_info_container_state.waiting is not None:
            complex_status['job_pod_waiting'] = job_pod_info_container_state.waiting.reason
            complex_status['job_success'] = None
            return complex_status

        time.sleep(delay)

    # Check job running status
    while True:
        try:
            job_info = batch_v1.read_namespaced_job_status(job_name, namespace, pretty=True)
        except api_client.rest.ApiException as error:
            # K8s token can expire, request new one
            api_config.load_kube_config()
            batch_v1 = api_client.BatchV1Api()
            job_info = batch_v1.read_namespaced_job_status(job_name, namespace, pretty=True)

        if job_info.status.failed or job_info.status.succeeded:
            complex_status['job_pod_waiting'] = None
            complex_status['job_success'] = job_info.status.succeeded
            api_config.load_kube_config()
            return complex_status

        time.sleep(delay)



def delete_job(api_client, namespace, job_name):
    """
    :type job_name: string
    :type namespace: string
    :type api_client: object
    """
    batch_v1 = api_client.BatchV1Api()
    api_response = batch_v1.delete_namespaced_job(
        name=job_name,
        namespace=namespace,
        body=api_client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))

    return api_response


def get_job_pod_log(api_client, namespace, app_name_label, container_name='app'):
    """
    :type container_name: string
    :type app_name_label: string
    :type namespace: string
    :type api_client: object
    """
    core_v1 = api_client.CoreV1Api()
    # Get job task pod specs
    job_pod_info = core_v1.list_namespaced_pod(namespace, label_selector=f'app={app_name_label},role=console')
    job_pod_name = job_pod_info.items[0].metadata.name
    # Get job task pod logs
    job_pod_log = core_v1.read_namespaced_pod_log(job_pod_name, namespace, container=container_name)

    return job_pod_log
