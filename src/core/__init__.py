"""
Core modules for the AI Research Assistant.

This package contains the main business logic including document processing,
vector database management, and the research assistant coordinator.
"""

from .document_processor import DocumentProcessor
from .vector_database import VectorDatabase
from .research_assistant import ResearchAssistant

__all__ = ["DocumentProcessor", "VectorDatabase", "ResearchAssistant"]