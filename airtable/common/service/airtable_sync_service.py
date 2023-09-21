import logging
import os
import traceback
from typing import Dict, Optional, List

from pyairtable import Table
from urllib3.util import Url

from airtable.common.config.configuration import AppConfig, AirtableConfig
from airtable.common.data.import_record_model import ProducesDatasetModel, AirtableThumbnail, StoreCode, ProductsStatsModel


class AirtableSyncService:
    config: AirtableConfig
    products_table: Table
    store_code_table: Table

    thumbnail_buffer: Dict[str, AirtableThumbnail]

    def __init__(self, app_config: AppConfig):
        logging.info("Connecting to Airtable")
        self.config = app_config.airtable_configuration
        # https://airtable.com/appqcEalZfvY4G1vy/tblcRn5JEXVSLWzFx/viwZ2DchVVKYRraPH?blocks=hide
        self.products_table = Table(
            api_key=self.config.api_key,
            base_id=self.config.database_id,
            table_name=self.config.products_table_id
        )
        # https://airtable.com/appqcEalZfvY4G1vy/tblAgS5fy0cWTeaVK/viwn5mjq1FlD2aLyr?blocks=hide
        self.store_code_table = Table(
            api_key=self.config.api_key,
            base_id=self.config.database_id,
            table_name=self.config.store_code_table_id
        )
        self.products_stats_table = Table(
            api_key=self.config.api_key,
            base_id=self.config.database_id,
            table_name=self.config.products_stats_table_id
        )
        self.thumbnail_buffer = dict()
        logging.info("Connected to Airtable")

    def extract_thumbnail(self, thumbnail_dto_list: dict = None) -> Optional[AirtableThumbnail]:
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

        temp_thumbnail = thumbnail_dto['thumbnails']['full']
        thumbnail.shape = (temp_thumbnail['width'], temp_thumbnail['height'])
        thumbnail.url = temp_thumbnail['url']
        return thumbnail

    def extract_id_and_fields(self, airtable_dto: dict) -> (bool, str, dict):
        record_id = airtable_dto.get("id", None)
        record_fields = airtable_dto.get("fields", None)
        if record_id is None or record_fields is None:
            logging.error("Exception during reading record")
            return False, None, None
        else:
            return True, record_id, record_fields

    def extract_produces_data(self, record_dto: dict, store_codes_dict: dict) -> Optional[ProducesDatasetModel]:
        record = ProducesDatasetModel()
        ret, record_id, record_fields = self.extract_id_and_fields(record_dto)
        if not ret:
            return None

        record.record_id = record_id
        record.name = record_fields.get("Name", None)
        record.dataset_code = record_fields.get('Vimana produce Code', None)
        record.thumbnail = self.extract_thumbnail(record_fields.get('Thumbnail', None))
        record.comments = record_fields.get("Comments", None)
        record.amount_of_images = record_fields.get("Nbr of pictures", 0)
        record.amount_correct_high_confidence_recognition = record_fields.get('Nombre de passage J-1', 0)
        record.status = record_fields.get('Status', None)
        record.amount_correct_recognition = record_fields.get('Nombre de passage', 0)
        record.percentage_high_confidence_recognition = record_fields.get('% de reconnaissance J-1', 0)
        record.status_photoset = record_fields.get('Status Photoset', None)
        record.photoset = Url(record_fields.get('Photoset', None))
        record.percentage_recognition = record_fields.get('% Recognition', 0)

        if record.dataset_code is None:
            # Do not use this thumbnail if there is no `dataset_code`
            record.thumbnail = None
        else:
            # Use `dataset_code` as a part of file name for this thumbnail
            file_name_parts = os.path.splitext(record.thumbnail.name)
            file_name = record.dataset_code + file_name_parts[1]
            record.thumbnail.name = file_name
        # Thumbnail must be added to the downloading queue
        if record.thumbnail is not None:
            self.thumbnail_buffer[record.thumbnail.record_id] = record.thumbnail

        for store_codes_id in record_fields.get('Linked products', []):
            if store_codes_id in store_codes_dict:
                record.store_codes.append(store_codes_dict[store_codes_id])

        return record

    def extract_store_code_data(self, store_code_dto: dict) -> Optional[StoreCode]:
        store_code = StoreCode()
        ret, record_id, record_fields = self.extract_id_and_fields(store_code_dto)
        if not ret:
            return None

        store_code.record_id = record_id
        store_code.name = record_fields.get("Code", None)
        store_code.ud = record_fields.get("UD", None)
        if store_code.name is None:
            return None
        else:
            return store_code

    def get_all_store_codes(self) -> Dict[str, StoreCode]:
        """
        Get all alpha store codes (like 5300) from Products table.
        """
        logging.info("Loading codes from `Products` table...")
        store_codes_dto: List[Dict] = self.store_code_table.all()
        logging.debug(
            f'There is {len(store_codes_dto)} records in `products_code_table`'
        )
        debug_num = 3
        logging.debug(
            f'First {debug_num} records of `products_code_table`: '
            f'{store_codes_dto[:debug_num]}'
        )
        store_codes_by_record_id: Dict[str, StoreCode] = dict()
        for store_code_dto in store_codes_dto:
            try:
                store_code = self.extract_store_code_data(store_code_dto)
                if store_code is not None:
                    store_codes_by_record_id[store_code.record_id] = store_code
            except Exception as e:
                traceback.print_exc()
        logging.debug(f'There is {len(store_codes_by_record_id)} extracted store codes')
        return store_codes_by_record_id

    def get_all_products(self, store_codes_dict: Dict[str, StoreCode]) -> Dict[str, ProducesDatasetModel]:
        logging.info("Load dataset products")
        records_dto_list = self.products_table.all()
        debug_num = 3
        logging.debug(
            f'First records {debug_num} of `products_table`: '
            f'{records_dto_list[:debug_num]}'
        )
        products_by_record_id: Dict[str, ProducesDatasetModel] = {}
        for record_dto in records_dto_list:
            try:
                record = self.extract_produces_data(record_dto, store_codes_dict)
                products_by_record_id[record.record_id] = record
            except Exception as e:
                traceback.print_stack()
        return products_by_record_id

    def extract_products_stats_data(
            self,
            record_dto: Dict,
            store_codes_by_record_id: Dict[str, StoreCode],
            products_by_record_id: Dict[str, ProducesDatasetModel]
    ) -> Optional[ProductsStatsModel]:
        record = ProductsStatsModel()
        ret, record_id, record_fields = self.extract_id_and_fields(record_dto)
        if not ret:
            return None
        record.record_id = record_id
        if 'Code' not in record_fields:
            return None
        product_code_link = record_fields['Product code'][0]
        if product_code_link in store_codes_by_record_id.keys():
            record.product_code = store_codes_by_record_id[product_code_link].name
        else:
            record.product_code = ''
        if 'Nom' in record_fields:
            record.nom = record_fields['Nom'][0]
        else:
            record.nom = ''
        if 'Dataset' in record_fields:
            record.dataset = record_fields['Dataset'][0]
        else:
            record.dataset = ''
        if 'Thumbnail' in record_fields:
            record.thumbnail = record_fields['Thumbnail'][0]['id']
        else:
            record.thumbnail = ''
        if 'Statut photoset' in record_fields:
            record.statut_photoset = record_fields['Statut photoset'][0]
        else:
            record.statut_photoset = ''
            # dataset_link = record_fields['Dataset']
        # if dataset_link in products_by_record_id.keys():
        #     record.dataset
        return record

    def get_all_products_stats(
            self,
            store_codes_by_record_id: Dict[str, StoreCode],
            products_by_record_id: Dict[str, ProducesDatasetModel]
    ) -> Dict[str, ProductsStatsModel]:
        logging.info(f'Loading Products stats')
        products_stats_dto_list = self.products_stats_table.all()
        debug_num = 3
        logging.debug(
            f'First records {debug_num} of `Products stats`: '
            f'{products_stats_dto_list[:debug_num]}'
        )
        products_stats_by_record_id: Dict[str, ProductsStatsModel] = {}
        for record_dto in products_stats_dto_list:
            # try:
            record = self.extract_products_stats_data(
                record_dto=record_dto,
                store_codes_by_record_id=store_codes_by_record_id,
                products_by_record_id=products_by_record_id
            )
            if record is not None:
                products_stats_by_record_id[record.record_id] = record
            # except Exception as exc:
            #     print(exc)
            #     traceback.print_stack()
        return products_stats_by_record_id
