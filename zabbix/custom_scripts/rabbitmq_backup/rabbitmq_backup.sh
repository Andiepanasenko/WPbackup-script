#/bin/bash

# include vars
if [ -z $1 ]
then
        echo "Config file is missing"
        exit 1
else

        if [ -s $1 ]; then source $1; else echo "Invalid config file"; exit 1; fi
fi

# Variables should be in config file
# AWS - path to aws
# BUCKET - name of s3 bucket
# FOLDER - folder on s3 bucket to store backups
# RABBIT_API http address of rabbitmq api with port
# RABBIT_CREDS - credentials of rabbitmq user with admins rights in format username:password
# ZABBIX_SERVER - IP or DNS name of zabbix host
# ZABBIX_HOST - Hostname of trap-host on zabbix server
# ZABBIX_KEY - Specify zabbix item key to send value to.

FILENAME=$(date +"rabbitmq_%Y%m%d_%H%M.bkp")

zabbix_send()
{
    /usr/bin/zabbix_sender -z $ZABBIX_SERVER -s $ZABBIX_HOST -k $ZABBIX_KEY -o $1
}

# define default profile if $PROFILE undefined
if [ -z ${PROFILE} ]; then PROFILE='default'; fi

# get rabbitmq JSON data
/usr/bin/curl -u $RABBIT_CREDS $RABBIT_API/api/definitions | /usr/bin/python -m json.tool > /tmp/$FILENAME && echo 'rabbittmq config was saved' || echo 'ERROR in backup rabbitmq'

#test if FILE exists and has a size greater than zero and put data in s3 bucket. After that send zabbix notification.
/usr/bin/test -s /tmp/$FILENAME && $AWS s3 cp /tmp/$FILENAME s3://$BUCKET/$FOLDER/$FILENAME --profile $PROFILE && zabbix_send 1 || zabbix_send 0

rm -f /tmp/$FILENAME

