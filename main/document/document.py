from flask import Blueprint, request
from ..models.uploaded_document import UploadedDocument
from ..models.user import User
from main.server_helper_functions import token_required, success, failure
from main.db_helper_functions import reference_id_generator
import os
from werkzeug.utils import secure_filename
from ..tasks import add_document_to_vector_db
import json

document = Blueprint("document", __name__)

@document.route("/upload", methods=["POST"])
@token_required
def upload_document(current_user):
    try:
        if 'file' in request.files:
            file_object = request.files["file"]
            temp_document = UploadedDocument()
            temp_document.name = secure_filename(file_object.filename) if secure_filename(file_object.filename) else reference_id_generator()

            check_if_file_name_exists = UploadedDocument.objects(name = temp_document.name)

            if len(check_if_file_name_exists) == 0:

                check_path_exists = os.path.exists("./uploads/"+current_user.get_id())

                if not check_path_exists:
                    os.makedirs("./uploads/"+current_user.get_id())

                file_object.save(os.path.join("./uploads/"+current_user.get_id(), temp_document.name))
                temp_document.location = os.path.join("./uploads/"+current_user.get_id(), temp_document.name)
                temp_document.document_id = reference_id_generator()
                temp_document.user_id = current_user

                temp_document.save()
                
                task_data = {
                    "name" : temp_document.name,
                    "user_id" : current_user.get_id(), 
                    "location" : temp_document.location,
                    "document_id" : temp_document.document_id,
                    "qdrant_collection_name" : current_user.qdrant_collection_name
                }

                add_document_to_vector_db.delay(task_data)

                return success({"message" : "File Upload Successful!"})
            
            else: 
                raise Exception("You already have file with same name already uploaded")
        else:
            raise Exception("File not uploaded in the correct key")
    except Exception as e: 
        return failure(e)
    

@document.route("/list_documents", methods = ["GET"])
@token_required
def list_documents(current_user):
    try: 
        documents = json.loads(UploadedDocument.objects.filter(user_id = current_user.pk).to_json())
        return success({"user_documents" : documents})
    except Exception as e: 
        return failure(e)