from mongoengine import *
from datetime import datetime

class User(Document):
    name = StringField(required = True)
    email = EmailField(required = True, unique = True)
    password = StringField(required = True)
    created = DateTimeField(default = lambda : datetime.now())


    def get_id(self):
        return str(self.pk)