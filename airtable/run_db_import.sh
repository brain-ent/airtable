#!/bin/bash

# Set all output to English
export LC_ALL=C

# Find the root directory of the project
UTILS="./common/bash/utils.sh"; SP=$(realpath "$0"); SD=$(dirname "$SP"); cd "$SD" || (echo "Not a directory $SD"; exit 1);
while [ ! -f "$UTILS" ]; do cd ..; [ "$PWD" = "/" ] && (echo "Cannot find the root dir of the project"; exit 1) ; done
source "$UTILS"

export PYTHONPATH=.
python3 ./airtable/db_import/synchronizer.py --config-path ./airtable/config/synchronizer_config.json
