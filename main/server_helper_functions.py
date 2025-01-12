import json

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