import logging
from typing import Dict

from peewee import PostgresqlDatabase

from airtable.db_import.data.configuration import AppConfig, PostgresDbConfig
from airtable.db_import.data.db_models import StoreProductCode, Product, Thumbnail


class PostgresDBService:
    config: PostgresDbConfig
    _logger = logging.getLogger("PostgresDBService")

    def __init__(self, app_config: AppConfig):
        self._logger.info("Connecting to cache database")
        self.config = app_config.postgres_db_configuration
        self.cache_database = PostgresqlDatabase(
            database=self.config.db_name,
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_user,
            password=self.config.db_password
        )
        self._logger.info("Connected to cache database")

    def _truncate_tables(self):
        StoreProductCode.truncate_table()
        Product.truncate_table()
        Thumbnail.truncate_table()

    def create_tables(self):
        self._logger.info("Updating cache database tables")
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
