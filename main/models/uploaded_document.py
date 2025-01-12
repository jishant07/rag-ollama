from mongoengine import *
from datetime import datetime

class UploadedDocuments(EmbeddedDocument):
    name = StringField()
    location = StringField()
    uploaded_at = DateTimeField(default=datetime.now())
