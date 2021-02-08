#!/bin/bash

if [ $# -lt 1 ] ; then
    echo "usage $0 <path_to_file_with_forms_id>"
    exit
fi

FROM_FILE=$1
SOLR_ENDPOINT="http://52.6.28.227:8983"
SOLR_URL="${SOLR_ENDPOINT}/solr/forms/update?commit=true"
CURL="/usr/bin/curl"
LOGFILE=$(LANG=c date "+%y%b%d-%H%M%S-")$(basename $0)".log"

echo "save to ${LOGFILE}"
for form_id in $(cat ${FROM_FILE} |  sed -e "s/,//g; s/ //g; s/\r//g")
do

    echo "delete ${form_id}"

    echo >> ${LOGFILE}
    echo "delete ${form_id}:" >> ${LOGFILE}
    ${CURL} ${SOLR_URL} -d "<delete><query>id:${form_id}</query></delete>" -H "Content-Type: text/xml" >> ${LOGFILE} 2>&1

done
