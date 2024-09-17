import fire
from pyairtable import Table

from airtable.common.config.config_manager import ConfigManager


def stats_test(
        config_path = '/home/lsh/dev/GFruitsVegetables/code/IREC-904-airtable/airtable/config/synchronizer_config.json'
):
    config_manager = ConfigManager(config_path)
    app_config = config_manager.load()
    products_stats = Table(
        api_key=app_config.airtable_configuration.api_key,
        base_id=app_config.airtable_configuration.database_id,
        table_name='tbl4PZ1wS2Kn7f2N8'
    )
    records = products_stats.all()
    for r in records:
        # print(r)
        if 'Code' not in r['fields']:
            continue
        if r['fields']['Code'] in (6337, 6313):
            print(r)


if __name__ == '__main__':
    fire.Fire(stats_test)
