from functools import wraps
import json
from cerberus import Validator
from flask import request
import jwt
from .config import server_config
from .models.user import User

def success(data):
    return json.dumps({
        "success" : True,
        **data
    })

def failure(e):
    return json.dumps({
        "success" : False,
        "message" : str(e)
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
           return failure({'message': 'a valid token is missing'})
       try:
           print(server_config["JWT_SECRET"])
           data = jwt.decode(token, server_config["JWT_SECRET"], algorithm="HS256")
           current_user = User.objects(id = data["user_id"]).first()
       except:
           return failure({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator