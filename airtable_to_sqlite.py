import os
import re
import json
import sqlite3
import unicodedata

from time import time
from datetime import datetime
from airtable import Airtable
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class ProducesDatasetModel:
    alpha_code: Optional[int]
    type: Optional[str]
    name: Optional[str]
    name_normalized: Optional[str]
    class_dataset_code: str


def load_config(config_file: str = 'config.json') -> dict:
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_french_word(word: str) -> str:
    if not word:
        return ''
    # TODO: make \w to ignore non alphabetic symbols
    word: str = unicodedata.normalize('NFD', word)
    word: str = ''.join(c for c in word if unicodedata.category(c) != 'Mn')
    word: str = word.replace("'", "").replace("-", " ")
    word: str = re.sub(r"[^a-zA-Z0-9]+", " ", word)
    return re.sub(r"\s+", " ", word).strip()


def map_airtable_product_record(products: List[dict], classes: List[dict], name_field: str) -> List[ProducesDatasetModel]:
    print(f"Map the products with classes (using field: {name_field})")
    result = []
    id_code_mapping: Dict[str, int] = {cls['id']: cls['fields'].get("Vimana produce Code") for cls in classes}
    for product in products:  # type: dict
        fields: dict = product['fields']
        alpha_code: int = fields.get('Code')
        sale_type: str = fields.get('UD')
        name: str = fields.get(name_field)
        name_normalized: str = normalize_french_word(name)
        class_dataset_code: List[str] = fields.get("Nom classe")
        # retreive the code
        if class_dataset_code:
            class_dataset_code: int = id_code_mapping.get(class_dataset_code[0])
        # form the class code manually if code not exists or empty
        if not class_dataset_code and name_normalized:
            class_dataset_code: str = name_normalized.upper().replace(' ', '.')
        # skip broken products
        if not (alpha_code and sale_type and name):
            continue
        #
        result.append(
            ProducesDatasetModel(
                alpha_code=alpha_code,
                type=sale_type,
                name=name,
                name_normalized=name_normalized,
                class_dataset_code=class_dataset_code,
            )
        )
    return result


def remove_existing_db(db_path: str):
    print("Delete the existing local DB before creating new one")
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Existing local DB ({db_path}) was removed")


def create_tables(conn: sqlite3.Connection):
    print("Create tables for new DB")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_code TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alpha_code INTEGER,
            type TEXT,
            name TEXT,
            name_normalized TEXT,
            class_id INTEGER,
            FOREIGN KEY(class_id) REFERENCES classes(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article (
            id INTEGER PRIMARY KEY,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itempos (
            intcode INTEGER PRIMARY KEY,
            description TEXT,
            alpha_code INTEGER,
            item_subtype INTEGER,
            item_type INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            alpha_code INTEGER PRIMARY KEY,
            available  INTEGER,
            corrected  INTEGER
        )
    """)
    conn.commit()


def insert_metadata(conn: sqlite3.Connection):
    print("Fill the Metadata table")
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("INSERT INTO metadata (created_at) VALUES (?)", (created_at,))
    conn.commit()


def insert_classes(conn: sqlite3.Connection, products: List[ProducesDatasetModel]) -> Dict[str, int]:
    print("Fill the data for Classes table")
    class_dataset_code_class_id_mapping: Dict[str, int] = {}  # to save the performance due to many SELECT
    cursor = conn.cursor()
    for product in products:  # type: ProducesDatasetModel
        class_dataset_code = product.class_dataset_code
        if not class_dataset_code_class_id_mapping.get(class_dataset_code):
            cursor.execute("INSERT INTO classes (dataset_code) VALUES (?)", (class_dataset_code,))
            class_dataset_code_class_id_mapping[class_dataset_code] = cursor.lastrowid
    conn.commit()
    return class_dataset_code_class_id_mapping


def insert_products(conn: sqlite3.Connection, products: List[ProducesDatasetModel], classes: Dict[str, int]):
    print("Fill the data for Products table")
    cursor = conn.cursor()
    for product in products:  # type: ProducesDatasetModel
        class_id: int = classes[product.class_dataset_code]  # guarantee
        cursor.execute(
            "INSERT INTO products (alpha_code, type, name, name_normalized, class_id) VALUES (?, ?, ?, ?, ?)",
            (product.alpha_code, product.type, product.name, product.name_normalized, class_id)
        )
    conn.commit()


def process_database(db_path: str, product_records: list, class_records: list, name_field: str):
    """Создает и заполняет одну базу данных"""
    print(f"\n{'=' * 60}")
    print(f"Processing database: {db_path}")
    print(f"Using name field: {name_field}")
    print(f"{'=' * 60}")

    remove_existing_db(db_path)
    conn = sqlite3.connect(db_path)
    create_tables(conn)

    mapped_products: List[ProducesDatasetModel] = map_airtable_product_record(
        product_records, class_records, name_field
    )
    class_name_id_mapping: Dict[str, int] = insert_classes(conn, mapped_products)
    insert_products(conn, mapped_products, class_name_id_mapping)
    insert_metadata(conn)

    conn.close()
    print(f"Database {db_path} created successfully")


def main():
    t_start = time()
    config: dict = load_config()

    airtable_conf = config["airtable"]
    base_id = airtable_conf["base_id"]
    api_key = airtable_conf["api_key"]

    # загружаем данные из Airtable
    print("Downloading the classes")
    classes_airtable = airtable_conf["tables"]["classes"]
    airtable_classes = Airtable(base_id, classes_airtable, api_key)
    class_records: list = airtable_classes.get_all()
    print(f"Downloaded {len(class_records)} records")

    print("Downloading the products")
    products_airtable = airtable_conf["tables"]["products"]
    airtable_products = Airtable(base_id, products_airtable, api_key)
    product_records: list = airtable_products.get_all()
    print(f"Downloaded {len(product_records)} records")

    # Получаем базовое имя БД из конфига
    base_db_name = config['sqlite']['db_name']
    db_name_without_ext = base_db_name.rsplit('.', 1)[0] if '.' in base_db_name else base_db_name
    db_ext = base_db_name.rsplit('.', 1)[1] if '.' in base_db_name else 'db'

    # Создаем первую БД с окончанием '_fr' и полем 'Nom'
    db_fr = f"{db_name_without_ext}_fr.{db_ext}"
    process_database(db_fr, product_records, class_records, 'Nom')

    # Создаем вторую БД с окончанием '_it' и полем 'Dénomination Italie '
    db_it = f"{db_name_without_ext}_it.{db_ext}"
    process_database(db_it, product_records, class_records, 'Dénomination Italie')

    t_end = time()
    print(f"\n{'=' * 60}")
    print(f"Import finished by {t_end - t_start:.1f} seconds")
    print(f"Created databases:")
    print(f"  - {db_fr}")
    print(f"  - {db_it}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
