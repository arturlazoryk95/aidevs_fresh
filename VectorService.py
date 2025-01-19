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
        collection_name='le_countries_database_v2'

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
    
    def search(self, text) -> list[dict]:
        embedding = self.openai_service.create_embedding(text)
        search_results = self.vector_service.query_points(
            collection_name=self.collection_name,
            query = embedding,
            with_payload=True,
            limit=3,
        )
        return search_results

    # def search(self, text) -> list[dict]:
    #     try:
    #         # Get the embedding for the search query
    #         embedding = self.openai_service.create_embedding(text)
            
    #         # Debug: Print collection stats
    #         print(f"\nSearching in collection: {self.collection_name}")
    #         count = self.vector_service.count(collection_name=self.collection_name)
    #         print(f"Total points in collection: {count}")

    #         # Perform the search with adjusted parameters
    #         search_results = self.vector_service.search(
    #             collection_name=self.collection_name,
    #             query_vector=embedding,
    #             with_payload=True,
    #             with_vectors=False,  # We don't need the vectors returned
    #             limit=5,
    #             score_threshold=0.0  # Accept all results and we'll see the scores
    #         )

    #         # Debug: Print raw results
    #         print(f"\nRaw search results:")
    #         for idx, result in enumerate(search_results):
    #             print(f"Result {idx + 1}:")
    #             print(f"  Score: {result.score}")
    #             print(f"  Payload: {result.payload}")

    #         return search_results

    #     except Exception as e:
    #         print(f"Search error: {str(e)}")
    #         raise


    


    