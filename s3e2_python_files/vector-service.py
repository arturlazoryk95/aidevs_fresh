from qdrant_client import QdrantClient
from qdrant_client.http import models
from uuid import uuid4
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .openai_service import OpenAIService

class VectorService:
    def __init__(self, openai_service: OpenAIService):
        self.client = QdrantClient(
            url=config('QDRANT_URL'),
            api_key=config('QDRANT_API_KEY')
        )
        self.openai_service = openai_service

    async def ensure_collection(self, name: str):
        collections = self.client.get_collections()
        if not any(c.name == name for c in collections.collections):
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=1024,
                    distance=models.Distance.COSINE
                )
            )

    async def initialize_collection_with_data(self, name: str, points: List[Dict]):
        collections = self.client.get_collections()
        if not any(c.name == name for c in collections.collections):
            await self.ensure_collection(name)
            await self.add_points(name, points)

    async def add_points(self, collection_name: str, points: List[Dict]):
        points_to_upsert = []
        
        for point in points:
            embedding = await self.openai_service.create_jina_embedding(point['text'])
            
            points_to_upsert.append(models.PointStruct(
                id=str(point.get('id', uuid4())),
                vector=embedding,
                payload={
                    'text': point['text'],
                    **(point.get('metadata', {}))
                }
            ))

        points_file_path = Path(__file__).parent / 'points.json'
        with open(points_file_path, 'w') as f:
            json.dump([p.dict() for p in points_to_upsert], f, indent=2)

        self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points_to_upsert
        )

    async def perform_search(
        self, 
        collection_name: str, 
        query: str, 
        filter_: Dict = None, 
        limit: int = 5
    ):
        query_embedding = await self.openai_service.create_jina_embedding(query)
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=filter_,
            with_payload=True
        )
