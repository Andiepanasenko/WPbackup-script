# ecs-service-update 

One shot docker container for ecs service updating, checking container status after deploy, run migrations.
[DockerHub Repo], stable version is _v1.1.*_ , _v1.0.*\_as_ is deprecated.

## Local install

### Build image

```bash
docker build -t ecs-service-update .
```

## Modes

Mode is the first script parameter and set as container command.
Modes are independent from each other, you can run it in any order.
But recommended next:
1. migrate
2. update
3. check

_Required environment variables are highlighted **bold text**!_

### 1. update 

Create new task definition revision with new image tag and update ECS service.

Environment variables:
- **AWS_DEFAULT_REGION**
- **SERVICE_NAME**
- **CLUSTER_NAME**
- **IMAGE**
- **TAG**

Example:

```bash
docker run --rm \
  -e "SERVICE_NAME=${SERVICE_NAME}" \
  -e "CLUSTER_NAME=${CLUSTER_NAME}" \
  -e "IMAGE=${ECR_IMAGE_OR_CUSTOM_IMAGE}" \
  -e "TAG=${NEW_IMAGE_TAG}" \
ecs-service-update update
```
### 2. Check

Checks ECS events log when service has reached a steady state. 
This checking locks agent, but very useful simple monitoring.

Environment variables:
- **AWS_DEFAULT_REGION**
- **SERVICE_NAME**
- **CLUSTER_NAME**
- GRACE_PERIOD - wait before the first check, `default 30 sec`
- CHECK_COUNT - count of check iterations every 10 sec, `default 18`

Example:

```bash
docker run --rm \
  -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}"\
  -e "SERVICE_NAME=${SERVICE_NAME}" \
  -e "CLUSTER_NAME=${CLUSTER_NAME}" \
  -e "GRACE_PERIOD="60" \
  -e "CHECK_COUNT="24" \
ecs-service-update check
```

### 3. migrate

Migrate mode just runs `/app/docker/provision/migration.sh` script as a container command.
It creates FARGATE compatible task definition from the `fargate_td_tmpl.json` setting:
- `image` from the env vars
- `environment` from the original container definition
- `name` from the original container definition
- `family` from the original container definition + '-migration' ending
- `executionRoleArn` from the env vars
- `logConfiguration` from the env vars

Run this FARGATE task definitions as one shot task overwriting next env vars:
- `SERVICE_ROLE` -> `console`
- `CONSUL_HTTP_ADDR` -> internal consul cluster endpoint, `CONSUL_HTTP_ADDR` env var

_**Migration task use `awsvpc` network type for container and we have to configure it. 
Script do it automatically using subnet and security group of one of the cluster container instances(random choice).
So, cluster should has at list one running container instance! 
Otherwise, the task will fail and need to create additional env vars for network configuration.**_

Environment variables:
- **AWS_DEFAULT_REGION**
- **SERVICE_NAME**
- **CLUSTER_NAME**
- **IMAGE**
- **TAG**
- **CONSUL_HTTP_ADDR** - internal consul cluster endpoint 
- LOG_GROUP - cloudwatch log group, default `/aws/ecs/service-migration`, _**need to be created in AWS**_
- LOG_PREFIX - log  stream prefix in log group, default `fargate`
- EXECUTION_ROLE_NAME - role for FARGATE task execution, default `ecsTaskExecutionRole`, _**need to be created in AWS**_

As you can see, you should create two AWS resources by yourself.
`ecsTaskExecutionRole` can use AWS managed policy `AmazonECSTaskExecutionRolePolicy`. 
Also if your service run from non ECR image(DockerHub as example) you should add appropriate policy to get access to external repo creds. 

Example:

```bash
docker run --rm \
  -e "SERVICE_NAME=${SERVICE_NAME}" \
  -e "CLUSTER_NAME=${CLUSTER_NAME}" \
  -e "IMAGE=${ECR_IMAGE_OR_CUSTOM_IMAGE}" \
  -e "TAG=${NEW_IMAGE_TAG}" \
  -e "EXECUTION_ROLE_NAME=${CUSTOM_ROLE_NAME}"
  -e "LOG_GROUP=${CUSTOM_LOG_GROUP}" \
  -e "LOG_PREFIX=${CUSTOM_LOG_PREFIX}" \
  -e "CONSUL_HTTP_ADDR=http://consul.as-stage.int" \
ecs-service-update migrate
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
ecs-service-update ${mode}
```

Be aware, you only need **AWS_SESSION_TOKEN** env variable if you are using credentials from another IAM role!

**P.S.** airSlate TC templates use credentials from ecs service attached role, 
so we need to parse creds and to pass it inside the container. 
To fix it  will attache appropriate IAM role to underlying ec2 instances.

[DockerHub Repo]:https://cloud.docker.com/u/pdffiller/repository/docker/pdffiller/ecs-service-update/general