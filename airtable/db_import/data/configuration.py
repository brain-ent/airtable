from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class AirtableConfig:
    class Meta:
        ordered = True
    # how to get base_id, table_name
    # https://support.airtable.com/docs/finding-airtable-ids
    api_key: str = '<api-key>'
    database_id: str = '<db-id>'
    products_table_id: str = '<id-of-table-with-dataset-codes>'
    store_code_table_id: str = '<id-of-table-with-store-codes>'


@dataclass
class PostgresDbConfig:
    class Meta:
        ordered = True
    db_host: str = 'localhost'
    db_port: int = 5433
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_name: str = 'airtable_cache'


@dataclass
class LoggerConfig:
    class Meta:
        ordered = True
    filename: str = '/tmp/airtable/synchronizer.log'
    log_level: str = 'INFO'


@dataclass
class ThumbnailsConfig:
    class Meta:
        ordered = True
    size: Tuple[int, int] = (300, 300)
    format: str = 'png'
    temp_loading_dir_path: str = "/tmp/airtable/temp"
    resized_images_dir_path: str = "/tmp/airtable/pics"
    clean_on_startup: bool = True


@dataclass
class AppConfig:
    class Meta:
        ordered = True
    airtable_configuration: AirtableConfig = field(default=AirtableConfig())
    postgres_db_configuration: PostgresDbConfig = field(default=PostgresDbConfig())
    thumbnails_configuration: ThumbnailsConfig = field(default=ThumbnailsConfig())
    logger_configuration: LoggerConfig = field(default=LoggerConfig())
