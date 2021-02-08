Script rabittmq_backup.sh for creating scheduling backups for rabbitmq.
Scripts get JSON backup data by API and store it in s3 amazon bucket.
For working script config file (1st parameter of a script - $1) is mandatory.
In config file should be defined next variables : 

* AWS - path to aws (`which aws` to get it)
* BUCKET - name of s3 bucket
* FOLDER - folder on s3 bucket to store backups
* RABBIT_API - HTTP address of rabbitmq API with port
* RABBIT_CREDS - credentials of rabbitmq user with admins rights in format username: password
* ZABBIX_SERVER - IP or DNS name of zabbix host
* ZABBIX_HOST - Hostname of trap-host on zabbix server
* ZABBIX_KEY - Specify zabbix item key to send a value to.
```bash
Config example:

# Variables should be in config file
# AWS - path to aws
# BUCKET - name of s3 bucket
# FOLDER - folder on s3 bucket to store backups
# RABBIT_API http address of rabbitmq api with port
# RABBIT_CREDS - credentials of rabbitmq user with admins rights in format username:password
# ZABBIX_SERVER - IP or DNS name of zabbix host
# ZABBIX_HOST - Hostname of trap-host on zabbix server
# ZABBIX_KEY - Specify zabbix item key to send value to.
# PROFILE - profile of aws cli. (OPTIONAL). If it dosen't define - will use profile "default". 

AWS="/usr/bin/aws"
BUCKET="pdffiller-some-backet"
FOLDER="rabbitmq_backups"

RABBIT_API="http://internal-prod-rabbitmq-some-load-balancer.amazonaws.com:15672"
RABBIT_CREDS="someuser:olololmegapassword"

ZABBIX_SERVER="zabbix-server.pdf.int"
ZABBIX_HOST="Cron"
ZABBIX_KEY="cron.rabbitmq_backup.status"

```
