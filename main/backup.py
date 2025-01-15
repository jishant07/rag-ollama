from flask import *
from .make_celery import celery_init_app
from main.config import server_config
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from .vector_helper_functions import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from qdrant_client.models import Filter, MatchValue, FieldCondition, SearchParams
from uuid import uuid4
from .models.user import User

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./uploads/"

@app.route("/")
def start():
    return json.dumps({
        "message" : "success", 
        "result" : "Server is up and running"
    })

# def watch_changes_in_user_document():
#     print("Starting Thread...")
#     try:
#         collection = User._get_collection()
#         pipeline = [
#             {
#                 "$match": {
#                     "$and": {
#                         "updateDescription.updatedFields.user_documents": {"$exists": True},
#                         "operationType" : "update"
#                     }
#                 }
#             }
#         ]
#         with collection.watch(pipeline = pipeline, full_document="updateLookup") as stream: 
#             print("Listening to changes in the User Document")
#             for change in stream:
#                 print("=======CHANGE STREAM=======", change)
#                 full_document = change['fullDocument']
#                 list_of_documents = change['updateDescription']['updatedFields']['user_documents']

#                 print(list_of_documents)

#                 for document in list_of_documents:
#                     if document["is_active"] == False and document["document_id"] not in [t.getName() for t in threading.enumerate()]:
#                         threading.Thread(target=add_data_to_qdrant, daemon=False, name=document['document_id'], args=(document,full_document)).start()
#     except Exception as e:
#         return e
    
# # Create change watch thread

# change_stream_thread = threading.Thread(target=watch_changes_in_user_document, daemon=True, name="User-Collection-Thread")
# change_stream_thread.start()

# @app.route("/upload", methods = ["POST"])
# def document_uploader():
#     if 'file' in request.files:
#         file = request.files['file']
#         filename = file.filename
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         server_file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#         loader = PyPDFLoader(server_file_location)
#         doc = loader.load()

#         chunks = document_splitter(documents=doc)

#         chunks = [format_chunk(chunk, filename=filename) for chunk in chunks]

#         qcollection = getQdrantCollection("test_user_collection")
#         qcollection.add_documents(documents=chunks, ids = [str(uuid4()) for _ in range(len(chunks))])

#         return json.dumps({
#             "message" : "success", 
#             "result" : "File Upload Success at" + server_file_location
#         })
    
#     else:
#         return json.dumps({
#             "message" : "failure", 
#             "result" : "Server Error : File not uploaded with correct key."
#         })
    
# @app.route("/get_answer", methods = ["POST"])
# def get_answer():
#     PROMPT_TEMPLATE = """
#         You are a teacher that answers questions based on the following context:
#         {context}

#         ---
#         Answer the student's question {question} based on the context given above.
#         Don't mention that the answer is talking from context.
#     """

#     query_text = request.form["question"]

#     vector_store = getQdrantCollection("test_user_collection")

#     results = vector_store.similarity_search_with_score(
#         query=query_text,
#         k=3,
#         query_filter=Filter(
#         should=[
#             FieldCondition(
#                 key="metadata.source",
#                 match=MatchValue(
#                     value="The Alchemist by Paulo Coelho-1.pdf",
#                 ),
#             )
#         ]
#     ),
#     )

#     # print(results)

#     # for doc, score in results:
#     #     print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")

#     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = prompt_template.format(context= context_text, question = query_text)

#     def generate():
#         model = Ollama(model="mistral")
#         for chunk in model.stream(prompt):
#             yield chunk 

#     return generate(), {"Content-Type": "text/plain"}