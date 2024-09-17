class ExportRecordModel:
    name: str
    # will be ignored by airtable
    # thumbnail: str
    status: str
    comments: str
    status_photoset: str
    # will be ignored by airtable
    # sigale_product_code: str
    dataset_code: str
    photoset: str
    amount_of_images: int
    report_field_1: float
    report_field_2: float
    report_field_3: int
    report_field_4: int

    def __init__(self):
        self.name = ""
        self.thumbnail = ""
        self.status = "OK"
        self.comments = ""
        self.status_photoset = "Yes"
        # self.sigale_product_code = ""
        self.photoset = ""
        self.amount_of_images = 0
        self.report_field_1 = 0.9
        self.report_field_2 = 0.9
        self.report_field_3 = 123
        self.report_field_4 = 23

    # def to_dict(self):
    #     return self.__dict__.values()

    def get_csv_header(self):
        return ['name', 'thumbnail', 'status', 'comments', 'status_photoset', 'sigale_product_code', 'dataset_code',
                'photoset', 'amount_of_images', 'report_field_1', 'report_field_2', 'report_field_3', 'report_field_4']
        # return ['name', 'thumbnail', 'status', 'comments', 'status_photoset', 'dataset_code', 'photoset', 'amount_of_images', 'report_field_1', 'report_field_2', 'report_field_3', 'report_field_4']
