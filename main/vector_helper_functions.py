from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

client = QdrantClient("localhost", port=6333)

def document_splitter(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 100,
            length_function = len,
            is_separator_regex= False
        )
    
    return text_splitter.split_documents(documents)


def get_embedding_function():
    embeddings = OllamaEmbeddings(model='nomic-embed-text')
    return embeddings


def getQdrantCollection(collection_name):
    
    is_exists = client.collection_exists(collection_name=collection_name)

    print("ALL COLLECTIONS", client.get_collections())
    
    if not is_exists:

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    
    return QdrantVectorStore(
            collection_name=collection_name,
            client = client,
            embedding=get_embedding_function(),
        )


