from flask import Blueprint, request
from main.models.user import User
import bcrypt
from ..server_helper_functions import *
import jwt
from datetime import datetime, timedelta

auth = Blueprint("auth", __name__)


@auth.route("/signup", methods = ["POST"])
def signup():
    data = request.get_json()
    signup_schema = {
        "email" : {"type" : "string", "required" : True , "empty" : False},
        "password" : {"type" : "string", "required" : True, "empty" : False},
        "name" : {"type" : "string", "required" : True, "empty" : False}
    }
    try:
        if schema_validator(signup_schema, data):
            is_user_exists = User.objects(email=data["email"]).first()
            if is_user_exists == None:
                temp_user = User()
                temp_user.email = data["email"]
                temp_user.password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                temp_user.name = data["name"]
                result = temp_user.save()
                
                access_token_payload =  {}
                access_token_payload["exp"] = datetime.now(tz = datetime.timezone.utc) + datetime.timedelta(minutes=30),
                access_token_payload["user_id"] = result.get_id()

                print(server_config["JWT_SECRET"])

                access_token = jwt.encode(
                    payload=access_token_payload, 
                    key=server_config["JWT_SECRET"],
                    algorithm="HS256"
                )

                return success({"message" : "User Signup Success!", "access_token" : access_token})
            else:
                raise Exception("User with same email already exists")
        else:
            raise Exception("Error in requst schema")
    except Exception as e:
        return failure(e)
    

@auth.route("/protected", methods=["GET"])
@token_required
def protected_test(current_user):
    print(current_user.get_id())
    return "Reached a protected route"
