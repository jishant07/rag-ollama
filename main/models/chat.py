from mongoengine import *

class Chat(Document):
    user_id = ReferenceField("User", required = True)
    selected_documents = ListField(StringField(), default = [])