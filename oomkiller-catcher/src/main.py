from docker import DockerClient
from datadog import initialize, statsd
from os import getenv

PROVIDER = getenv('PROVIDER', 'ecs')
ENVIRONMENT = getenv('ENVIRONMENT', 'unknown')
INFRA = getenv('INFRA', 'unknown')
STATSD_HOST = getenv('STATSD_HOST', '127.0.0.1')
STATSD_PORT = getenv('STATSD_PORT', 8125)
STATSD_PREFIX = getenv('STATSD_PREFIX', "container")

options = {
    'statsd_host': STATSD_HOST,
    'statsd_port': STATSD_PORT
}


def main():
    client = DockerClient(base_url='unix://var/run/docker.sock')

    initialize(**options)

    events = client.events(decode=True)
    for event in events:
        if event["Action"] == 'oom':
            if PROVIDER == 'k8s':
                service_name = "-".join(event["Actor"]["Attributes"]["io.kubernetes.pod.name"].split("-")[:-2])
                cluster_name = "io.kubernetes.pod.namespace"
            elif PROVIDER == 'ecs':
                service_name = event["Actor"]["Attributes"]["com.amazonaws.ecs.container-name"]
                cluster_name = "com.amazonaws.ecs.cluster"
            with statsd.timed(f"{STATSD_PREFIX}.oom.killed",
                            tags=[
                                "service:{}".format(service_name),
                                "cluster:{}".format(event["Actor"]["Attributes"][cluster_name]),
                                "infra:{}".format(INFRA),
                                "env:{}".format(ENVIRONMENT)
                            ]) as timed:
                print(timed)


if __name__ == "__main__":
    main()
