#!/bin/bash

function delete_from () {
    # Params start #
    TABLE=$1
    ITEM_ID=$2
    DAY=$3
    USER=$4
    PSWD=$5
    DBSERVER=$6
    DBNAME=$7
    ## Params end ##
    echo "DELETE FROM ${TABLE} WHERE itemid=$ITEM_ID AND clock<$DAY" \
        | mysql -u $USER -p$PSWD -h $DBSERVER $DBNAME 2>&1 \
        | grep -v "Using a password on the command line"
}


DBSERVER=$1
USER=$2
PSWD=$3
DBNAME=${4-"zabbix"}
SAVE_MONTH=${5-"3"}
IGNORE_HOST_ID=${6-"10142"} # for prod - stats host (hostid=10142)

# for each history length, get the oldest date we can have for that value

DAY=$(date --date="$SAVE_MONTH month ago" +%s)

# group items by their history
for history_interval in $(echo "SELECT history FROM items GROUP BY history ORDER BY history DESC;" | mysql -h $DBSERVER -u $USER -p$PSWD -N $DBNAME); do
    echo "SELECT itemid FROM items WHERE history='${history_interval}' AND NOT hostid=$IGNORE_HOST_ID;" | mysql -h $DBSERVER -u $USER -p$PSWD -N $DBNAME > itemids

    total=$(wc -l < itemids) # how many? (just for stats)

    item_num=1;
    current_percent=0;

    for item in $(cat itemids) ; do

        current_percent=$(((100*item_num)/total))

        echo "$(date) | [H${history_interval}] $item_num/$total [$current_percent%]"

        delete_from "history_uint" $item $DAY $USER $PSWD $DBSERVER $DBNAME
        delete_from "history_str"  $item $DAY $USER $PSWD $DBSERVER $DBNAME
        delete_from "history_log"  $item $DAY $USER $PSWD $DBSERVER $DBNAME
        delete_from "history_text" $item $DAY $USER $PSWD $DBSERVER $DBNAME
        delete_from "history"      $item $DAY $USER $PSWD $DBSERVER $DBNAME

        ((item_num++))
    done
done

exit 0
