#!/bin/bash

function usage() {
  echo "Usage: ./$0 PDF_FILE [debug]"
}

function debug() {
  echo "$1"
}

if [ $# -lt 1 ]
then
  usage
  exit 0
fi

PDF_FILE=$1
[ $# -eq 2 ]&&[ $2 == "debug" ]&&DEBUG=true
 
VALIDATION=$(pdfinfo -f 1 -l 1000 $PDF_FILE | grep "Page.* size:" \
   | while read Page _pageno size _width x _height pts _format
     do
       VAL="${Page} ${_pageno}"
       [ $DEBUG ]&&debug "${Page} ${_pageno} ${size} ${_width} x ${_height} pts ${_format}"
       if [[ "$(echo "${_width} / 1"|bc)" -gt "$(echo "${_height} / 1"|bc)" ]]
       then
          VAL=$VAL":ORIENTATION_FAILED"
          echo $VAL
       fi

       if [[ -z $(echo "${_format}" | grep "letter") ]]
       then
          VAL=$VAL":FORMAT_FAILED"
          echo $VAL
       fi
     done) 

ROTATION=$(pdfinfo -f 1 -l 1000 $PDF_FILE | grep rot: | awk '$NF > 0 {print "FAILED"}' | uniq)

[[ $ROTATION == "FAILED" ]]&&VALIDATION=$VALIDATION"\n ROTATION:FAILED"
[[ -n $(echo $VALIDATION) ]]&&VALIDATION=${VALIDATION}"\n"

if [[ -n $(echo $VALIDATION | grep FAILED) ]]
then
  echo -e "${VALIDATION}FAILED"  
  exit 0
fi

echo -e "${VALIDATION}PASSED"
