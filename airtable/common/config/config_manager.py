import json
import logging
import os
from typing import Optional

import marshmallow_dataclass

from airtable.common.config.configuration import AppConfig


class ConfigManager:
    def __init__(
            self,
            path: str
    ):
        self._path = path
        self._schema = \
            marshmallow_dataclass.class_schema(AppConfig)()

    def load(self) -> Optional[AppConfig]:
        if not os.path.exists(self._path):
            self.save_default()
            return None
        with open(self._path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return self._schema.load(data)

    def save_default(self):
        config = AppConfig()
        data = self._schema.dump(config)
        with open(self._path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        logging.info(
            f'A config example was saved to {self._path}. '
            f'Please make necessary changes'
        )

    def save(self, config: AppConfig):
        data = self._schema.dump(config)
        with open(self._path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, sort_keys=True)

    @property
    def path(self) -> str:
        return self._path
