import json
import logging
import os.path
import sys
from dataclasses import dataclass
from typing import Dict, Set, Iterable

import fire
import marshmallow_dataclass

from airtable.common.config.config_manager import ConfigManager
from airtable.common.data.import_record_model import ProducesDatasetModel
from airtable.common.logs import setup_logs, log_build_info
from airtable.common.service.airtable_sync_service import AirtableSyncService
from common.codes_and_ids.utils import split_ireco_code_and_subcode


@dataclass
class ClassMappingRecord:
    code: str
    name: str


@dataclass
class ClassMapping(dict):
    records: Dict[str, ClassMappingRecord]


def get_ia_codes_from_class_mapping_json(path: str) -> Set[str]:
    codes = set()
    schema = marshmallow_dataclass.class_schema(ClassMapping)()
    with open(path, 'r') as json_file:
        data = json_file.read()
        data = '{"records": ' + data + '}'
        class_mapping: ClassMapping = schema.loads(data)
    for r in class_mapping.records.values():
        codes.add(r.code)
    return codes


def get_ia_codes_from_classes_json(path: str) -> Set[str]:
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return set(data)


def get_ia_codes_from_txt_list(path: str) -> Set[str]:
    result = set()
    with open(path, 'r') as txt_file:
        for line in txt_file:
            line = line.strip()
            if line == '':
                continue
            result.add(line)
    return result


def get_ia_codes_from_file(path: str) -> Set[str]:
    logging.info(f'Reading IA codes from {path}')
    result_codes: Set[str] = set()
    source_file_name: str = os.path.basename(path)
    if source_file_name == 'class_mapping.json':
        possible_ia_codes = get_ia_codes_from_class_mapping_json(path)
    elif source_file_name == 'classes.json':
        possible_ia_codes = get_ia_codes_from_classes_json(path)
    else:
        possible_ia_codes = get_ia_codes_from_txt_list(path)
    for possible_code in possible_ia_codes:
        ireco_code, ireco_subcode = split_ireco_code_and_subcode(possible_code)
        logging.debug(f'{possible_code} => {ireco_code}')
        result_codes.add(ireco_code)
    return result_codes


def collect_all_store_codes(
        ia_codes: Iterable[str],
        store_product_by_ia_code: Dict[str, ProducesDatasetModel]
) -> Set[str]:
    all_store_codes = set()
    for iac in ia_codes:
        if iac not in store_product_by_ia_code:
            logging.warning(f'There is no {iac} in the AirTable')
            continue
        at_product = store_product_by_ia_code[iac]
        if len(at_product.store_codes) == 0:
            logging.warning(
                f'Product {iac} in the AirTable,'
                f'BUT there is no numeric store codes'
            )
            continue
        product_store_codes = []
        for sc in at_product.store_codes:
            store_code_id = sc.name
            if type(store_code_id) == int:
                store_code_id = str(store_code_id)
            elif type(store_code_id) != str:
                logging.error(
                    f'Unsupported code type: '
                    f'{type(store_code_id)} ({store_code_id})'
                )
                continue
            if store_code_id in all_store_codes:
                logging.error(
                    f'{store_code_id} of {iac} '
                    f'already used by another product!'
                )
                continue
            all_store_codes.add(store_code_id)
            product_store_codes.append(store_code_id)
        store_codes_str = ', '.join(product_store_codes)
        logging.info(f'Store codes for {iac}: {store_codes_str}')
    return all_store_codes


def grab_store_codes(
        config_path: str,
        file_with_classes: str,
        save_to: str
):
    config_manager = ConfigManager(config_path)
    app_config = config_manager.load()
    if app_config is None:
        logging.critical(f"Could not read configuration file: {config_path}")
        exit(1)
    # Update new default values
    config_manager.save(app_config)
    setup_logs(app_config=app_config, utility_path=sys.argv[0])
    log_build_info()
    #
    ia_codes = get_ia_codes_from_file(file_with_classes)
    ia_codes = sorted(ia_codes)
    logging.info(f'There {len(ia_codes)} IA codes')
    code_str = ', '.join(ia_codes)
    logging.debug(f'Codes: {code_str}')
    airtable_sync_service = AirtableSyncService(app_config)
    store_codes_by_id = airtable_sync_service.get_all_store_codes()
    products = airtable_sync_service.get_all_products(store_codes_by_id).values()
    products_by_ia_code: Dict[str, ProducesDatasetModel] = {p.dataset_code: p for p in products}
    print()
    logging.info(f'Inspecting {len(ia_codes)} IA codes...')
    all_store_codes = collect_all_store_codes(
        ia_codes=ia_codes,
        store_product_by_ia_code=products_by_ia_code
    )
    all_store_codes = sorted(all_store_codes)
    with open(save_to, 'w') as target_file:
        data = '\n'.join(all_store_codes)
        target_file.write(data)


if __name__ == '__main__':
    fire.Fire(grab_store_codes)
