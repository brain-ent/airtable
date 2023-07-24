#!/bin/bash
export PYTHONPATH=.
python3 ./airtable/db_import/synchronizer.py --config-path ./airtable/config/synchronizer_config.json
