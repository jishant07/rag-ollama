from flask import Blueprint, Response, request, stream_with_context
from .prompts import system_prompt, contextualize_question_prompt

from main.models.message import ChatMessage
from main.server_helper_functions import token_required, success, failure, schema_validator
from main.vector_helper_functions import getQdrantCollection
from ..models.uploaded_document import UploadedDocument
from ..models.chat import Chat
from bson import ObjectId
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import OllamaLLM
from qdrant_client.models import Filter, MatchValue, FieldCondition
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import AIMessage, HumanMessage


llm_chat = Blueprint("llm_chat", __name__)

@llm_chat.route("/create_chat", methods=["POST"])
@token_required
def create_chat(current_user):
    try:
        create_chat_schema = {
            "selected_documents" : {"type" : ["string", "list"], "required" : True , "empty" : False},
            "chat_title" : {"type" : "string", "required" : True, "empty" : False}
        }
        data = request.get_json()
        document_array = []
        if schema_validator(create_chat_schema, data):
            list_chat = Chat.objects(chat_title__iexact = data["chat_title"], user_id = ObjectId(current_user.get_id())).first()
            if not list_chat : 
                for document_id in data["selected_documents"]:
                    not_exits = UploadedDocument.objects(user_id = current_user.id , document_id = document_id)
                    if not not_exits:
                        raise Exception("Some of the document selected are invalid")
                    document_array.append(document_id)

                chat_object = Chat()
                chat_object.chat_title = data["chat_title"]
                chat_object.user_id = current_user
                chat_object.selected_documents = document_array
                chat_object.save()

                return success({"message" : "Chat successfully added", "chat_id": str(chat_object.pk)})
            else:
                raise Exception("Chat with same title already exists")
        else:
            raise Exception("Schema Structure Error")
    except Exception as e:
        return failure(e)
    
@llm_chat.route("/list_chats", methods = ["GET"])
@token_required
def getChats(current_user):
    try:
        chat_data = []
        chat_list = Chat.objects(user_id = current_user)
        for chat in chat_list:
            chat_data.append(chat.get_chat_data())
        return success({"chat_list" : chat_data})
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
                
                model = OllamaLLM(model="llama3.1:8b")

                vector_store = getQdrantCollection(current_user.qdrant_collection_name)

                filter_condition = []

                def get_filter(document_id: str):
                    return FieldCondition(key="metadata.document_id", match=MatchValue(value=document_id))

                for document_id in chat_data.selected_documents:
                    filter_condition.append(get_filter(document_id))

                vector_retriver = vector_store.as_retriever(
                    seach_type = "similarity_score_threshold",
                    search_kwargs = {
                        "k" : 20,
                        "score_threshold" : 0.5,
                        "filter": Filter(
                            should=filter_condition
                        )
                    }
                )

                prompt_context = ChatPromptTemplate.from_messages(
                    [
                        ("system", contextualize_question_prompt),
                        MessagesPlaceholder(variable_name="chat_history"),
                        ("human", "{input}")
                    ]
                )

                history_aware = create_history_aware_retriever(model,vector_retriver,prompt_context)
                
                main_question_answer_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                        MessagesPlaceholder(variable_name="chat_history"),
                        ("human", "{input}")
                    ]
                )


                question_answer_chain = create_stuff_documents_chain(model, main_question_answer_prompt)
                chain = create_retrieval_chain(history_aware, question_answer_chain)

                chat_history = [
                    AIMessage(message.message_text) if message.message_by == 'agent' else HumanMessage(message.message_text)
                    for message in chat_data.chat_messages
                ]

                def generate():

                    for chunk in chain.stream({"input": data["query_text"], "chat_history": chat_history}):
                        if answer_chunk := chunk.get("answer"):
                            yield answer_chunk

                return Response(stream_with_context(generate()), content_type="text/event-stream")
            else:
                raise Exception("Chat not found")
        else: 
            raise Exception("Request Schema Error")
    except Exception as e: 
        return failure(e)
    
@llm_chat.route("/save_chat_message", methods = ["POST"])
@token_required
def save_chat_message(current_user):

    chat_schema = {
        "chat_id" : {"type" : "string", "required" : True , "empty" : False},
        "message_by" : {"type": "string", "required": True, "empty" : False, 'allowed': ['agent', 'user',]},
        "message_text" : {"type" : "string", "required" : True, "empty" : False}
    }

    data = request.get_json()

    try:
        if(schema_validator(chat_schema, data)):
            chat_object = Chat.objects.filter(id = data["chat_id"], user_id = ObjectId(current_user.get_id())).first()
            chat_message_object = ChatMessage()
            chat_message_object.message_by = data["message_by"]
            chat_message_object.message_text = data["message_text"]

            chat_object.chat_messages.append(chat_message_object)

            chat_object.save()

            return success({"message_added" : True})
        else:
            raise Exception("Schema Error")
    except Exception as e:
        print(e)
        return failure(e)
    

@llm_chat.route("/list_chat_messages", methods=["POST"])
@token_required
def list_chat_messages(current_user):
    list_chat_schema = {
         "chat_id" : {"type" : "string", "required" : True , "empty" : False}
    }

    try:
        data = request.get_json()
        print(data)
        if schema_validator(list_chat_schema, data):
            chat_object = Chat.objects.filter(id = data["chat_id"], user_id = ObjectId(current_user.get_id())).first()
            return success({"chat_messages" : chat_object.get_chat_messages()})
        else:
            raise Exception("SChema Error")
    except Exception as e:
        return failure(e)