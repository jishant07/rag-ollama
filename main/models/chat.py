from mongoengine import *

from main.models.message import ChatMessage
from .uploaded_document import UploadedDocument
import json

class Chat(Document):
    user_id = ReferenceField("User", required = True)
    selected_documents = ListField(StringField(), default = [])
    chat_title = StringField(required = True)
    chat_messages = ListField(EmbeddedDocumentField(ChatMessage), default=[])

    def get_chat_data(self):

        document_list = []
        for document in self.selected_documents:
            selected_document = json.loads(UploadedDocument.objects(document_id = document).first().to_json())
            document_list.append(selected_document)

        return {
            "chat_id" : str(self.pk),
            "documents" : document_list,
            "chat_title" : self.chat_title
        }
    
    def get_chat_messages(self):
        chat_data = []

        for chat in self.chat_messages:
            selected_chat = {
                "message_by" : chat.message_by,
                "message_text" : chat.message_text,
                "created_on" : chat.created
            }
            chat_data.append(selected_chat)

        return chat_data