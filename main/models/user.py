from mongoengine import *
from datetime import datetime
from .uploaded_document import UploadedDocument
from ..db_helper_functions import reference_id_generator

class User(Document):
    name = StringField(required = True)
    email = EmailField(required = True, unique = True)
    password = StringField(required = True)
    qdrant_collection_name = StringField(required = True)
    created = DateTimeField(default = lambda : datetime.now())
    user_documents = ListField(EmbeddedDocumentField(UploadedDocument), default = [])

    def get_id(self):
        return str(self.pk)
    
    def save(self, *args, **kwargs):
        if not self.qdrant_collection_name:
            self.qdrant_collection_name = "user_" + reference_id_generator() + "_collection"

        return super(User, self).save(*args, **kwargs)
    
