from main import create_app
import json

app, celery = create_app()
app.app_context().push()

@app.route("/")
def start():
    return json.dumps({
        "message" : "success", 
        "result" : "Server is up and running"
    })