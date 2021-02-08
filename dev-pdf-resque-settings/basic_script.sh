#!/bin/bash

su - developer -c "cd /mnt/www && git clone git@github.com:pdffiller/system-utils.git"
cp system-utils/dev-pdf-resque-settings/dev_and_resque.sh .
rm -rf system-utils/

chmod +x dev_and_resque.sh
./dev_and_resque.sh
rm basic_script.sh
