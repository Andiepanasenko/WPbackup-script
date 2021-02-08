#!/bin/bash

if [[ $# -ne 1 ]];then 
   echo "Usage: ./$0 removal_records_file"
   exit 0;
fi

SOURCE_FILE=$1
RETENTION=1  #will remove files older than 1 day 
EMPTY_DIRS_DATA=/home/ubuntu/empty_files
EMPTY_DIRS_LOG=${EMPTY_DIRS_DATA}/`echo ${SOURCE_DIR}_$(date +%s).log | tr '/' '_'`

function is_older_than(){
   filename=${1}
   file_time=$(stat --format='%Y' "$filename")
   current_time=$(date +%s)
   if (( file_time < ( current_time - ( 60 * 60 * 24 * ${RETENTION} )) ));then
      #echo "$filename is older than ${RETENTION} days"
      echo 1 
   else 
      echo 0 
   fi
}

function find_empty_folder(){
  cat $SOURCE_FILE | while read dir  
  do
    count=$(ls $dir | wc -l)
    if [[ $count -eq 0 ]];then
      if [ $(is_older_than $dir) -eq 1 ] ;then
        echo $dir  
        rmdir $dir
      fi
    fi
  done
}

find_empty_folder $1 
