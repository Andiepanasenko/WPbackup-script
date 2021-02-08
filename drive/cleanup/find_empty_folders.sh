#!/bin/bash

if [[ $# -ne 1 ]];then 
   echo "Usage: ./$0 directory_path"
   exit 0;
fi

SOURCE_DIR=$1
OP=$2
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
  for dir in $(find ${1} -maxdepth 1 -mindepth 1 -type d)
  do
    count=$(ls $dir | wc -l)
    if [[ $count -gt 0 ]];then
        find_empty_folder "${dir}"
    else
      if [ $(is_older_than $dir) -eq 1 ] ;then
        echo "$dir" >> ${EMPTY_DIRS_LOG} 
      fi
    fi
  done
}

find_empty_folder $1 
