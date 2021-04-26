import requests
from tqdm import tqdm
import boto3
from boto3.s3.transfer import transferconfig
import re
import sys
import os
import datetime


lst = sys.argv[1:]
s3 = boto3.resource('s3')

gb = 1024 ** 3
transfer_config = transferconfig(multipart_threshold=5 * gb, max_concurrency=4)
bucket_name = 'mr-prod-wpengine-backup-20201022121325811200000001'
min_date = datetime.datetime.now() - datetime.timedelta(days=30)


def processing_backup(item, config):
    """ for item in lst:"""
    pattern = re.search(r'\/([a-za-z0-9-]+\.zip)', item)
    if pattern is none:
        print("url does not match")
        return "not completed"
    article = re.sub(r'-[a-za-z0-9]+(:?\.zip)', '.zip', pattern.group(1))
    print("start process %s" % article)
    if 'snblog-live' in article:
        folder = "blog.signnow.com/"
    elif "signnow2016-live" in article:
        folder = "university.signnow.com/"
    elif 'airslate-live' in article:
        folder = "blog.airslate.com/"
    elif 'pdffillerblog-live' in article:
        folder = "blog.pdffiller.com/"
    elif 'sellmyforms-live' in article:
        folder = "blog.sellmyforms.com/"
    elif 'uslegal-live' in article:
        folder = "uslegal.com/"
    else:
        folder = "unknown folder"
        raise valueerror(folder)
    response = requests.get(item, stream=true)

    with open(article, "wb") as file:
        for chunk in tqdm(response.iter_content(chunk_size=5000000*20)):
            print("got chunk response")
            if chunk:
                file.write(chunk)

    print(article)
    s3.meta.client.upload_file(
        bucket=bucket_name,
        config=config,
        key=folder + article,
        filename=article
        )
    os.remove(article)


def delete_expired():
    """delete old back_up from s3"""
    s3_client = boto3.client('s3')
    bucket_objects = s3_client.list_objects(bucket=bucket_name)['contents']

    bucket_objects_to_delete = list(
        map(
            lambda y: {'key': y['key']},
            filter(
                lambda x: '.zip' in x['key'] and x['lastmodified'].date() < min_date.date(),
                bucket_objects
            )
        )
    )

    if bucket_objects:
        s3_client.delete_objects(
            bucket=bucket_name,
            delete={'objects': bucket_objects_to_delete}
        )


if __name__ == "__main__":
    for i in lst:
        processing_backup(i, transfer_config)

    delete_expired()



