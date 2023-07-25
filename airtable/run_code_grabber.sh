#!/bin/bash

# Set all output to English
export LC_ALL=C

# Find the root directory of the project
UTILS="./common/bash/utils.sh"; SP=$(realpath "$0"); SD=$(dirname "$SP"); cd "$SD" || (echo "Not a directory $SD"; exit 1);
while [ ! -f "$UTILS" ]; do cd ..; [ "$PWD" = "/" ] && (echo "Cannot find the root dir of the project"; exit 1) ; done
source "$UTILS"

usage () {
  cat << EOF
 run_code_grabber.sh  ${UL}source file${FR}  ${UL}destination file${FR}
 This utility uses classes with alphabetic codes from a dataset or a model and grabs all store codes from the AirTable.

 ${UL}source file${FR} - path to 'class_mapping.json' (from a model), 'classes.json' (from a dataset), or a simple one column list with classes
 ${UL}destination file${FR} - path to a new file, where to save store codes

 Make sure to edit the config file ${UL}airtable/config/synchronizer_config.json${FR}. If there is no such file, then default will be created.
EOF
}

# Check and use command line arguments
arg_num "$#" 2
source_file=$(arg_is_file "$1")
destination_file="$2"

export PYTHONPATH=.
python3 airtable/code_grabber/store_codes_grabber.py  \
  --config-path "./airtable/config/synchronizer_config.json"  \
  --file-with-classes "$source_file"  \
  --save-to "$destination_file"
