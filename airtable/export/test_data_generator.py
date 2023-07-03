import random

from random_word import RandomWords

from airtable.export.data.export_record_model import ExportRecordModel

word_generator = RandomWords()


def generate_mock_data_for_airtable(count: int):
    records: list[ExportRecordModel] = []
    for i in range(0, count):
        record = ExportRecordModel()
        set_name_and_code(record)
        record.photoset = f"https://server/view?{record.name}"
        # set_sigale_codes(record, i)
        record.amount_of_images = random.randint(3, 9)
        set_report_data(record)
        records.append(record)
        print(f"generated i record: {record}")
    return records


def set_name_and_code(record: ExportRecordModel):
    keywords = []
    keywords.append(word_generator.get_random_word())
    keywords.append(word_generator.get_random_word())

    record.name = f"{keywords[0]} {keywords[1]}"
    record.dataset_code = f"{keywords[0]}.{keywords[1]}"


def set_sigale_codes(record: ExportRecordModel, index):
    sigale_codes = []
    for i in range(0, random.randint(1, 2)):
        sigale_codes.append(4000 + index * 10 + i)
    record.sigale_product_code = sigale_codes


def set_report_data(record: ExportRecordModel):
    record.report_field_1 = random.randint(1, 10000) / 10000.0
    record.report_field_2 = random.randint(1, 10000) / 10000.0
    record.report_field_3 = random.randint(100, 150)
    record.report_field_4 = random.randint(10, 100)
