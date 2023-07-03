import logging
import sys
from logging.handlers import TimedRotatingFileHandler

import fire

from airtable.db_import.data.configuration import AppConfig
from airtable.db_import.data.db_models import StoreProductCode, Product, Thumbnail
from airtable.db_import.data.import_record_model import ImportRecordModel
from airtable.db_import.service.airtable_sync_service import AirtableSyncService
from airtable.db_import.service.config_service import ConfigManager
from airtable.db_import.service.psql_service import PostgresDBService
from airtable.db_import.service.thumbnails_loader import ThumbnailsLoader

_logger = logging.getLogger("Synchronizer")


def upload_to_cache(app_config: AppConfig):
    airtable_sync_service = AirtableSyncService(app_config)
    postgres_db_service = PostgresDBService(app_config=app_config)
    thumbnails_loader = ThumbnailsLoader(app_config)

    store_codes_dict = airtable_sync_service.get_all_store_codes()
    products: list[ImportRecordModel] = airtable_sync_service.get_all_products(store_codes_dict)

    postgres_db_service.create_tables()

    _logger.info("Saving Sigale product codes")
    for store_code in store_codes_dict.values():
        StoreProductCode.save_from_airtable(store_code)

    _logger.info("Saving dataset products")
    for product in products:
        Product.save_from_airtable(product)

    thumbnails_loader.multithread_load()
    count_of_records = postgres_db_service.count_of_records()
    _logger.info(f"data uploaded: {count_of_records}")


def images_loading_test(app_config):
    postgres_db_service = PostgresDBService(app_config=app_config)
    postgres_db_service.cache_database.bind([StoreProductCode, Product, Thumbnail])
    ThumbnailsLoader(app_config).multithread_load()


def app_startup(config_path: str):
    config_manager = ConfigManager(config_path)
    app_config = config_manager.load()
    if app_config is None:
        logging.critical(f"Could not read configuration file: {config_path}")
        return
    logging.basicConfig(encoding='utf-8',
                        level=app_config.logger_configuration.log_level,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.StreamHandler(sys.stdout),
                            TimedRotatingFileHandler(filename=app_config.logger_configuration.filename,
                                                     when='D',
                                                     interval=1,
                                                     backupCount=10
                                                     )])
    logging.getLogger('PIL').setLevel(logging.ERROR)
    upload_to_cache(app_config=app_config)
    # images_loading_test(app_config=app_config)


if __name__ == '__main__':
    fire.Fire(app_startup)
