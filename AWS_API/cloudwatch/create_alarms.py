"""
This module create WARNING and CRITICAL alarms for RDS databases.
"""

import boto3

SNS = 'arn:aws:sns'
REGION = ''
ACCOUNT_ID = ''

WARNING = SNS + ':' + REGION + ':' + ACCOUNT_ID + ':' + 'WARNING'
CRITICAL = SNS + ':' + REGION + ':' + ACCOUNT_ID + ':' + 'CRITICAL'

def create_alarm(db_name, channel, percent_in_bytes, alarm_name_prefix):
    """
    Create or update existing alarm in Cloudwatch.

    Args:
        db_name (str): DBInstanceIdentifier from RDS
        channel (str): AWS ARN channel for send notification
        percent_in_bytes (int): bytes. If less - start alarm
        alarm_name_prefix (str):

    Returns:
        response (json):
    """
    response = CLOUDWATCH.put_metric_alarm(
        AlarmName=alarm_name_prefix + ' | mysql | FreeStorageSpace | ' + db_name,
        AlarmDescription='',

        ActionsEnabled=True, # Enable OK and ALARM.
        OKActions=[channel], # Channel which get info about OK action.
        AlarmActions=[channel], # Channel which get info about ALARM action.
        TreatMissingData='breaching', # analog "bad" in GUI.

        MetricName='FreeStorageSpace',
        Namespace='AWS/RDS',
        Statistic='Average',
        Dimensions=[
            {
                'Name': 'DBInstanceIdentifier',
                'Value': db_name
            },
        ],
        Period=300, # 5 minutes in seconds.
        EvaluationPeriods=1, # Period after which activate ALARM.
        Threshold=percent_in_bytes,
        ComparisonOperator='LessThanThreshold',
    )

    return response


# Get data about DB's from RDS
CLIENT = boto3.client('rds')
RDS = CLIENT.describe_db_instances()
DB_IN_GB = {}

for i in range(len(RDS['DBInstances'])):
    name = RDS['DBInstances'][i]['DBInstanceIdentifier']
    DB_IN_GB[name] = RDS['DBInstances'][i]['AllocatedStorage']

# Create alarms in Cloudwatch
CLOUDWATCH = boto3.client('cloudwatch')
for db in DB_IN_GB:
    fifteen_percent = 0.15 * DB_IN_GB[db] * 1073741824 # Last - convert GB to Bytes.
    ten_percent = 0.1 * DB_IN_GB[db] * 1073741824 # Last - convert GB to Bytes.

    create_alarm(db, WARNING, fifteen_percent, 'WARNING')
    create_alarm(db, CRITICAL, ten_percent, 'CRITICAL')
