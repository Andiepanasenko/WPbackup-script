#!/bin/bash

# Script for move data between consul, s3 storage and local mashine
# Author: Dmitry Teikovcev, teikovtsev.dmitry@pdffiller.team
# Copyright: PDFfiller, inbox@pdffiller.com, www.pdffiller.com
#
# dependencies and settings:
#	- install consulate https://github.com/gmr/consulate
#	- install zabbix_sender as part of zabbix https://www.zabbix.com/
#	- install aws cli http://docs.aws.amazon.com/cli/latest/userguide/installing.html
#	- setup user s3 profile for access to s3 bucket and modify ${PROFILE} variable
#	- modify and check declare path variables like as PATH_TO_XXX in this file
#	- modyfy and chek declare in this file or in included config file (example backup_consul2s3.sh "/path/to/config.conf")
#
# addition need for shedule backup:
#	- create items with name like as ${MONKEY} variables for server like as ${MONHOST} in zabbix
#	- modify all variables in this file in blok 'user define parameters'
#	- modify root crontab like as:
#	22 8,14	* * *	/path/to/consul_backup2s3.sh /path/to/consul_backup2s3.conf
#	- optionally: create trigger like as
#	  '{server:keynames.nodata(86400)}=1 | {server:keynames.last()}<1'

LANG=c

PATH_TO_CONSULATE="/usr/local/bin/consulate"
PATH_TO_AWS="/usr/bin/aws"
PATH_TO_ZABBIXSENDER="/usr/bin/zabbix_sender"

PATH_TO_PYTHON="/usr/bin/python"
PATH_TO_BASENAME="/usr/bin/basename"
PATH_TO_STAT="/usr/bin/stat"
PATH_TO_ECHO="/bin/echo"
PATH_TO_SED="/bin/sed"
PATH_TO_DATE="/bin/date"
PATH_TO_GREP="/bin/grep"
PATH_TO_CAT="/bin/cat"
PATH_TO_RM="/bin/rm"

# ---------------------- start blok user define parameters

# The consul host to connect on.
APIHOST="localhost"

# The consul API port to connect to. Default is "8500".
APIPORT="8500"

# set to "yes" if need report to zabbix
REPORTTOZABBIX="no"

# Hostname or IP address of Zabbix server.
ZABBIXSERVER="localhost"

# Specify port number of server trapper running on the server. Default is "10051"
ZABBIXPORT="10051"

# Specify monitoring host name. Host IP address and DNS name will not wor.
MONHOST=""

# Specify monitoring item key.
MONKEY=""

# If "yes" send monitoring value as size file, else 0:error and 1:success. Default no
SIZEVALUE="no"

# aws s3 bucket.
BUCKET=""

# Specify folder in s3 bucket.
FOLDER=""

# Specify profile for connect to s3
PROFILE="default"

# Specify backup in human readable format.
ISHUMAN="no"

# local folder for work with files. Default is "/tmp/"
LOCALFOLDER="/tmp/"

# Specify file for log
#LOGFILE="/var/log/$(${BASENAME} $0).log"
LOGFILE="/dev/stdout"

# Specify debug level 0:error only, 1:fulldebug default "0"
DEBUGLEVEL="1"
# -------------------- end blok user define parameters

DEBUGFILE="/dev/null"
declare FILESIZE=0

# function write message to log file
function tolog()
{
    message=$*
    ${PATH_TO_ECHO} $(${PATH_TO_DATE} "+%Y.%m.%d %H:%M:%S ")${message} >> ${LOGFILE}
}

# function write message to log if debuglevel greate then zero
function todebug()
{
    message=$*
    if [ "${DEBUGLEVEL}" -gt 0 ] ; then
	${PATH_TO_ECHO} $(${PATH_TO_DATE} "+%Y.%m.%d %H:%M:%S ")${message} >> ${LOGFILE}
    fi
}

# function report to zabbix
# param:
#	$1 value for monitoring  0: error, >0 sucsess
function reporttozabbix()
{
    STATUS=$1

    for server in ${ZABBIXSERVER}
    do

	${PATH_TO_ZABBIXSENDER} -z ${server} -p ${ZABBIXPORT} -s ${MONHOST} -k ${MONKEY} -o ${STATUS} >> ${DEBUGFILE} 2>&1
	retstatus=$?
	if [ ${retstatus} -eq 0 ] ; then
	    todebug "success report to zabbix ${MONHOST}:${MONKEY}=${STATUS} server:${server}"
	    break
	else
	    tolog "error report to zabbix ${MONHOST}:${MONKEY}=${STATUS} server:${server}"
	fi

    done
}

# function get data from consul server and report to zabbix if need report about error
# stop script if error
# param:
#	$1 file name for save data from consul
#	$2 set to "yes" if need report to zabbix if error
function getfromconsul()
{
    backupfilename=$1
    report2zabbix=$2

    ${PATH_TO_CONSULATE} --api-host ${APIHOST} --api-port ${APIPORT} kv backup --file "${backupfilename}" >> ${DEBUGFILE} 2>&1
    retstatus=$?
    if [ ${retstatus} -eq 0 ] ; then
	todebug "success consulate backup to ${backupfilename}"
    else
	tolog "ERROR: consulate backup to ${backupfilename}, exit..."
	if [ "${report2zabbix}" = "yes" ] ; then
	    reporttozabbix 0
	fi
	exit
    fi
}

# function check if file exsissts and report to zabbix if need report about not found file
# break script if not found file
# param:
#	$1 file name for check exsissts file
#	$2 set to "yes" if need report to zabbix if file not found
function checkfile()
{
    checkfilename=$1
    report2zabbix=$2

    if [ -a "${checkfilename}" ] ; then
	todebug "success backup exists ${checkfilename}"
    else
	tolog "error backup not exists ${checkfilename}, exit"
	if [ "${report2zabbix}" = "yes" ] ; then
	    reporttozabbix 0
	fi
	exit
    fi
}

# function get size of file and report if need report about zero filesize
# break script if filezise is zero
# param:
#	$1 file name for get filesize
#	$2 set to "yes" if need report to zabbix if filesize is zero
function getfilesize()
{
    checkfilename=$1
    report2zabbix=$2

    FILESIZE=$(${PATH_TO_STAT} -c%s "${checkfilename}")
    if [ ${FILESIZE} -gt 0 ] ; then
	todebug "file ${checkfilename} have size=${FILESIZE}b"
    else
	tolog "ERROR: backup size for file ${checkfilename} is zero, exit"
	if [ "${report2zabbix}" = "yes" ] ; then
	    reporttozabbix 0
	fi
	exit
    fi
    #${PATH_TO_ECHO} "${FILESIZE}"
}

# function convert consulate backup to human readable format and validate json
# if need report to zabbix about fail
# break script if not passed json validate
# param:
#	$1 source file name
#	$2 destination file name
#	$3 set to "yes" if need report to zabbix if filesize is zero
function tohumanreadable()
{
    fromfile=$1
    tofile=$2
    report2zabbix=$3

    ${PATH_TO_CAT} "${fromfile}" | ${PATH_TO_PYTHON} -m json.tool > "${tofile}" 2>>${DEBUGFILE}
    retstatus=$?
    if [ ${retstatus} -eq 0 ] ; then
	todebug "success jsonvalidate in ${fromfile}"
    else
	tolog "ERROR: jsonvalidate backup in ${fromfile}"
	if [ "${report2zabbix}" = "yes" ] ; then
	    reporttozabbix 0
	fi
	exit
    fi
}

# function saved file to s3 backet. if need report to zabbix if fail
# break script if fail
# param:
#	$1 local file name
#	$2 destination file name
#	$3 set to "yes" if need report to zabbix if filesize is zero
function copytos3()
{
    localname=$1
    remotename=$2
    report2zabbix=$3

    foldername=$(${PATH_TO_DATE} "+${FOLDER}")

    ${PATH_TO_AWS} s3 cp "${localname}" s3://${BUCKET}/${foldername}/${remotename} --profile ${PROFILE} >> ${DEBUGFILE} 2>&1
    retstatus=$?
    if [ ${retstatus} -eq 0 ] ; then
	todebug "success copy to s3://${BUCKET}/${foldername}/${filename}"
    else
	tolog "error copy to s3://${BUCKET}/${foldername}/${filename}"
	if [ "${report2zabbix}" = "yes" ] ; then
	    reporttozabbix 0
	fi
	exit
    fi
}

# include config from file
if [ -n "$1" ] ; then
    if [ -s "$1" ] ; then
	. $1
	todebug "success included file $1"
    else
	tolog "ERROR: include file $1 not found"
    fi
fi

# filename for save backup to s3
filename="${APIHOST}-$(${PATH_TO_DATE} "+%Y%m%d%H").bak"

# variable for size of backup file
#declare -i backupsize=0

# get data from consul to local file and report to zabbix if error
getfromconsul "/${LOCALFOLDER}/${filename}" "${REPORTTOZABBIX}"

# check if file exsissts and report to zabbix if not found file
checkfile "/${LOCALFOLDER}/${filename}" "${REPORTTOZABBIX}"

# get size of file and report if zero filesize
#backupsize=$(getfilesize "/${LOCALFOLDER}/${filename}" "${REPORTTOZABBIX}")
getfilesize "/${LOCALFOLDER}/${filename}" "${REPORTTOZABBIX}"

# convert consulate backup to human readable format and validate json report to zabbix if fail
tohumanreadable "/${LOCALFOLDER}/${filename}" "/${LOCALFOLDER}/${filename}.txt" "${REPORTTOZABBIX}"

# copy file to s3 bucket
# choice .txt file if need save in human readable format
# report to zabbix if copy fail
if [ ${ISHUMAN} = "yes" ] ; then
    copytos3 "/${LOCALFOLDER}/${filename}.txt" "${filename}" "${REPORTTOZABBIX}"
else
    copytos3 "/${LOCALFOLDER}/${filename}" "${filename}" "${REPORTTOZABBIX}"
fi

# remove temporary files
${PATH_TO_RM} "/tmp/${filename}"
${PATH_TO_RM} "/tmp/${filename}.txt"

# if need report to zabbix
if [ "${REPORTTOZABBIX}" = "yes" ] ; then
    # if monitoring variant as size of file send size of backup file else send 1
    if [ "${SIZEVALUE}" = "yes" ] ; then
	reporttozabbix ${FILESIZE}
    else
	reporttozabbix 1
    fi
fi

# end of file
