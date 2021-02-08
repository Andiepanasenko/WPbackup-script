#!/bin/bash

TYPE="$1"

SOCKETS=($(netstat -ant | tail -n +3 | awk '{print $6}' | sort | uniq -c | sort -n))

for ((i=0;i< ${#SOCKETS[@]} ;i+=2)); do
    if [ "${SOCKETS[i+1]}" == ${TYPE} ]; then
        echo ${SOCKETS[i]}
        exit 0
    fi
done

echo 0
