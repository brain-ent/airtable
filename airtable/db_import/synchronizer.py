import logging
import os.path
import shutil
import sys
from typing import List

import fire

from airtable.common.config.configuration import AppConfig
from airtable.common.logs import setup_logs, log_build_info
from airtable.db_import.data.db_models import StoreProductCode, Product, Thumbnail, ProductsStats
from airtable.common.service.airtable_sync_service import AirtableSyncService
from airtable.common.config.config_manager import ConfigManager
from airtable.db_import.service.local_db_service import LocalDBService
from airtable.db_import.service.thumbnails_loader import ThumbnailsLoader


def upload_to_cache(app_config: AppConfig):
    airtable_sync_service = AirtableSyncService(app_config)
    local_db_service = LocalDBService(app_config=app_config)
    thumbnails_loader = ThumbnailsLoader(app_config)

    store_codes_by_record_id = airtable_sync_service.get_all_store_codes()
    products_by_record_id = airtable_sync_service.get_all_products(store_codes_by_record_id)
    products_stats_by_record_id = airtable_sync_service.get_all_products_stats(
        store_codes_by_record_id=store_codes_by_record_id,
        products_by_record_id=products_by_record_id
    )

    local_db_service.create_tables()

    logging.info("Saving Sigale product codes")
    for store_code in store_codes_by_record_id.values():
        StoreProductCode.save_from_airtable(store_code)

    logging.info("Saving dataset products")
    for product in products_by_record_id.values():
        Product.save_from_airtable(product)

    print('!!!!')
    for product_stat in products_stats_by_record_id.values():
        r = ProductsStats.save_from_airtable(product_stat)
        print('!!!!', r)

    thumbnails_loader.multithread_load()
    count_of_records = local_db_service.count_of_records()
    logging.info(f"data uploaded: {count_of_records}")


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
    setup_logs(app_config=app_config, utility_path=sys.argv[0])
    log_build_info()
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
