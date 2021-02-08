# AWS RDS - Drop old manual snapshots

This tool allows to delete manual AWS RDS snapshots for specific databases, leaving only N latest.


### Prerequisites

*   [Docker](https://docs.docker.com/install/)
*   [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)


### Usage

##### *AWS scenario*
*   Create an ECR repo
*   Build, tag and push docker image to repo
*   Create appropriate IAM Roles and Policies<br>
My test role contained two policies - custom

| Service       | Access level              | Resource      |
|---------------|-----------------------    |---------------|
| CloudWatch    | Full access               | All resources |
| RDS           | List: DescribeDBSnapshots | All resources |
|               | Write: DeleteDBSnapshot   |               |

and built in one
> AmazonEC2ContainerServiceforEC2Role

*   Create ECS cluster task definition.
*   Enable default Cloudawatch logging (optional)<br>
Set the following environment variables for the container


 | Variable           | Example                       |
 |--------------------|-------------------------------|
 | `AWS_REGION`       | us-east-1                     |
 | `DATABASES`        | dev-zabbix,dev-zabbix-upgrade |
 | `BACKUPS_TO_KEEP`  | 5                             |


*   Create a Cloudwatch rule.
*   Select cluster, task definition, run schedule inside the rule

##### *Manual scenario*

*   Build docker image
```
docker build -t aws_rds_drop_manual_snapshots .
```
*   Run it with set of environment variables mentioned above + credentials for AWS CLI
```
docker run \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=MyAWSAccessKey \
  -e AWS_SECRET_ACCESS_KEY=MyAWSSecretAccessKey \
  -e DATABASES='dev-zabbix,dev-zabbix-upgrade' \
  -e BACKUPS_TO_KEEP=5 \
  aws_rds_drop_manual_snapshots
```
