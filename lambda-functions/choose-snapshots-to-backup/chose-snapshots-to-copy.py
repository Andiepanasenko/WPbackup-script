import re
import boto3
import json

session = boto3.Session()
rds_client = session.client('rds')
lambda_client = session.client('lambda')
sns_client = session.client('sns')


def lambda_handler(event, context):
    print('Starting at {}'.format(event['time']))

    """
    function to handle lambda tirgger
    :param event: raw copy of request
    :param context: aws meta info
    :return: response
    """
    print ("start execution")
    EXCLUDE_RE = [r"denis.+", r".+\-ro", r"dev\-.+"]

    session = boto3.Session()

    rds_client = session.client('rds')

    all_rds = rds_client.describe_db_instances()[u"DBInstances"]
    rds_to_backup = list()
    for instance in all_rds:
        try:
            db_name = instance[u'DBInstanceArn'].split(":")[6]

            # flag to check if DB should be excluded from backup-list
            exclude_db = False

            for regexp in EXCLUDE_RE:
                if re.match(regexp, db_name):
                    exclude_db = True
            rds_to_backup.append(instance[u'DBInstanceArn']) if not exclude_db else None
        except:
            pass

    # Get snapshots-list for all DB, choice the latest and share it for account
    for some_db in rds_to_backup:
        response = rds_client.describe_db_snapshots(
            DBInstanceIdentifier=some_db.split(":")[6],
            SnapshotType="manual",
            IncludePublic=False,
            IncludeShared=False, )

        # get last snapshot arn
        snapshot_arn = response[u'DBSnapshots'][-1][u'DBSnapshotArn'] if response[u'DBSnapshots'] else None
        if not snapshot_arn:
            continue

        snapshot_to_share = snapshot_arn.split(":")[6]
        payload = {"snapshot_to_share": snapshot_to_share, "snapshot_arn": snapshot_arn}
        print (payload)
        response = lambda_client.invoke(FunctionName="cross-account-backup", InvocationType="RequestResponse",
                                        Payload=json.dumps(payload))
        print (response)

        # test if errors exist ans send message to SNS
        if "errors" in response.keys():
            sns_client.publish(TopicArn='arn:aws:sns:us-east-1:811130481316:WARNING',
                               Message=response["errors"],
                               Subject='test-warning-sommetings went wrong while cross-account backup')
