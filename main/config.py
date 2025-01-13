import os
from dotenv import dotenv_values

server_config = {}

if "FLASK_ENV" in os.environ.keys() and os.environ["FLASK_ENV"] == "development":
    server_config = dotenv_values('.env.develop')
else:
    server_config = dotenv_values('.env.local')


from mongoengine import *

db = connect(host = server_config["DB_URI"], db=server_config["DEFAULT_DATABASE"])
