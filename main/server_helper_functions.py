from functools import wraps
from cerberus import Validator
from flask import jsonify, request
import jwt
from .config import server_config
from .models.user import User
import string
import re

def success(data):
    return jsonify({
        "success" : True,
        **data
    })

def failure(e):
    return jsonify({
        "success" : False,
        "message" : str(e)
    })

def failure_withkeys(e):
    return jsonify({
        "success" : False, 
        **e
    })

def schema_validator(schema, body):
    validator = Validator(schema)
    validator.allow_unknown = False
    if validator.validate(body):
        return True
    else:
        print("SCHEMA ERROR => ", validator.errors)
        return False
    

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-token' in request.headers:
           token = request.headers['x-access-token']
 
       if not token:
           return failure_withkeys({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, server_config["JWT_SECRET"], algorithms=["HS256"])
           current_user = User.objects(id = data["user_id"]).first()
       except:
           return failure_withkeys({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator


def clean_file_name(fileName):
    chars = re.escape(string.punctuation) + ' '
    return re.sub('['+chars+']', '_',fileName)