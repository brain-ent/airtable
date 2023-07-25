#!/bin/bash

# This script updates a version info inside `airtable/db_import/version/ver.py`
# This script is used by `.github/workflows/makefile.yml`

# A path to a directory where current script is located
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# A path to `airtable/db_import/version/ver.py`
VER_FILE_PATH="$SCRIPT_DIR/ver.py"
# Current date and time
DATE=$(date '+%Y%m%d%H%M')

# The $build_num variable is set inside .github/workflows/makefile.yml
sed -i "s/number_undefined/$build_num/g" "$VER_FILE_PATH"
sed -i "s/date_undefined/$DATE/g" "$VER_FILE_PATH"

echo "=== Patched $VER_FILE_PATH ==="
cat $VER_FILE_PATH
echo "=== Patched $VER_FILE_PATH ==="

# The `tr` command is needed because Bash can not handle spaces in statements with variables
cat "$VER_FILE_PATH" | tr -d ' ' | grep "^VER_" > /tmp/ver.sh
cat "$VER_FILE_PATH" | tr -d ' ' | grep "^BUILD_" >> /tmp/ver.sh
source /tmp/ver.sh

# Example version: 1.0.0-30-2022-08-08-11-26-24
echo "::set-output name=ver::$VER_MAJOR.$VER_MINOR.$VER_PATCH.$BUILD_NUMBER-$BUILD_DATE"
