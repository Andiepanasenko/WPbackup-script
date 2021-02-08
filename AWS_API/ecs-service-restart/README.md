# ecs-service-restart 

One shot docker container for ecs services restart.

## Local install

### Build image

```bash
docker build -t ecs-service-restart .
```
_Required environment variables are highlighted **bold text**!_

### Restart all services in cluster

Lists services from CLUSTER_NAME and restarts them in loop.

#### EXCLUDED SERVICES:
- gcp-node-exporter
- registrator
- dns-cache
- gcp-cadvisor
- jaeger-agent
- zabbix-agent
- consul-agent
- filebeat

Environment variables:
- **AWS_DEFAULT_REGION**
- **CLUSTER_NAME**

Example:

```bash
docker run --rm \
  -e "CLUSTER_NAME=${CLUSTER_NAME}"
```

## Notices
If appropriate IAM role is not attached to TC agent instances 
(exactly ec2 instances, because containers run using host mounted docker socket), 
you have to add AWS credentials, like 

```bash
docker run --rm \
  -e "AWS_DEFAULT_REGION=${AWS_REGION}"
  -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -e "AWS_SESSION_TOKEN"=${AWS_SESSION_TOKEN} \
  .........
```

Be aware, you only need **AWS_SESSION_TOKEN** env variable if you are using credentials from another IAM role!

**P.S.** airSlate TC templates use credentials from ecs service attached role, 
so we need to parse creds and to pass it inside the container. 
To fix it  will attache appropriate IAM role to underlying ec2 instances.
