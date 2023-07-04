import logging

from peewee import Model, CharField, ForeignKeyField, IntegerField, PostgresqlDatabase

from airtable.db_import.data.configuration import AppConfig, PostgresDbConfig
from airtable.db_import.data.import_record_model import StoreCode, AirtableThumbnail, ImportRecordModel

# DB_NAME = 'airtable_cache'
# DB_HOST = 'localhost'
# DB_PORT = 5433
# DB_USER = 'postgres'
# DB_PASSWORD = 'postgres'
#
# cache_database = PostgresqlDatabase(DB_NAME, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD)

PRODUCT_TABLE_NAME = 'product'
STORE_PRODUCT_CODE_TABLE_NAME = 'store_product_code'
THUMBNAIL_TABLE_NAME = 'thumbnail'

_logger = logging.getLogger("Repository")


class Thumbnail(Model):
    RecordId = CharField(primary_key=True)
    Name = CharField()
    Url = CharField(max_length=1000)

    class Meta:
        db_table = THUMBNAIL_TABLE_NAME

    # @staticmethod
    # def save_from_airtable(airtable_thumbnail: AirtableThumbnail):
    #     if airtable_thumbnail is None:
    #         return
    #     saved_thumbnail = Thumbnail.create(
    #         record_id=airtable_thumbnail.record_id,
    #         name=airtable_thumbnail.name,
    #         url=airtable_thumbnail.url
    #     )
    #     return saved_thumbnail

    @staticmethod
    def save_from_airtable(airtable_thumbnail: AirtableThumbnail):
        if airtable_thumbnail is None:
            return
        _logger.debug(f"Saving thumbnail: {airtable_thumbnail}")
        thumbnail, created = Thumbnail.get_or_create(
            RecordId=airtable_thumbnail.record_id,
            defaults={'Name': airtable_thumbnail.name, 'Url': airtable_thumbnail.url})
        _logger.debug(f"Saved thumbnail: {thumbnail}")
        return thumbnail


class Product(Model):
    RecordId = CharField(primary_key=True)

    Name = CharField(null=True)
    DatasetCode = CharField(null=True)
    AmountOfImages = IntegerField(null=True)
    Thumbnail = ForeignKeyField(Thumbnail, null=True)

    class Meta:
        db_table = PRODUCT_TABLE_NAME

    @staticmethod
    def save_from_airtable(airtable_product: ImportRecordModel):

        _logger.debug(f"Saving product: {airtable_product}")
        saved_thumbnail = Thumbnail.save_from_airtable(airtable_product.thumbnail)

        if saved_thumbnail is not None:
            saved_product = Product.create(
                RecordId=airtable_product.record_id,
                Name=airtable_product.name,
                DatasetCode=airtable_product.dataset_code,
                AmountOfImages=airtable_product.amount_of_images,
                Thumbnail=airtable_product.thumbnail.record_id
            )
        else:
            saved_product = Product.create(
                RecordId=airtable_product.record_id,
                Name=airtable_product.name,
                DatasetCode=airtable_product.dataset_code,
                AmountOfImages=airtable_product.amount_of_images,
                Thumbnail=None
            )

        for airtable_product_store_code in airtable_product.store_codes:
            store_code_model: StoreProductCode = StoreProductCode.get_by_id(airtable_product_store_code.record_id)
            store_code_model.Product = saved_product.RecordId
            store_code_model.save()
            _logger.debug(f"Sigale code added: {store_code_model}")

        _logger.debug(f"Saved product: {saved_product}")

        return saved_product


class StoreProductCode(Model):
    RecordId = CharField(primary_key=True)

    Name = CharField()
    Product = ForeignKeyField(Product, null=True)

    class Meta:
        db_table = STORE_PRODUCT_CODE_TABLE_NAME

    @staticmethod
    def save_from_airtable(airtable_store_code: StoreCode, product_id: int = None):
        _logger.debug(f"Saving Sigale code: {airtable_store_code}")

        saved_store_code = StoreProductCode.create(
            RecordId=airtable_store_code.record_id,
            Name=airtable_store_code.name,
            Product=product_id)

        _logger.debug(f"Saved Sigale code: {saved_store_code}")
        return saved_store_code
