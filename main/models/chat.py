from mongoengine import *
from .uploaded_document import UploadedDocument
import json

class Chat(Document):
    user_id = ReferenceField("User", required = True)
    selected_documents = ListField(StringField(), default = [])

    def get_chat_data(self):

        document_list = []
        for document in self.selected_documents:
            selected_document = json.loads(UploadedDocument.objects(document_id = document).first().to_json())
            document_list.append(selected_document)

        return {
            "chat_id" : str(self.pk),
            "documents" : document_list
        }