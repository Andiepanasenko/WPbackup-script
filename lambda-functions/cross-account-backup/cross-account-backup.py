import boto3
import os
import json
import requests

BKP_ACCOUNT = os.environ['BKP_ACCOUNT']
API_KEY = os.environ['API_KEY']
API_URL = os.environ["API_URL"]
TEST_API = os.environ["TEST_API"]

session = boto3.Session()
rds_client = session.client('rds')
sns_client = session.client('sns')


def lambda_handler(event, context):
    print("========== EVENT =============")
    print (event)
    try:

        # share snapshot
        rds_client.modify_db_snapshot_attribute(AttributeName='restore',
                                                DBSnapshotIdentifier=event["snapshot_to_share"],
                                                ValuesToAdd=[BKP_ACCOUNT])

        print ("Snapshot %s was shared to copy" % event["snapshot_to_share"])

        # make request
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        api_gw_url = API_URL

        if TEST_API == "true":
            # test if API is working
            params = json.dumps({"ping": "send"})
            response = requests.post(api_gw_url, headers=headers, data=params)

        else:
            #copy snapshots
            response = requests.post(api_gw_url, headers=headers,
                                     data=json.dumps({event["snapshot_to_share"]: event["snapshot_arn"]}))

        if response.json().__class__ == dict:
            if "errors" in response.json().keys():
                print ('warning! sommetings went wrong while cross-account backup')

                print (response.json()["errors"])

                sns_client.publish(TopicArn='arn:aws:sns:us-east-1:811130481316:WARNING',
                                   Message=response.json()["errors"],
                                   Subject='warning! sommetings went wrong while cross-account backup')
        print(response.json())

    except Exception as e:
        errors = e.__str__()
        print ("exception errors", errors)
        sns_client.publish(TopicArn='arn:aws:sns:us-east-1:811130481316:WARNING',
                           Message=errors,
                           Subject='warning! sommetings went wrong while cross-account backup')

