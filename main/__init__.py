from flask import Flask
from .config import server_config
from .make_celery import celery_init_app

def create_app():
    app = Flask(__name__)

    from .auth.auth import auth
    from .document.document import document
    from .llm_chat.llm_chat import llm_chat

    app.register_blueprint(auth, url_prefix = "/auth")
    app.register_blueprint(document, url_prefix = "/document")
    app.register_blueprint(llm_chat, url_prefix = "/chat")

    app.config["CELERY"] = {
        "broker_url" : "redis://localhost/0", 
        "result_backend" : "redis://localhost/0",
        "broker_connection_retry_on_startup" : True
    }

    celery = celery_init_app(app=app)
    celery.set_default()

    return app, celery