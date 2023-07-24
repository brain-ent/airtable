import logging
import os.path
import shutil
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import List

import fire

from airtable.common.config.configuration import AppConfig
from airtable.db_import.data.db_models import StoreProductCode, Product, Thumbnail
from airtable.common.data.import_record_model import ImportRecordModel
from airtable.common.service.airtable_sync_service import AirtableSyncService
from airtable.common.config.config_manager import ConfigManager
from airtable.db_import.service.local_db_service import LocalDBService
from airtable.db_import.service.thumbnails_loader import ThumbnailsLoader
from airtable.db_import.version import get_build_info

_logger = logging.getLogger("Synchronizer")


def upload_to_cache(app_config: AppConfig):
    airtable_sync_service = AirtableSyncService(app_config)
    local_db_service = LocalDBService(app_config=app_config)
    thumbnails_loader = ThumbnailsLoader(app_config)

    store_codes_dict = airtable_sync_service.get_all_store_codes()
    products: List[ImportRecordModel] = airtable_sync_service.get_all_products(store_codes_dict)

    local_db_service.create_tables()

    _logger.info("Saving Sigale product codes")
    for store_code in store_codes_dict.values():
        StoreProductCode.save_from_airtable(store_code)

    _logger.info("Saving dataset products")
    for product in products:
        Product.save_from_airtable(product)

    thumbnails_loader.multithread_load()
    count_of_records = local_db_service.count_of_records()
    _logger.info(f"data uploaded: {count_of_records}")


def images_loading_test(app_config):
    local_db_service = LocalDBService(app_config=app_config)
    local_db_service.cache_database.bind([StoreProductCode, Product, Thumbnail])
    ThumbnailsLoader(app_config).multithread_load()


def synchronizer(
        config_path: str,
        download_images_only: bool = False
):
    config_manager = ConfigManager(config_path)
    app_config = config_manager.load()
    if app_config is None:
        logging.critical(f"Could not read configuration file: {config_path}")
        exit(1)
    # Update new default values
    config_manager.save(app_config)
    log_dir = os.path.dirname(app_config.logger_configuration.filename)
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=app_config.logger_configuration.log_level,
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            TimedRotatingFileHandler(
                filename=app_config.logger_configuration.filename,
                when='D',
                interval=1,
                backupCount=10
            )
        ]
    )
    logging.getLogger('PIL').setLevel(logging.ERROR)
    build_info = get_build_info()
    _logger.info("=" * len(build_info))
    _logger.info(build_info)
    _logger.info("=" * len(build_info))
    if app_config.thumbnails_configuration.clean_on_startup:
        # Clean old images if any
        dirs_for_clean_up = [
            app_config.thumbnails_configuration.temp_loading_dir_path,
            app_config.thumbnails_configuration.resized_images_dir_path,
            app_config.thumbnails_configuration.image_links_by_store_code
        ]
        for dir in dirs_for_clean_up:
            if dir is None:
                continue
            if os.path.isdir(dir):
                shutil.rmtree(dir)
            os.makedirs(dir, exist_ok=True)
    if download_images_only:
        images_loading_test(app_config=app_config)
    else:
        upload_to_cache(app_config=app_config)


if __name__ == '__main__':
    fire.Fire(synchronizer)
