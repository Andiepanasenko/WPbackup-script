#!/bin/bash

#### Test if PDF contains AcroForm and whether fileds are writable

if [[ $# -ne 1 ]]
then
  echo "Usage ./$0 PDF_FILE"
  exit 1
fi

PDF_INFO=`pdfinfo $1 | grep -E "(^Form:|^Encrypted)"`
ACROFORM=`echo -n "$PDF_INFO" | grep Form | awk {'print $2'}` 
ENCRYPTED=`echo -n "$PDF_INFO" | grep Encrypt | awk {'print $2'}` 
EDITABLE=`echo -n "$PDF_INFO" | grep Encrypt | awk {'print $5'} | cut -f2 -d:` 

#echo "$ACROFORM $ENCRYPTED $EDITABLE"

if [[ "${ACROFORM}" == "AcroForm" && "${ENCRYPTED}" == "yes" && "${EDITABLE}" == "no" ]]
then
  echo "yes"
else
  echo "no" 
fi

