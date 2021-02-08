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

    until [ $(${CURL} -s -XGET ${HOST_PORT}/_snapshot/${SNAPSHOT_NAME}/${INDEX} | ${GREP} -o SUCCESS) ]; do
        ${SLEEP} 60
    done
}

function backup_index {
    ##### Params #####
    HOST_PORT=$1
    SNAPSHOT_NAME=$2
    INDEX=$3
    BACKUP_DATE=$4
    DATE_FORMAT=$5
    INDEX_SUFFIX=$6
    ### Params end ###

    DAY_WHICH_BACKUP=$(${DATE} --date="${BACKUP_DATE}" +${DATE_FORMAT})
    INDEX_BACKUP=${INDEX}${DAY_WHICH_BACKUP}${INDEX_SUFFIX}

    # Start create snapshot for index
    RESPONSE=$(${CURL} -XPUT ${HOST_PORT}/_snapshot/${SNAPSHOT_NAME}/${INDEX_BACKUP} -d "{\"indices\": \"${INDEX_BACKUP}\"}")

    echo "Backup: ${INDEX_BACKUP}   ${RESPONSE}" | ${TR} " " " "

    wait_success ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX_BACKUP}
}

function have_backup {
    ##### Params #####
    HOST_PORT=$1
    SNAPSHOT_NAME=$2
    INDEX=$3
    BACKUP_DATE=$4
    DATE_FORMAT=$5
    INDEX_SUFFIX=$6
    ### Params end ###

    if [ $(${CURL} -s -XGET ${HOST_PORT}/_snapshot/${SNAPSHOT_NAME}/${INDEX} | ${GREP} -o snapshot_missing_exception | ${HEAD} -1) == "snapshot_missing_exception" ]; then
        backup_index ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX} ${BACKUP_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX}
    fi
}

function remove_index {
    ##### Params #####
    HOST_PORT=$1
    SNAPSHOT_NAME=$2
    INDEX=$3
    BACKUP_DATE=$4
    DATE_FORMAT=$5
    INDEX_SUFFIX=$6
    ### Params end ###

    DAY_WHICH_REMOVE=$(${DATE} --date="${BACKUP_DATE}" +${DATE_FORMAT})
    INDEX_REMOVE=${INDEX}${DAY_WHICH_REMOVE}${INDEX_SUFFIX}

    have_backup ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX} ${BACKUP_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX}

    # Remove old index in elasticsearch
    ${CURL} -XDELETE ${HOST_PORT}/${INDEX_REMOVE}
    ${CURL} -XPOST ${HOST_PORT}/_cache/clear -d '{ "fielddata": "true" }'
}

function change_index_settings {
    ##### Params #####
    HOST_PORT=$1
    ### Params end ###

    ${CURL} -XPUT ${HOST_PORT}/_settings?pretty -H 'Content-Type: application/json' -d '
    {
        "index.auto_expand_replicas": "false",
        "index.number_of_replicas": 2
    }
    '| ${SED} '2q;d' | ${TR} " " "_"
}

HOST_PORT=$1
SNAPSHOT_NAME=$2
INDEX=${3-"filebeat-"}
INDEX_SUFFIX=""
BACKUP_DATE=${4-"-1day"}
REMOVE_DATE=${5-"-30day"}
DATE_FORMAT=${6-"%Y.%m.%d"}
JSFILLER_REMOVE_DATE="-7day"

$(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} ".kibana-" ${BACKUP_DATE} "%Y.%m.%d" ${INDEX_SUFFIX})
$(change_index_settings ${HOST_PORT})

$(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX} ${BACKUP_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})
$(remove_index ${HOST_PORT} ${SNAPSHOT_NAME} ${INDEX} ${REMOVE_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})

VERSION=(6.1.1 6.1.2 6.2.2)

for version in "${VERSION[@]}"; do

    $(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} "filebeat-${version}-" ${BACKUP_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})
    $(remove_index ${HOST_PORT} ${SNAPSHOT_NAME} "filebeat-${version}-" ${REMOVE_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})

done


JS_ENV=(desk desk1 desk2 desk3 desk4 desk5 desk6 desk7 mob mob1 app app1 true_editor trueedit2 trueedit3)

for js_env in "${JS_ENV[@]}"; do

    $(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_history_" ${BACKUP_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})
    $(remove_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_history_" ${JSFILLER_REMOVE_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})
    $(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_client_" ${BACKUP_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})
    $(remove_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_client_" ${JSFILLER_REMOVE_DATE} ${DATE_FORMAT} ${INDEX_SUFFIX})

    $(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_history_" ${BACKUP_DATE} ${DATE_FORMAT} ":7")
    $(remove_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_history_" ${JSFILLER_REMOVE_DATE} ${DATE_FORMAT} ":7")
    $(backup_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_client_" ${BACKUP_DATE} ${DATE_FORMAT} ":7")
    $(remove_index ${HOST_PORT} ${SNAPSHOT_NAME} "ahs_"$js_env"_client_" ${JSFILLER_REMOVE_DATE} ${DATE_FORMAT} ":7")

done
