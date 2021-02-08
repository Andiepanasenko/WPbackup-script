#!/usr/bin/env bash

# trace ERR through pipes
set -o pipefail

# trace ERR through 'time command' and other functions
set -o errtrace

# set -u : exit the script if you try to use an uninitialised variable
set -o nounset

# set -e : exit the script if any statement returns a non-true return value
set -o errexit

if [ -z "$GITHUB_USER" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "This Docker Image require a \$GITHUB_TOKEN and \$GITHUB_IMAGE variables. These variable are missing (or they is empty)."
    exit 1
fi

git clone --depth=1 -q https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/pdffiller/php-pcrypt-extension.git -b ${PCRYPT_VERSION} /tmp/pcrypt
cd /tmp/pcrypt

zephir build --backend-ZendEngine3

cp ./ext/modules/pcrypt.so "$(php-config --extension-dir)/pcrypt.so"
cp ./ext/modules/pcrypt.so /artifacts/pcrypt.so


