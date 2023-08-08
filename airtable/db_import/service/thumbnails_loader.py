import logging
import os.path
import traceback
from multiprocessing.pool import Pool
from pathlib import Path
from typing import Union

import wget
from PIL import Image

from airtable.common.config.configuration import AppConfig, ThumbnailsConfig
from airtable.db_import.data.db_models import Thumbnail, StoreProductCode, Product


class ThumbnailsLoader:
    _logger = logging.getLogger("ThumbnailsLoader")
    config: ThumbnailsConfig
    app_config: AppConfig

    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.config = app_config.thumbnails_configuration

    def resize_image(self, src: Union[Path, str], dst: Union[Path, str]):
        image = Image.open(src)
        resized_image = image.resize(self.config.size, Image.ADAPTIVE)
        resized_image.save(fp=dst)
        os.unlink(src)
        self._logger.debug(f"{dst} saved")

    def _gen_resized_path(self, thumbnail: Thumbnail) -> Union[Path, str]:
        file_name_wo_ext = os.path.splitext(thumbnail.Name)[0]
        return Path(self.config.resized_images_dir_path) / f'{file_name_wo_ext}.{self.config.format}'

    def _create_links(self, thumbnail: Thumbnail):
        resized_image_path = self._gen_resized_path(thumbnail)
        product: Product = Product.select(Product.RecordId).where(Product.Thumbnail == thumbnail.RecordId)[0]
        product_id = product.RecordId
        store_codes = StoreProductCode.select().where(StoreProductCode.Product == product_id)
        for sc in store_codes:
            sc: StoreProductCode
            link_target = Path(self.config.image_links_by_store_code) / f'{sc.Code}.{self.config.format}'
            os.link(resized_image_path, link_target)

    def load(self):

        self._logger.info("Thumbnails loading...")
        # _logger.debug(Thumbnail.select().dicts().execute())
        for thumbnail in Thumbnail.select():
            self.load_one(thumbnail)

    def load_one(self, thumbnail: Thumbnail):
        if thumbnail is None:
            return
        try:
            if self.app_config.logger_configuration.log_level.lower() == "debug":
                print(f"loading thumbnail: {thumbnail.Name}")
            image_temp_path = f"{self.config.temp_loading_dir_path}/{thumbnail.Name}"
            resized_image_path = self._gen_resized_path(thumbnail)
            response = wget.download(thumbnail.Url, image_temp_path)
            self.resize_image(Path(response), resized_image_path)
            if self.config.image_links_by_store_code is not None:
                self._create_links(thumbnail)
        except Exception:
            traceback.print_exc()

    def multithread_load(self):
        self._logger.info("Loading Thumbnails")
        # _logger.debug(Thumbnail.select().dicts().execute())
        thumbnails = Thumbnail.select()
        with Pool() as p:
            p.map(self.load_one, thumbnails)
