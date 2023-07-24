from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional


class DBType(Enum):
    PSQL = 'PSQL'
    SQLITE = 'SQLITE'


@dataclass
class AirtableConfig:
    # how to get base_id, table_name
    # https://support.airtable.com/docs/finding-airtable-ids
    api_key: str = '<api-key>'
    database_id: str = '<db-id>'
    products_table_id: str = '<id-of-table-with-dataset-codes>'
    store_code_table_id: str = '<id-of-table-with-store-codes>'


@dataclass
class PostgresDbConfig:
    db_host: str = 'localhost'
    db_port: int = 5433
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_name: str = 'airtable_cache'


@dataclass
class SQLiteDbConfig:
    db_path: str = '/tmp/airtable/sqlite.db'


@dataclass
class LoggerConfig:
    filename: str = '/tmp/airtable/synchronizer.log'
    log_level: str = 'DEBUG'


@dataclass
class ThumbnailsConfig:
    size: Tuple[int, int] = (300, 300)
    format: str = 'png'
    temp_loading_dir_path: str = "/tmp/airtable/temp"
    resized_images_dir_path: str = "/tmp/airtable/pics-by-dataset-code"
    image_links_by_store_code: Optional[str] = "/tmp/airtable/pics-by-store-code"
    clean_on_startup: bool = True


@dataclass
class AppConfig:
    airtable_configuration: AirtableConfig = field(default=AirtableConfig())
    db_type: DBType = DBType.PSQL
    postgres_db_configuration: PostgresDbConfig = field(default=PostgresDbConfig())
    sqlite_db_configuration: SQLiteDbConfig = field(default=SQLiteDbConfig())
    thumbnails_configuration: ThumbnailsConfig = field(default=ThumbnailsConfig())
    logger_configuration: LoggerConfig = field(default=LoggerConfig())
