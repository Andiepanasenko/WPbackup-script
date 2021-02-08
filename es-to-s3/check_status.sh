#!/bin/bash
# Examlpe usage:
# ./check_status.sh host:port snapshot_name index_name

HOST_PORT=$1
SNAPSHOT_NAME=$2

INDEX=${3-"filebeat-"}
DAY_WHICH_BACKUP=$(date --date="-1day" +\%Y.\%m.\%d)
INDEX_BACKUP=$INDEX$DAY_WHICH_BACKUP

STATUS_URL=$HOST_PORT/_snapshot/$SNAPSHOT_NAME/$INDEX_BACKUP/_status
curl -s $STATUS_URL | jq '{snapshots}[][].state'
