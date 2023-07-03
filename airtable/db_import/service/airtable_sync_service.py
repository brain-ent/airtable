import logging
import traceback
from io import BytesIO
from pathlib import Path

import requests
import wget as wget

from PIL import Image
from pyairtable import Table
from urllib3.util import Url

from airtable.db_import.data.configuration import AppConfig, AirtableConfig
from airtable.db_import.data.import_record_model import ImportRecordModel, AirtableThumbnail, StoreCode

_logger = logging.getLogger("AirtableSyncService")


class AirtableSyncService:
    config: AirtableConfig
    products_table: Table
    products_code_table: Table

    thumbnail_buffer: dict[str, AirtableThumbnail]

    def __init__(self, app_config: AppConfig):
        _logger.info("Connecting to Airtable")
        self.config = app_config.airtable_configuration
        # https://airtable.com/appqcEalZfvY4G1vy/tblcRn5JEXVSLWzFx/viwZ2DchVVKYRraPH?blocks=hide
        self.products_table = Table(
            api_key=self.config.api_key,
            base_id=self.config.database_id,
            table_name=self.config.products_table_id
        )
        # https://airtable.com/appqcEalZfvY4G1vy/tblAgS5fy0cWTeaVK/viwn5mjq1FlD2aLyr?blocks=hide
        self.products_code_table = Table(
            api_key=self.config.api_key,
            base_id=self.config.database_id,
            table_name=self.config.product_codes_table_id
        )
        self.thumbnail_buffer = dict()
        _logger.info("Connected to Airtable")

    def extract_thumbnail(self, thumbnail_dto_list: dict = None) -> AirtableThumbnail | None:
        if thumbnail_dto_list is None:
            return None
        thumbnail_dto = thumbnail_dto_list[0]
        if (
                'thumbnails' not in thumbnail_dto
                or 'filename' not in thumbnail_dto):
            return None
        thumbnail = AirtableThumbnail()
        thumbnail.record_id = thumbnail_dto['id']
        thumbnail.name = thumbnail_dto['filename']

        temp_thumbnail = thumbnail_dto['thumbnails']['large']
        thumbnail.shape = (temp_thumbnail['width'], temp_thumbnail['height'])
        thumbnail.url = temp_thumbnail['url']
        return thumbnail

    def extract_id_and_fields(self, airtable_dto: dict) -> (bool, str, dict):
        record_id = airtable_dto.get("id", None)
        record_fields = airtable_dto.get("fields", None)
        if record_id is None or record_fields is None:
            _logger.error("Exception during reading record")
            return False, None, None
        else:
            return True, record_id, record_fields

    def extract_record_data(self, record_dto: dict, store_codes_dict: dict) -> ImportRecordModel | None:
        record = ImportRecordModel()
        ret, record_id, record_fields = self.extract_id_and_fields(record_dto)
        if not ret:
            return None

        record.record_id = record_id
        record.name = record_fields.get("Name", None)
        record.amount_of_images = record_fields.get("Nombre de photos", 0)
        record.percentage_recognition = record_fields.get('% de reconnaissance', 0)
        record.dataset_code = record_fields.get('Dataset Vimana Code', None)
        record.amount_correct_high_confidence_recognition = record_fields.get('Nombre de passage J-1', 0)
        record.status = record_fields.get('Status', None)
        record.photoset = Url(record_fields.get('Photoset', None))
        record.amount_correct_recognition = record_fields.get('Nombre de passage', 0)
        record.percentage_high_confidence_recognition = record_fields.get('% de reconnaissance J-1', 0)
        record.status_photoset = record_fields.get('Status Photoset', None)
        record.thumbnail = self.extract_thumbnail(record_fields.get('Thumbnail', None))
        record.comments = record_fields.get("Comments", None)

        # thumbnail must be added to the downloading queue
        if record.thumbnail is not None:
            self.thumbnail_buffer[record.thumbnail.record_id] = record.thumbnail

        for store_codes_id in record_fields.get('Codes et produits Sigales', []):
            if store_codes_id in store_codes_dict:
                record.store_codes.append(store_codes_dict[store_codes_id])

        return record

    # 'Codes et produits Sigales'

    def extract_store_code_data(self, store_code_dto: dict) -> StoreCode | None:
        store_code = StoreCode()
        ret, record_id, record_fields = self.extract_id_and_fields(store_code_dto)
        if not ret:
            return None

        store_code.record_id = record_id
        store_code.name = record_fields.get("Name", None)
        if store_code.name is None:
            return None
        else:
            return store_code

    def get_all_store_codes(self) -> dict[str, StoreCode]:
        _logger.info("Load Sigale codes")

        store_codes_dto_list = self.products_code_table.all()
        store_codes_dict = dict()

        for store_code_dto in store_codes_dto_list:
            try:
                store_code = self.extract_store_code_data(store_code_dto)
                if store_code is not None:
                    store_codes_dict[store_code.record_id] = store_code
            except Exception as e:
                traceback.print_exc()

        return store_codes_dict

    def get_all_products(self, store_codes_dict: dict[str, StoreCode]) -> list[ImportRecordModel]:
        _logger.info("Load dataset products")
        records_dto_list = self.products_table.all()

        records: list[ImportRecordModel] = []

        for record_dto in records_dto_list:
            try:
                record = self.extract_record_data(record_dto, store_codes_dict)
                records.append(record)
            except Exception as e:
                traceback.print_stack()

        return records
