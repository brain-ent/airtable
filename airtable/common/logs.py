import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from airtable.common.config.configuration import AppConfig
from airtable.version import get_build_info


def setup_logs(
        app_config: AppConfig,
        utility_path: str
):
    log_dir = app_config.logger_configuration.log_dir
    utility_path = os.path.basename(utility_path)
    utility_path = os.path.splitext(utility_path)[0]
    log_file = os.path.join(log_dir, f'{utility_path}.log')
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=app_config.logger_configuration.log_level,
        format='%(asctime)s.%(msecs)d %(module)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            TimedRotatingFileHandler(
                filename=log_file,
                when='D',
                interval=1,
                backupCount=10
            )
        ]
    )
    logging.getLogger('PIL').setLevel(logging.DEBUG)


def log_build_info():
    build_info = get_build_info()
    logging.info("=" * len(build_info))
    logging.info(build_info)
    logging.info("=" * len(build_info))
