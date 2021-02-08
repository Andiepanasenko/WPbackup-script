# OOMKiller-catcher - catch oom-killer events from docker socket

Exporter that connects to nodes docker socket and catch oom-events and sends them to statsd as timed metrics.


### Prerequisites

*   [Python 3](https://www.python.org/downloads/)
*   [Datadog python lib](https://github.com/DataDog/datadogpy)
*   [Docker python lib](https://github.com/docker/docker-py)


### Usage

##### *ECS scenario*
*   Create an ECR repo
*   Build, tag and push docker image to repo
*   Deploy container per cluster(daemon) where you need to catch oom events with `docker.sock` mounted to `/var/run/docker.sock`<br>

Environment variables for the container:

| Variable        | Descriotion                               | Default       |
|-----------------|-------------------------------------------|---------------|
| `PROVIDER`      | Used for docker events filtering(ecs)     | ecs           |
| `ENVIRONMENT`   | Environment metric tag                    | unknown       |
| `INFRA`         | Infra metric tag                          | unknown       |
| `STATSD_HOST`   | Statsd host address                       | 127.0.0.1     |
| `STATSD_PORT`   | Statsd port                               | 8125          |
| `STATSD_PREFIX` | Metrics prefix                            | container     |
##### *K8S scenario*

*   Create an ECR repo
*   Build, tag and push docker image to repo
*   Deploy container to k8s as daemon to catch oom events with `docker.sock` mounted to `/var/run/docker.sock`<br>

Environment variables for the container:

| Variable        | Descriotion                               | Default       |
|-----------------|-------------------------------------------|---------------|
| `PROVIDER`      | Used for docker events filtering(set k8s) | ecs           |
| `ENVIRONMENT`   | Environment metric tag                    | unknown       |
| `INFRA`         | Infra metric tag                          | unknown       |
| `STATSD_HOST`   | Statsd host address                       | 127.0.0.1     |
| `STATSD_PORT`   | Statsd port                               | 8125          |
| `STATSD_PREFIX` | Metrics prefix                            | container     |