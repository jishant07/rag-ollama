from mongoengine import *
from .uploaded_document import UploadedDocument

class Chat(Document):
    user_id = ReferenceField("User", required = True)
    selected_documents = ListField(ReferenceField("UploadedDocument"), default = [])