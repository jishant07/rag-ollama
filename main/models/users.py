from mongoengine import *

from .uploaded_document import UploadedDocuments

class User(Document):
    email = EmailField(unique = True)
    password = StringField()
    uploaded_document_list = ListField(EmbeddedDocumentField(UploadedDocuments) , required = True)
