from flask import *
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from .helper_functions import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from uuid import uuid4

app = Flask(__name__,template_folder='templates',static_url_path='/static')
app.config["UPLOAD_FOLDER"] = "./sample_pdfs/uploads/"

@app.route("/")
def start():
    return json.dumps({
        "message" : "success", 
        "result" : "Server is up and running"
    })

@app.route("/upload", methods = ["POST"])
def document_uploader():
    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        server_file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        loader = PyPDFLoader(server_file_location)
        doc = loader.load()

        chunks = document_splitter(documents=doc)

        qcollection = getCollection("new_collection")
        qcollection.add_documents(documents=chunks, ids = [str(uuid4()) for _ in range(len(chunks))])

        return json.dumps({
            "message" : "success", 
            "result" : "File Upload Success at" + server_file_location
        })
    
    else:
        return json.dumps({
            "message" : "failure", 
            "result" : "Server Error : File not uploaded with correct key."
        })
    
@app.route("/get_answer", methods = ["POST"])
def get_answer():
    PROMPT_TEMPLATE = """
        You are a teacher that answers questions based on the following context:
        {context}

        ---
        Answer the student's question {question} based on the context given above.
        Don't mention that the answer is talking from context.
    """

    query_text = request.form["question"]

    vector_store = getCollection("new_collection")

    results = vector_store.similarity_search_with_score(
        query=query_text, k=3
    )

    # for doc, score in results:
    #     print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context= context_text, question = query_text)

    model = Ollama(model="mistral")
    response_text = model.invoke(prompt)
    print(response_text)

    return json.dumps({
        "status" : "success", 
        "message" : response_text
    })