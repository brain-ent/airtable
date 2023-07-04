import logging
import os.path
import traceback
from multiprocessing.pool import Pool
from pathlib import Path
from typing import Union

import wget
from PIL import Image

from airtable.db_import.data.configuration import AppConfig, ThumbnailsConfig
from airtable.db_import.data.db_models import Thumbnail


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
            resized_image_path = Path(f"{self.config.resized_images_dir_path}/{thumbnail.Name}")
            resized_image_path = os.path.splitext(resized_image_path)[0] + '.' + self.config.format

            response = wget.download(thumbnail.Url, image_temp_path)
            self.resize_image(Path(response), resized_image_path)
        except Exception:
            traceback.print_exc()

    def multithread_load(self):
        self._logger.info("Loading Thumbnails")
        # _logger.debug(Thumbnail.select().dicts().execute())
        thumbnails = Thumbnail.select()
        with Pool() as p:
            p.map(self.load_one, thumbnails)
