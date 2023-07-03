import csv

from airtable.export.data.export_record_model import ExportRecordModel
from airtable.export.test_data_generator import generate_mock_data_for_airtable


def export_to_csv(records: list[ExportRecordModel]):
    with open('dataset_info.csv', 'w', newline='') as csvfile:
        header = records[0].get_csv_header()
        writer = csv.DictWriter(csvfile, fieldnames=header, quoting=csv.QUOTE_NONNUMERIC)

        writer.writeheader()
        for record in records:
            writer.writerow(record.__dict__)


def example():
    records = generate_mock_data_for_airtable(1000)
    export_to_csv(records)
    # print(records)


example()
