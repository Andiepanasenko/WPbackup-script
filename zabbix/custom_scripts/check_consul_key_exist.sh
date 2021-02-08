#!/bin/bash
# Check key if exist. If key not exist - instance up without keys or someone remove this key.

KEY=$(curl -s localhost:8500/v1/kv/us-east-1/local/zabbix-sender/host)

if [ "$KEY" = "" ]; then
    echo 0
else
    echo 1
fi
