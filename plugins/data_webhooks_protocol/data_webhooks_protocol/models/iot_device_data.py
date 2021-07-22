from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow.utils import EXCLUDE

class IOTDeviceData:
    def __init__(self, data: dict = None) -> None:
        self.data = data

class IOTDeviceDataSchema(Schema):

    class Meta:
        model_class = IOTDeviceData
        unknown = EXCLUDE
    
    data = fields.Dict(
        data_key="data"
    )