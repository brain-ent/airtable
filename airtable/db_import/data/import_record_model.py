from dataclasses import dataclass

from urllib3.util import Url

@dataclass
class AirtableThumbnail:
    record_id: str

    name: str
    shape: tuple[int, int]
    url: Url

    def __init__(self):
        pass

@dataclass
class StoreCode:
    record_id: str

    name: str

    def __init__(self):
        pass

@dataclass
class ImportRecordModel:
    record_id: str

    name: str
    thumbnail: AirtableThumbnail
    status: str
    comments: str
    status_photoset: str
    store_codes: list[StoreCode]
    dataset_code: str
    photoset: Url
    amount_of_images: int
    percentage_high_confidence_recognition: float
    percentage_recognition: float
    amount_correct_recognition: int
    amount_correct_high_confidence_recognition: int

    def __init__(self):
        self.store_codes = []
