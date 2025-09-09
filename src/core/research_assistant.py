"""
Research Assistant module for the AI Research Assistant.

This module coordinates document processing, vector search, and AI responses.
"""

import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import tempfile
import os
from pathlib import Path

from groq import Groq

from core.document_processor import DocumentProcessor
from core.vector_database import VectorDatabase
from utils.config import ConfigManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchAssistant:
    """Main class that coordinates document processing, vector search, and AI responses."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Initialize the Research Assistant.
        
        Args:
            config (Optional[ConfigManager]): Configuration manager instance
        """
        self.config = config or ConfigManager()
        
        # Initialize components
        self.doc_processor = DocumentProcessor(
            max_file_size_mb=self.config.get('max_file_size_mb', 50)
        )
        
        self.vector_db = VectorDatabase(
            db_path=self.config.get('vector_db_path', ':memory:'),
            collection_name=self.config.get('collection_name', 'documents'),
            embedding_model=self.config.get('embedding_model', 'all-MiniLM-L6-v2')
        )
        
        # Initialize Groq client
        groq_api_key = self.config.get('groq_api_key')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in configuration")
        
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_model = self.config.get('groq_model', 'llama3-8b-8192')
        
        # Conversation history (in-memory for this session)
        self.conversation_history = []
        
        logger.info("Research Assistant initialized successfully")
    

    def process_documents(self, files: List[Any]) -> str:
        if not files:
            return "No files uploaded."
        
        results = []
        successful_uploads = 0
        total_files = len(files)
        
        for file_idx, file in enumerate(files, 1):
            try:
                # Gradio gives either a string path or an UploadedFile object
                if isinstance(file, str) and os.path.exists(file):
                    file_path = file
                    filename = Path(file).name
                elif hasattr(file, 'name') and os.path.exists(file.name):
                    file_path = file.name
                    filename = Path(file.name).name
                else:
                    raise Exception("Cannot read uploaded file: unsupported type")
                
                file_size = os.path.getsize(file_path)
                logger.info(f"Temporary file ready: {file_path} ({file_size} bytes)")
                if file_size == 0:
                    raise Exception("Uploaded file is empty.")
                
                # Process the document
                result = self.process_single_document(file_path, filename)
                results.append(result)
                
                if "successfully processed" in result.lower():
                    successful_uploads += 1
                    logger.info(f"✅ Successfully processed: {filename}")
                else:
                    logger.error(f"❌ Failed to process: {filename}")
                
            except Exception as e:
                error_msg = f"❌ Error processing '{getattr(file, 'name', str(file))}': {e}"
                logger.error(error_msg)
                results.append(error_msg)
        
        # Summary
        if successful_uploads > 0:
            summary = f"\n\n📊 **Summary**: Successfully processed **{successful_uploads}/{total_files}** files."
            summary += "\n\n✅ Your documents are now available in the knowledge base."
        else:
            summary = f"\n\n❌ **Summary**: No files were successfully processed out of {total_files} files."
            summary += "\n\n💡 **Tips**: Make sure your files are not corrupted, encrypted, or scanned images."
        
        return "\n".join(results) + summary

    
    def process_single_document(self, file_path: str, filename: str) -> str:
        """
        Process a single document and add it to the vector database.
        
        Args:
            file_path (str): Path to the document file
            filename (str): Original filename
            
        Returns:
            str: Status message about the processing
        """
        try:
            logger.info(f"Starting text extraction for: {filename}")
            
            # Extract text from document
            extraction_result = self.doc_processor.extract_text(file_path, filename)
            
            if not extraction_result['success']:
                error_msg = f"❌ Failed to process '{filename}': {extraction_result['error']}"
                logger.error(error_msg)
                return error_msg
            
            # Check if we got meaningful text
            extracted_text = extraction_result['text']
            # Count meaningful lines instead of characters
            lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
            if not lines:
                return f"❌ '{filename}' appears to be empty or contains no meaningful lines to process."

            
            # Prepare metadata
            metadata = {
                'filename': filename,
                'file_type': extraction_result.get('file_type', 'unknown'),
                'upload_time': datetime.now().isoformat(),
                'chunk_size': self.config.get('chunk_size', 500),
                'chunk_overlap': self.config.get('chunk_overlap', 50),
                'extra_metadata': extraction_result.get('metadata', {})
            }
            
            # Add to vector database
            db_result = self.vector_db.add_document(extracted_text, metadata)
            
            if db_result['success']:
                return (f"✅ Successfully processed '{filename}': "
                        f"{db_result['chunks_added']} chunks added "
                        f"({db_result['total_characters']} characters)")
            else:
                return f"❌ Failed to add '{filename}' to database: {db_result['error']}"
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return f"❌ Error processing '{filename}': {str(e)}"
    
    # --- All other methods from older file (generate_response, _build_context, etc.) ---
    # This includes: generate_response, _build_context, _build_conversation_context,
    # _get_system_prompt, _build_user_prompt, get_database_stats, clear_database,
    # delete_document, get_supported_formats
    
    # You can copy them exactly as in your older file here.

        # Inside ResearchAssistant class
    def get_database_stats(self) -> Dict[str, Any]:
        return self.vector_db.get_database_stats()

    def clear_database(self) -> bool:
        return self.vector_db.clear_database()

    def delete_document(self, document_id: str) -> bool:
        return self.vector_db.delete_document(document_id)

    def get_supported_formats(self) -> List[str]:
        return self.doc_processor.get_supported_formats()

    def generate_response(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate an AI response based on the query and conversation history.
        """
        try:
            # 🔹 Use search_similar instead of non-existent search()
            search_results = self.vector_db.search_similar(query, limit=5)

            # Build context string
            context_texts = [doc["text"] for doc in search_results]
            context = "\n\n".join(context_texts) if context_texts else "No relevant context found."

            # Build the prompt for Groq
            system_prompt = (
                "You are an AI research assistant. Use the following context to answer the question.\n"
                "If the context is not sufficient, say so clearly instead of guessing.\n"
                f"Context:\n{context}"
            )

            user_prompt = f"Question: {query}"

            # Call Groq LLM
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            # 🔹 Groq returns choices with message content
            answer = response.choices[0].message.content.strip()

            # Save to conversation history
            self.conversation_history.append({"query": query, "answer": answer})

            return answer

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"❌ Error generating response: {str(e)}"


