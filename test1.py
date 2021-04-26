import requests
from tqdm import tqdm
import boto3
from boto3.s3.transfer import TransferConfig
import re
import sys
import os
import datetime

min_date = datetime.datetime.now() - datetime.timedelta(days=30)
print(min_date.date())
s3_client = boto3.client('s3')
bucket_objects = s3_client.list_objects(Bucket='mr-prod-wpengine-backup-20201022121325811200000001')['Contents']

bucket_objects_to_delete = list(
    map(
        lambda y: {'Key': y['Key']},
        filter(
            lambda x: '.zip' in x['Key'] and x['LastModified'].date() < min_date.date(),
            bucket_objects
        )
    )
)
print(bucket_objects)

if bucket_objects:
    s3_client.delete_objects(
        Bucket='mr-prod-wpengine-backup-20201022121325811200000001',
        Delete={'Objects': bucket_objects_to_delete}
    )
