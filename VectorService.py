from openai import OpenAI
from decouple import config
import tiktoken
from ChatService import ChatService
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from uuid import uuid4

class VectorService():
    def __init__(self, openai_service: ChatService):
        self.openai_service=openai_service
        self.vector_service = QdrantClient(
            url=config('QDRANT_LE_DATABASE_URL'),
            api_key=config('QDRANT_LE_DATABASE_API_KEY'),
        )
        self.collection_name=self.ensure_collection()

    def ensure_collection(self):
        collection_name='le_data',

        try:
            self.vector_service.get_collection(collection_name=collection_name)
            return collection_name
        except Exception as e:
            self.vector_service.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.DOT),
            )
            return collection_name
    
    def add_points(self, text, object):
        operation = self.vector_service.upsert(
            collection_name=self.collection_name,
            points= [
                PointStruct(
                    id=str(uuid4()),
                    vector = self.openai_service.create_embedding(text),
                    payload = object
                )
            ]
        )
        return operation

    


    