
Function to copy shared by another AWS account snapshots. 
Function working trough API GW (to invite calls from another accounts), 

Incoming data should be is HTTP Request. JSON format:
Request body format should be
{snapshot-to-share-name: snapshot_arn}


Additional python packages isn't using.
Lambda could be deployed by "inline edit on AWS console".
Zipped deploy package isn't mandatory, but using to deploy from S3.