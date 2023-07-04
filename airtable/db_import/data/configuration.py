from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class AirtableConfig:
    class Meta:
        ordered = True
    # how to get base_id, table_name
    # https://support.airtable.com/docs/finding-airtable-ids
    api_key: str = 'patI6jvuOLJrT05fI.2583af75464fa4daa06d9b1d856bfc352f401b9fab0d2bdcc202c6bb9f1c0b60'
    database_id: str = 'appqcEalZfvY4G1vy'
    products_table_id: str = 'tblWx2fdWqAYMp3JQ'
    product_codes_table_id: str = 'tblAgS5fy0cWTeaVK'


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
    filename: str = 'airtable_synchronizer.log'
    log_level: str = 'INFO'


@dataclass
class ThumbnailsConfig:
    class Meta:
        ordered = True
    size: Tuple[int, int] = (300, 300)
    temp_loading_dir_path: str = "./temp"
    resized_images_dir_path: str = "./pics"


@dataclass
class AppConfig:
    class Meta:
        ordered = True
    airtable_configuration: AirtableConfig = field(default=AirtableConfig())
    postgres_db_configuration: PostgresDbConfig = field(default=PostgresDbConfig())
    thumbnails_configuration: ThumbnailsConfig = field(default=ThumbnailsConfig())
    logger_configuration: LoggerConfig = field(default=LoggerConfig())
