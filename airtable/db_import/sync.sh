#!/bin/bash
export PYTHONPATH=.
python3 ./airtable/db_import/synchronizer.py --config_path ./airtable/db_import/synchronizer_config.json
