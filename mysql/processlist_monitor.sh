#!/bin/bash

DBUSER=
DBPASS=
HOST=
INTERVAL=15
# Main loop
while true
do
  echo "==================== `date` ======================="
  mysqladmin -u$DBUSER -p$DBPASS -h$HOST processlist |
    egrep -vwi 'Sleep|processlist|Binlog Dump' |
    awk -F'|' '{print $2 $3 $4 $5 $6, $7, $8, $9}'
  sleep $INTERVAL
done
