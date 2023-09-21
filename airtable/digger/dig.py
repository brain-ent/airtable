import fire
from pyairtable import Api

from airtable.common.config.config_manager import ConfigManager


def dig(
        config_path: str
):
    config_manager = ConfigManager(config_path)
    app_config = config_manager.load()
    api = Api(api_key=app_config.airtable_configuration.api_key)
    base = api.get_base(app_config)


if __name__ == '__main__':
    fire.Fire(dig)
