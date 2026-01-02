import uuid
from typing import List, Tuple, Dict, Any, Set
from qdrant_client import QdrantClient
from qdrant_client.http import models
from . import config

class QdrantStorage:
    def __init__(self):
        print(f"Connecting to Qdrant at {config.QDRANT_PATH}...")
        self.client = QdrantClient(path=config.QDRANT_PATH)
        self.ensure_collection()

    def ensure_collection(self):
        """Create the collection if it doesn't exist."""
        if not self.client.collection_exists(collection_name=config.COLLECTION_NAME):
            print(f"Creating collection '{config.COLLECTION_NAME}'...")
            self.client.create_collection(
                collection_name=config.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=config.VECTOR_SIZE,
                    distance=models.Distance.COSINE
                )
            )
        else:
            # print(f"Collection '{config.COLLECTION_NAME}' already exists.")
            pass

    def check_existing(self, story_ids: List[str]) -> Set[str]:
        """
        Check which of the given story IDs already exist in the collection.
        Returns a set of existing story IDs.
        """
        # Qdrant requires UUIDs or integers for Point IDs.
        # We process story IDs into UUIDs (deterministically) to query.
        
        # Map UUID back to original story_id to return the set of EXISTING original IDs
        uuid_map = {}
        points_to_check = []
        
        for sid in story_ids:
            # Deterministic UUID generation
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, sid))
            uuid_map[point_id] = sid
            points_to_check.append(point_id)
            
        # Retrieve by ID (metadata_only=True to save bandwidth)
        existing_points = self.client.retrieve(
            collection_name=config.COLLECTION_NAME,
            ids=points_to_check,
            with_payload=False,
            with_vectors=False
        )
        
        existing_sids = set()
        for point in existing_points:
            original_sid = uuid_map.get(point.id)
            if original_sid:
                existing_sids.add(original_sid)
                
        return existing_sids

    def upsert_stories(self, stories_data: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:
        """
        Upsert embeddings and metadata to Qdrant.
        
        Args:
            stories_data: List of (story_id, embedding, metadata)
            
        Returns:
            Number of points upserted.
        """
        if not stories_data:
            return 0
            
        points = []
        for story_id, embedding, metadata in stories_data:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, story_id))
            
            points.append(models.PointStruct(
                id=point_id,
                vector=embedding,
                payload=metadata
            ))
            
        try:
            self.client.upsert(
                collection_name=config.COLLECTION_NAME,
                points=points
            )
            return len(points)
        except Exception as e:
            print(f"Error upserting batch: {e}")
            return 0
