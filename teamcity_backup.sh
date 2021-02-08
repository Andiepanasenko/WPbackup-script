#!/usr/bin/env bash

#
# This script backup teamcity config to S3
# Dependencies:
# - aws cli
# - zabbix_sender
#
# Usage example:
#    bash teamcity_backup.sh TS_USER TS_PSWD S3_BUCKET_NAME/DIR
#

function wait_success {
    ##### Params #####
    URL=$1
    ### Params end ###

    while [ $(curl -s "${URL}/app/rest/server/backup") == "Running" ]; do
        sleep 1
    done
}

function zabbix_send {
    ##### Params #####
    ZBX_KEY=$1
    ZBX_DATA=$2
    ### Params end ###

    /usr/bin/zabbix_sender \
        -z "${ZBX_SERVER}" \
        -s "${ZBX_HOST}" \
        -k "${ZBX_KEY}" \
        -o "${ZBX_DATA}"
}

USER=$1
PSWD=$2
S3_PATH=$3

HOST=${4-"localhost"}
PORT=${5-"8111"}
BACKUP_DIR=${6-"/root/.BuildServer/backup"}
FILENAME=${7-"teamcity_backup"}

ZBX_SERVER=${8-"zabbix-proxy.pdf.int"}
ZBX_HOST=${9-"teamcity-server-new"}

URL="http://${USER}:${PSWD}@${HOST}:${PORT}"
LOGFILE="/var/log/${FILENAME}.log"

wait_success "${URL}"

# Run backup and get backup name
BACKUP_FILE=$(wget -qO- --post-data "" \
    "${URL}/httpAuth/app/rest/server/backup?`
    `includeConfigs=true&`
    `includeDatabase=true&`
    `includeBuildLogs=false&`
    `fileName=${FILENAME}")

wait_success "${URL}"

# Copy backup to S3
aws s3 cp --quiet \
    "${BACKUP_DIR}/${BACKUP_FILE}" "s3://${S3_PATH}/${BACKUP_FILE}"

BACKUP_EXIT_CODE=$?
BACKUP_SIZE=$(stat -c %s "${BACKUP_DIR}/${BACKUP_FILE}")

# Send to Zabbix
zabbix_send "teamcity.backup.exit_code" "${BACKUP_EXIT_CODE}"
zabbix_send "teamcity.backup.size" "${BACKUP_SIZE}"

# Send by Filebeat to ES and Grafana
echo "BACKUP_FILE: ${BACKUP_FILE}. `
     `BACKUP_EXIT_CODE: ${BACKUP_EXIT_CODE}. `
     `BACKUP_SIZE: ${BACKUP_SIZE}." \
    >> "${LOGFILE}"

# Remove local backup
rm -f "${BACKUP_DIR}/${BACKUP_FILE}"
