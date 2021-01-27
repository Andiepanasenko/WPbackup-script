import requests
from tqdm import tqdm
import boto3
from boto3.s3.transfer import TransferConfig
import re
import sys


lst = sys.argv[1:]
s3 = boto3.resource('s3')

GB = 1024 ** 3
transfer_config = TransferConfig(multipart_threshold=5 * GB, max_concurrency=4)


def processing_backup(item, config):
    """ for item in lst:"""
    pattern = re.search(r'\/([a-zA-Z0-9-]+\.zip)', item)
    if pattern is None:
        print("url does not match")
        return "not completed"
    article = re.sub(r'-[a-zA-Z0-9]+(:?\.zip)', '.zip', pattern.group(1))
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
        raise ValueError(folder)
    response = requests.get(item, stream=True)

    with open(article, "wb") as file:
        for chunk in tqdm(response.iter_content(chunk_size=5000000*20)):
            print("got chunk response")
            if chunk:
                file.write(chunk)

    print(article)
    s3.meta.client.upload_file(
        Bucket='mr-prod-wpengine-backup-20201022121325811200000001',
        Config=config,
        Key=folder + article,
        Filename=article
        )
    os.remove(article)
    print("complete")


for i in lst:
    processing_backup(i, transfer_config)

