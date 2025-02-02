from mongoengine import *
from datetime import datetime

class ChatMessage(EmbeddedDocument):
    message_by = StringField(required = True)
    message_text = StringField(required = True)
    created = DateTimeField(default = lambda : datetime.now())