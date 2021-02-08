
Function to share snapshots and call lambda function from another AWS account (trough API GW), 
to start copy shared backup on that account.

Incoming data (from function chose-snapshots-to-copy.py) should be in JSON format:
{"snapshot_to_share": snapshot-to-share-name, "snapshot_arn": snapshot-to-share-arn}

For correct working should be defined environment variables:
* BKP_ACCOUNT - AWS account ID were snapshots should be stored in
* API_KEY - Secret key. Should be added to request to remote lambda API GW header. 
* API_URL -  Url of API GW, using to proxy request to remote lambda function. 
* TEST_API - if "true" - ping remote function. Dry run.

Needed additional python packages in reqs.pip file.
Cannot be deployed by "inline edit on AWS console".
Zipped deploy package is mandatory.