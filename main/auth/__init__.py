from flask import Blueprint
from numpy import DataSource
from ..models.users import User
from ..models.uploaded_document import UploadedDocuments
import time
from ..server_helper_functions import *

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET"])
def auth_hello():
    try:
        test_user = User()
        test_user.email = "jishanta{time}@gmail.com".format(time = time.time())
        test_user.password = "test_password"
        temp_document = UploadedDocuments()
        temp_document.location = "test"
        temp_document.name= "test_name"
        test_user.uploaded_document_list = [temp_document]
        result = test_user.save()
        return success(data={"id" : str(result.id), "email" : result.email})
    except Exception as e:
        return failure(e)
    
@auth.route("/add_uploaded_file_to_user", methods = ["POST"])
def add_uploaded_file():
    try: 
        user = User.objects.first().to_json()
        del user["_id"]
        print(user)
        return success(data=user)
    except Exception as e:
        return failure(e)

