import os
import boto3


def get_manual_snapshots_dict(client, db_instance_identifier_list):
    """
    Method to get all the manual snapshot lists for particular database
    :param client: Client session to AWS CLI
    :param db_instance_identifier_list: List with DB Instance IDs
    :return: Dictionary with key=DB_Instance_Name, value={Snapshot_ID1, Snapshot_ID2, ...}
    """
    manual_snapshots = dict()

    for db_inst_id in db_instance_identifier_list:
        snapshot_objects = client.describe_db_snapshots(DBInstanceIdentifier=db_inst_id, SnapshotType='manual')[
            "DBSnapshots"]
        snapshot_objects.sort(key=lambda x: x['SnapshotCreateTime'], reverse=True)
        manual_snapshots[db_inst_id] = manual_snapshots.get(db_inst_id, list())
        snapshot_lst = manual_snapshots[db_inst_id]
        [snapshot_lst.append(i['DBSnapshotIdentifier']) for i in snapshot_objects]

    return manual_snapshots


def drop_manual_snapshots(client, manual_snapshots, num_of_snapshots_to_keep=5):
    """
    Delete all manual snapsnots, leave only N of most recent ones
    :param client: Client session to AWS CLI
    :param manual_snapshots: Dictionary containing snapshot IDs
    :param num_of_snapshots_to_keep: Desired number of latest snapshots to keep
    :return:
    """
    for db_instance in manual_snapshots.keys():
        snapshot_list = manual_snapshots[db_instance]
        print('Instance: {}, Manual snapshot count: {}, Snapshots to keep: {}'.format(
            db_instance, len(snapshot_list), num_of_snapshots_to_keep
        ))
        if len(snapshot_list) <= int(num_of_snapshots_to_keep):
            print('Nothing deleted')
            continue
        for i in range(0, num_of_snapshots_to_keep):
            snapshot_list.pop(0)
        for snapshot_id in snapshot_list:
            try:
                response = client.delete_db_snapshot(
                    DBSnapshotIdentifier=snapshot_id
                )
                print('Instance: {}, Snapshot: {}, Status: {}'.format(
                    response["DBSnapshot"]["DBInstanceIdentifier"],
                    response["DBSnapshot"]["DBSnapshotIdentifier"],
                    response["DBSnapshot"]["Status"],
                ))
                print()
            except BaseException as e:
                print('Cannot delete {}'.format(snapshot_id))
                print(e)
                continue
    return


def lambda_handler(event, context):
    AWS_REGION = os.environ['AWS_REGION']
    DATABASES = os.environ['DATABASES'].split(',')
    BACKUPS_TO_KEEP = int(os.environ['BACKUPS_TO_KEEP'])

    session = boto3.Session()
    rds_client = session.client('rds', region_name=AWS_REGION)

    manual_snapshots_dict = get_manual_snapshots_dict(rds_client, DATABASES)
    drop_manual_snapshots(rds_client, manual_snapshots_dict, BACKUPS_TO_KEEP)

    return None


if __name__ == "__main__":
    lambda_handler(None, None)
