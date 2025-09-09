"""
Vector database module for the AI Research Assistant.

This module manages vector database operations using Qdrant for document storage and retrieval.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import torch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabase:
    """Manages vector database operations using Qdrant for document storage and retrieval."""
    
    def __init__(
        self, 
        db_path: str = ":memory:", 
        collection_name: str = "documents",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the vector database.
        
        Args:
            db_path (str): Path to the database (":memory:" for in-memory)
            collection_name (str): Name of the collection
            embedding_model (str): Name of the embedding model to use
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize Qdrant client
        if db_path == ":memory:":
            self.client = QdrantClient(":memory:")
        else:
            Path(db_path).mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=db_path)
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_model = SentenceTransformer(embedding_model, device=device)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize collection
        self._initialize_collection()
        
        logger.info(f"Vector database initialized with {self.embedding_dim}D embeddings")
    
    def _initialize_collection(self) -> None:
        """Initialize the Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}' with {self.embedding_dim}D vectors")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.
        
        Args:
            text (str): Text to chunk
            chunk_size (int): Maximum words per chunk
            overlap (int): Number of overlapping words between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        if not text.strip():
            return []
        
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = ' '.join(chunk_words)
            if chunk.strip():
                chunks.append(chunk.strip())
                
            # Break if we've reached the end
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    def add_document(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a document to the vector database.
        
        Args:
            text (str): Document text
            metadata (Dict[str, Any]): Document metadata
            
        Returns:
            Dict[str, Any]: Result information
        """
        try:
            if not text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided',
                    'chunks_added': 0
                }
            
            # Generate chunks
            chunks = self.chunk_text(
                text, 
                metadata.get('chunk_size', 500),
                metadata.get('chunk_overlap', 50)
            )
            
            if not chunks:
                return {
                    'success': False,
                    'error': 'No chunks generated from text',
                    'chunks_added': 0
                }
            
            # Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = self.embedding_model.encode(chunks, show_progress_bar=True)
            
            # Create points for insertion
            points = []
            document_id = str(uuid.uuid4())
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = str(uuid.uuid4())
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk,
                        "chunk_id": i,
                        "document_id": document_id,
                        "document_name": metadata.get("filename", "unknown"),
                        "file_type": metadata.get("file_type", "unknown"),
                        "upload_time": metadata.get("upload_time", datetime.now().isoformat()),
                        "chunk_count": len(chunks),
                        **metadata.get("extra_metadata", {})
                    }
                )
                points.append(point)
            
            # Insert points into the database
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector database")
            
            return {
                'success': True,
                'chunks_added': len(chunks),
                'document_id': document_id,
                'total_characters': len(text)
            }
            
        except Exception as e:
            logger.error(f"Error adding document to vector database: {e}")
            return {
                'success': False,
                'error': str(e),
                'chunks_added': 0
            }
    
    def search_similar(
        self, 
        query: str, 
        limit: int = 5, 
        score_threshold: float = 0.0,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents/chunks.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            score_threshold (float): Minimum similarity score
            filter_conditions (Optional[Dict[str, Any]]): Additional filter conditions
            
        Returns:
            List[Dict[str, Any]]: List of search results
        """
        try:
            if not query.strip():
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Build filter if conditions provided
            search_filter = None
            if filter_conditions:
                conditions = []
                for field, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    search_filter = Filter(must=conditions)
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit,
                with_payload=True,
                query_filter=search_filter,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_result:
                results.append({
                    "text": result.payload["text"],
                    "score": result.score,
                    "document_name": result.payload.get("document_name", "unknown"),
                    "document_id": result.payload.get("document_id", "unknown"),
                    "chunk_id": result.payload.get("chunk_id", 0),
                    "file_type": result.payload.get("file_type", "unknown"),
                    "upload_time": result.payload.get("upload_time", "unknown")
                })
            
            logger.info(f"Found {len(results)} similar chunks for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the documents in the database.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get unique documents
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=1000,  # Adjust based on your needs
                with_payload=True
            )
            
            documents = {}
            total_chunks = 0
            
            for point in scroll_result[0]:
                doc_id = point.payload.get("document_id", "unknown")
                doc_name = point.payload.get("document_name", "unknown")
                
                if doc_id not in documents:
                    documents[doc_id] = {
                        "name": doc_name,
                        "chunks": 0,
                        "file_type": point.payload.get("file_type", "unknown"),
                        "upload_time": point.payload.get("upload_time", "unknown")
                    }
                
                documents[doc_id]["chunks"] += 1
                total_chunks += 1
            
            return {
                "total_documents": len(documents),
                "total_chunks": total_chunks,
                "total_vectors": collection_info.points_count,
                "documents": list(documents.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "total_vectors": 0,
                "documents": []
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the documents in the database.
        This is an alias for get_document_stats() for backward compatibility.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        return self.get_document_stats()
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks from the database.
        
        Args:
            document_id (str): ID of the document to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete points with matching document_id
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            
            logger.info(f"Successfully deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def clear_database(self) -> bool:
        """
        Clear all documents from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self._initialize_collection()
            
            logger.info("Successfully cleared vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.
        
        Returns:
            Dict[str, Any]: Collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": collection_info.points_count,
                "vectors_config": {
                    "size": collection_info.config.params.vectors.size,
                    "distance": collection_info.config.params.vectors.distance.name
                },
                "status": collection_info.status.name
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}