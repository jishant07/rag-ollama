from flask import Blueprint, request
from ..models.uploaded_document import UploadedDocument
from ..models.user import User
from main.server_helper_functions import token_required, success, failure
from main.db_helper_functions import reference_id_generator
import os
from werkzeug.utils import secure_filename

document = Blueprint("document", __name__)

@document.route("/upload", methods=["POST"])
@token_required
def upload_document(current_user):
    try:
        if 'file' in request.files:
            file_object = request.files["file"]
            temp_document = UploadedDocument()
            temp_document.name = secure_filename(file_object.filename) if secure_filename(file_object.filename) else reference_id_generator()

            check_if_file_name_exists = User.objects(id = current_user.get_id(), user_documents__name = temp_document.name)

            if len(check_if_file_name_exists) == 0 or True:

                check_path_exists = os.path.exists("./uploads/"+current_user.get_id())

                if not check_path_exists:
                    os.makedirs("./uploads/"+current_user.get_id())

                file_object.save(os.path.join("./uploads/"+current_user.get_id(), temp_document.name))
                temp_document.location = os.path.join("./uploads/"+current_user.get_id(), temp_document.name)
                user_docuements = current_user.user_documents if len(current_user.user_documents) > 0 else []
                user_docuements.append(temp_document)
                current_user.user_documents = user_docuements
                current_user.save()

                return success({"message" : "File Upload Successful!"})
            
            else: 
                raise Exception("You already have file with same name already uploaded")
        else:
            raise Exception("File not uploaded in the correct key")
    except Exception as e: 
        return failure(e)