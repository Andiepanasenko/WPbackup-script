#!/bin/bash

###############################################################
# Script to dump and restore production and marketing databases
# from origin to other servers
###############################################################
MYSQL_DENISE_PRODUCT_USER=
MYSQL_DENISE_PRODUCT_PASS=
MYSQL_DENISE_PRODUCT_HOST=
MYSQL_DENISE_PRODUCT_CONN="-u${MYSQL_DENISE_PRODUCT_USER} -p${MYSQL_DENISE_PRODUCT_PASS} -h${MYSQL_DENISE_PRODUCT_HOST}"
MYSQL_PRODUCT_DB=pdffiller_denise

MYSQL_DENISE_MARKETING_USER=
MYSQL_DENISE_MARKETING_PASS=
MYSQL_DENISE_MARKETING_HOST=
MYSQL_DENISE_MARKETING_CONN="-u${MYSQL_DENISE_MARKETING_USER} -p${MYSQL_DENISE_MARKETING_PASS} -h${MYSQL_DENISE_MARKETING_HOST}"
MYSQL_MARKETING_DB=marketing_denise

MYSQL_USER=
MYSQL_PASS=
MYSQL_HOST=localhost
MYSQL_CONN="-u${MYSQL_USER} -p${MYSQL_PASS} -h${MYSQL_HOST}"

DUMP_LOCATION_DIR=/mnt/data/db_dumps
MYSQLDUMP_OPTIONS="--routines --triggers --single-transaction"

function help (){
  echo "Usage: ./${0} [all|product|marketing]"
  exit 0
}

function sync_product (){
  mv ${DUMP_LOCATION_DIR}/${MYSQL_PRODUCT_DB}.sql ${DUMP_LOCATION_DIR}/${MYSQL_PRODUCT_DB}.sql.backup
  echo "===== Starting product dump `date`"
  mysqldump ${MYSQL_DENISE_PRODUCT_CONN} ${MYSQLDUMP_OPTIONS} --databases ${MYSQL_PRODUCT_DB} > ${DUMP_LOCATION_DIR}/${MYSQL_PRODUCT_DB}.sql
  echo "===== Finished product dump `date`"

  echo "===== Starting product restore `date`"
  echo "DROP DATABASE ${MYSQL_PRODUCT_DB}" | mysql ${MYSQL_CONN}
  echo "CREATE DATABASE ${MYSQL_PRODUCT_DB}" | mysql ${MYSQL_CONN}
  echo "CREATE USER ${MYSQL_DENISE_PRODUCT_USER}@'%' IDENTIFIED BY '${MYSQL_DENISE_PRODUCT_PASS}'" | mysql ${MYSQL_CONN}
  echo "GRANT ALL PRIVILEGES ON ${MYSQL_PRODUCT_DB}.* TO ${MYSQL_DENISE_PRODUCT_USER}@'%';FLUSH PRIVILEGES;" | mysql ${MYSQL_CONN}
  mysql ${MYSQL_CONN} ${MYSQL_PRODUCT_DB} < ${DUMP_LOCATION_DIR}/${MYSQL_PRODUCT_DB}.sql
  echo "===== Finished product restore `date`"

}

function sync_marketing (){
  mv ${DUMP_LOCATION_DIR}/${MYSQL_MARKETING_DB}.sql ${DUMP_LOCATION_DIR}/${MYSQL_MARKETING_DB}.sql.backup
  echo "===== Starting marketing dump `date`"
  mysqldump ${MYSQL_DENISE_MARKETING_CONN} ${MYSQLDUMP_OPTIONS} --databases ${MYSQL_MARKETING_DB} > ${DUMP_LOCATION_DIR}/${MYSQL_MARKETING_DB}.sql
  echo "===== Finished marketing dump `date`"

  echo "===== Starting marketing restore `date`"
  echo "DROP DATABASE ${MYSQL_MARKETING_DB}" | mysql ${MYSQL_CONN}
  echo "CREATE DATABASE ${MYSQL_MARKETING_DB}" | mysql ${MYSQL_CONN}
  echo "CREATE USER ${MYSQL_DENISE_MARKETING_USER}@'%' IDENTIFIED BY '${MYSQL_DENISE_MARKETING_PASS}'" | mysql ${MYSQL_CONN}
  echo "GRANT ALL PRIVILEGES ON ${MYSQL_MARKETING_DB}.* TO ${MYSQL_DENISE_MARKETING_USER}@'%';FLUSH PRIVILEGES;" | mysql ${MYSQL_CONN}
  mysql ${MYSQL_CONN} ${MYSQL_MARKETING_DB} < ${DUMP_LOCATION_DIR}/${MYSQL_MARKETING_DB}.sql
  echo "===== Finished marketing restore `date`"
}

if [ $# -ne 1 ]
then
  help
fi

db_type=$1

case $db_type in
  "product") sync_product ;;
  "marketing") sync_marketing ;;
  "all")
    sync_product
    sync_marketing
  ;;
  *) help ;;
esac