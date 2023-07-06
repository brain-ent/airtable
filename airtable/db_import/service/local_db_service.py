import logging
import os.path
from typing import Dict, Union

from peewee import PostgresqlDatabase, SqliteDatabase

from airtable.db_import.data.configuration import AppConfig, PostgresDbConfig, SQLiteDbConfig, DBType
from airtable.db_import.data.db_models import StoreProductCode, Product, Thumbnail

_logger = logging.getLogger("LocalDBService")


class LocalDBService:
    config: Union[PostgresDbConfig, SQLiteDbConfig]

    def __init__(self, app_config: AppConfig):
        _logger.info("Connecting to cache database")
        if app_config.db_type == DBType.PSQL:
            self.config = app_config.postgres_db_configuration
            self.cache_database = PostgresqlDatabase(
                database=self.config.db_name,
                host=self.config.db_host,
                port=self.config.db_port,
                user=self.config.db_user,
                password=self.config.db_password
            )
        elif app_config.db_type == DBType.SQLITE:
            self.config = app_config.sqlite_db_configuration
            dir_path = os.path.dirname(self.config.db_path)
            os.makedirs(dir_path, exist_ok=True)
            if os.path.isfile(self.config.db_path):
                os.unlink(self.config.db_path)
            self.cache_database = SqliteDatabase(
                database=self.config.db_path
            )
        else:
            _logger.critical(f'Unknown DB type!')
            quit(1)
        _logger.info("Connected to cache database")

    def _truncate_tables(self):
        StoreProductCode.truncate_table()
        Product.truncate_table()
        Thumbnail.truncate_table()

    def create_tables(self):
        _logger.info("Updating cache database tables")
        self.cache_database.bind([StoreProductCode, Product, Thumbnail])
        self.cache_database.drop_tables([StoreProductCode, Product, Thumbnail])
        self.cache_database.create_tables([Thumbnail, Product, StoreProductCode])

    def count_of_records(self) -> Dict[str, int]:
        result = dict(
            products=len(Product.select()),
            sigale_product_codes=len(StoreProductCode.select()),
            thumbnails=len(Thumbnail.select())
        )
        return result
