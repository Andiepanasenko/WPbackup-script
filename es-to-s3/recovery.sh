#!/bin/bash
# Examlpe usage:
# ./es_to_s3.sh host:port snapshot_name index_name -1day -30day "%Y.%m.%d"
# `-1day` - `date` format command, backup ES index for this day
# `-30day` - `date` format command, remove ES index for this day
# `%Y.%m.%d` - date format.

# added by daimon 04.09.2017
# replace called programm to full path to programm
CURL="/usr/bin/curl"
GREP="/bin/grep"
SLEEP="/bin/sleep"
DATE="/bin/date"
TR="/usr/bin/tr"
SED="/bin/sed"
HEAD="/usr/bin/head"


function wait_success {
    ##### Params #####
    HOST_PORT=$1
    SNAPSHOT_NAME=$2
    INDEX=$3
    ### Params end ###

    until [[ $(${CURL} -s -XGET ${HOST_PORT}/_cat/recovery | grep ${INDEX}) == ""]]; do
        ${SLEEP} 10
    done
}

function restore_index {
    ##### Params #####
    HOST_PORT=$1
    SNAPSHOT_NAME=$2
    INDEX=$3
    RESTORE_DATE=$4
    DATE_FORMAT=$5
    ### Params end ###

    DAY_WHICH_RESTORE=$(${DATE} --date="${RESTORE_DATE}" +${DATE_FORMAT})
    INDEX_RESTORE=${INDEX}${DAY_WHICH_RESTORE}

    # Start create snapshot for index
    RESPONSE=$(${CURL} -XPOST ${HOST_PORT}/_snapshot/${SNAPSHOT_NAME}/${INDEX_RESTORE}/_restore -H 'Content-Type: application/json' -d "{\"indices\": \"${INDEX_RESTORE}\",\"index_settings\": {\"index.number_of_replicas\": 0}, \"ignore_index_settings\": [\"index.refresh_interval\"]}")


    echo "Restore: ${INDEX_RESTORE}   ${RESPONSE}" | ${TR} " " " "

    wait_success ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX_RESTORE}
}

HOST_PORT=$1 # elk-snapshots-5-2-elastic.pdf.int
SNAPSHOT_NAME=$2 # s3_elastic_log
INDEX=${3-"filebeat-"}
RESTORE_DATE=${4-"-1day"}
DATE_FORMAT=${6-"%Y.%m.%d"}

days=90
while [ $days -gt 0 ]
do  

    DATA="-"$days"day"
    echo remove $DATA

    $(restore_index ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX} $DATA ${DATE_FORMAT})

    VERSION=(6.1.1 6.1.2 6.2.2)

    for version in "${VERSION[@]}"; do
        echo remove $DATA
        $(restore_index ${HOST_PORT} ${SNAPSHOT_NAME} "filebeat-${version}-" $DATA ${DATE_FORMAT})
    done

    JS_ENV=(desk desk1 desk2 desk3 desk4 desk5 desk6 desk7 mob mob1 app app1 true_editor trueedit2)

    for js_env in "${JS_ENV[@]}"; do
        echo remove $DATA
        $(restore_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_history_" $DATA ${DATE_FORMAT})
        $(restore_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_client_" $DATA ${DATE_FORMAT})
    done

    days=$(( $days - 1 ))

done

