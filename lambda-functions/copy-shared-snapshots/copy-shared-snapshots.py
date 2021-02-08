import boto3
import os
import json


def lambda_handler(event, context):
    """
    function to handle incoming request from AWS API
    :param event: raw copy of request to api
    :param context: aws meta info
    :return: response
    """

    print "start_handle"

    try:

        AWS_REGION = os.environ["REGION"]
        rds_client = boto3.client('rds', region_name=AWS_REGION)

        # test if it request from API GW (prod) or internal test
        if u"body" in event.keys():
            input_data = json.loads(event[u"body"])
        else:
            input_data = event

        if "ping" in input_data.keys():
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"pong": "pong"})}
        else:
            copy_result = copy_shared_snapshot(input_data, rds_client)
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(copy_result)}

    except Exception as e:
        errors = {"errors": e.__str__()}
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps(errors)}


def copy_shared_snapshot(input_json, client):
    """
    function to get object with shared snapshot ARNs should be copied from remote account
    :param input_json: JSON body object from request to API. Should contain dict
           {"some_snapshot_name" : "aws:::::some:arn", "another_snapshot_name" : "aws:::::another:arn"}
    :return: list of copy shared snapshot results (from boto3)
    """

    copied_snapshots = list()
    for snap in input_json.keys():
        cp_result = client.copy_db_snapshot(SourceDBSnapshotIdentifier=input_json[snap], TargetDBSnapshotIdentifier=snap)

        # turn datetime obj into string for JSON serializing
        cp_result[u'DBSnapshot']['InstanceCreateTime'] = cp_result[u'DBSnapshot']['InstanceCreateTime'].isoformat()

        copied_snapshots.append(cp_result[u'DBSnapshot'])

    return copied_snapshots

