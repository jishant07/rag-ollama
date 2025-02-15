from flask import Blueprint, request
from main.models.user import User
import bcrypt
from ..server_helper_functions import *
import jwt
from datetime import datetime, timedelta, timezone

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
                temp_user.save()
                
                access_token = create_access_token(temp_user.get_id())

                return success({"message" : "User Signup Success!", "access_token" : access_token})
            else:
                raise Exception("User with same email already exists")
        else:
            raise Exception("Error in requst schema")
    except Exception as e:
        return failure(e)
    

@auth.route("/signin", methods = ["POST"])
def signin():
    login_schema = {
        "email" : {"type" : "string", "required" : True , "empty" : False},
        "password" : {"type" : "string", "required" : True, "empty" : False},
    }

    try:
        data = request.get_json()
        if(schema_validator(login_schema, data)):
            check_user = User.objects(email=data["email"]).first()
            if check_user != None:

                password_match = bcrypt.checkpw(data["password"].encode('utf-8'), check_user.password.encode('utf-8'))

                if password_match: 
                    access_token = create_access_token(check_user.get_id())
                    return success({"message" : "Signin Successful", "access_token" : access_token})
                else: 
                    raise Exception("Password mis-match")
            else:
                raise Exception("User not found")
        else:
            raise Exception("Error in request schema")
    except Exception as e: 
        return failure(e)
