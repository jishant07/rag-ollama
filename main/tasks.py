from celery import shared_task
from celery.contrib.abortable import AbortableTask
from .models.uploaded_document import UploadedDocument
from .vector_helper_functions import *
from uuid import uuid4
from langchain_community.document_loaders import PyPDFLoader

def format_chunk(chunk, filename, document_id):
    chunk.metadata["source"] = filename
    chunk.metadata["document_id"] = document_id
    return chunk

def add_data_to_qdrant(data):
    print("Starting Thread Function...")
    loader = PyPDFLoader(data["location"])
    doc = loader.load()
    chunks = document_splitter(documents=doc)
    chunks = [format_chunk(chunk, filename=data["name"], document_id = data["document_id"]) for chunk in chunks]
    qcollection = getQdrantCollection(data["qdrant_collection_name"])
    qcollection.add_documents(documents=chunks, ids = [str(uuid4()) for _ in range(len(chunks))])

@shared_task(bind = True, base = AbortableTask)
def add_document_to_vector_db(self, data):

    add_data_to_qdrant(data)
    uploaded_document = UploadedDocument.objects.filter(document_id = data["document_id"]).first()
    uploaded_document.is_active = True

    uploaded_document.save()

    print("===Killing thread====" + data["document_id"])