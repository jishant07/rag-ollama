from mongoengine import *
from datetime import datetime
from ..db_helper_functions import reference_id_generator

class UploadedDocument(Document):

    document_id = StringField(required = True)
    name = StringField(required = True)
    location = StringField(required = True)
    created_at = DateTimeField(default = lambda : datetime.now())
    is_active = BooleanField(default=False)
    user_id = ReferenceField("User", required = True)