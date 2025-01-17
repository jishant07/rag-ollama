from flask import Blueprint, request

from main.server_helper_functions import token_required, success, failure, schema_validator
from main.vector_helper_functions import getQdrantCollection
from ..models.uploaded_document import UploadedDocument
from ..models.chat import Chat
from bson import ObjectId
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from qdrant_client.models import Filter, MatchValue, FieldCondition, SearchParams

llm_chat = Blueprint("llm_chat", __name__)

@llm_chat.route("/create_chat", methods=["POST"])
@token_required
def create_chat(current_user):
    try:
        create_chat_schema = {
            "selected_documents" : {"type" : ["string", "list"], "required" : True , "empty" : False},
        }
        data = request.get_json()
        document_array = []
        if schema_validator(create_chat_schema, data):
            for document_id in data["selected_documents"]:
                not_exits = UploadedDocument.objects(user_id = current_user.id , document_id = document_id)
                if not not_exits:
                    raise Exception("Some of the document selected are invalid")
                document_array.append(document_id)

            chat_object = Chat()
            chat_object.user_id = current_user
            chat_object.selected_documents = document_array
            chat_object.save()

            return success({"message" : "Chat successfully added"})
        else:
            raise Exception("Schema Structure Error")
    except Exception as e:
        return failure(e)
    
@llm_chat.route("/ask_question", methods = ["POST"])
@token_required
def ask_question(current_user):

    try:
        chat_schema = {
            "chat_id" : {"type" : "string", "required" : True , "empty" : False},
            "query_text" : {"type" : "string", "required" : True , "empty" : False}
        }

        data = request.get_json()

        if schema_validator(chat_schema, data):
            
        
            chat_data = Chat.objects(pk = data["chat_id"], user_id=ObjectId(current_user.pk)).first()

            if chat_data:
                
                vector_store = getQdrantCollection(current_user.qdrant_collection_name)

                filter_condition = []

                def get_filter(document_id: str):
                    return FieldCondition(key="metadata.document_id", match=MatchValue(value=document_id))

                for document_id in chat_data.selected_documents:
                    filter_condition.append(get_filter(document_id))

                results = vector_store.similarity_search_with_score(
                    query=data["query_text"],
                    k=10,
                    filter=Filter(
                        should=filter_condition
                    )
                )

                PROMPT_TEMPLATE = """
                    You are a teacher that answers questions based on the following context:
                    {context}

                    ---
                    Answer the student's question {question} based on the context given above.
                    Don't mention that the answer is talking from context.
                """

                context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
                prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
                prompt = prompt_template.format(context= context_text, question = data["query_text"])

                def generate():
                    model = Ollama(model="mistral")
                    for chunk in model.stream(prompt):
                        yield chunk 

                return generate(), {"Content-Type": "text/plain"}
            else:
                raise Exception("Chat not found")
        else: 
            raise Exception("Request Schema Error")
    except Exception as e: 
        return failure(e)