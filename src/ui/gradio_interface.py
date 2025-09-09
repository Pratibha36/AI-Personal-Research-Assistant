"""
Gradio interface module for the AI Research Assistant.

This module creates the web-based user interface using Gradio.
"""

import gradio as gr
from typing import List, Tuple, Any
import logging

from core.research_assistant import ResearchAssistant

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_interface(research_assistant: ResearchAssistant) -> gr.Blocks:
    """
    Create and configure the Gradio interface.
    
    Args:
        research_assistant (ResearchAssistant): The research assistant instance
        
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    
    def upload_and_process_files(files: List[Any]) -> str:
        """Handle file upload and processing."""
        try:
            if not files:
                return "📝 No files selected. Please upload some documents first."
            
            logger.info(f"Processing {len(files)} uploaded files")
            result = research_assistant.process_documents(files)
            return result
            
        except Exception as e:
            error_msg = f"Error processing files: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"
    
    def chat_with_documents(message: str, history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Handle chat interactions with documents."""
        try:
            if not message.strip():
                return history + [("", "Please enter a question to get started.")]
            
            logger.info(f"Processing chat query: '{message[:50]}...'")
            
            # Generate response
            response = research_assistant.generate_response(message, history)
            
            # Add to history
            history.append((message, response))
            return history
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            logger.error(f"Chat error: {e}")
            history.append((message, error_response))
            return history
    
    def clear_chat_history() -> List[Tuple[str, str]]:
        """Clear the chat history."""
        logger.info("Chat history cleared")
        return []
    
    def get_database_info() -> str:
        """Get information about the current database state."""
        try:
            stats = research_assistant.get_database_stats()
            
            if stats['total_documents'] == 0:
                return "📊 **Database Status**: Empty\n\nNo documents have been uploaded yet. Upload some documents to get started!"
            
            info = f"""📊 **Database Statistics**
            
**Total Documents**: {stats['total_documents']}
**Total Chunks**: {stats['total_chunks']}
**Total Vectors**: {stats['total_vectors']}

**Uploaded Documents**:"""
            
            for i, doc in enumerate(stats['documents'], 1):
                info += f"\n{i}. **{doc['name']}** ({doc['file_type']}) - {doc['chunks']} chunks"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return f"❌ Error retrieving database information: {str(e)}"
    
    def clear_database() -> str:
        """Clear all documents from the database."""
        try:
            success = research_assistant.clear_database()
            if success:
                logger.info("Database cleared successfully")
                return "✅ **Database Cleared**\n\nAll documents have been removed from the knowledge base."
            else:
                return "❌ **Error**: Failed to clear the database."
        except Exception as e:
            error_msg = f"Error clearing database: {str(e)}"
            logger.error(error_msg)
            return f"❌ **Error**: {error_msg}"
    
    # Create the Gradio interface
    with gr.Blocks(
        title="AI Research Assistant",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate"
        ),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .chat-container {
            height: 500px !important;
        }
        .upload-area {
            min-height: 100px !important;
        }
        """
    ) as interface:
        
        # Header
        gr.Markdown(
            """
            # 🤖 AI Personal Research Assistant
            
            **Transform your documents into an intelligent knowledge base!** Upload PDFs, Word documents, or text files and have natural conversations about their content.
            
            ---
            """,
            elem_classes=["header-markdown"]
        )
        
        # Main content area
        with gr.Row():
            # Left column - Document management
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("## 📁 Document Management")
                
                # File upload section
                with gr.Group():
                    gr.Markdown("### Upload Documents")
                    file_upload = gr.File(
                        label="Select Files",
                        file_count="multiple",
                        file_types=[".pdf", ".docx", ".txt"],
                        elem_classes=["upload-area"]
                    )
                    
                    with gr.Row():
                        upload_btn = gr.Button(
                            "📤 Process Documents", 
                            variant="primary",
                            size="lg"
                        )
                        
                    upload_status = gr.Textbox(
                        label="Processing Status",
                        lines=6,
                        max_lines=10,
                        interactive=False,
                        show_copy_button=True
                    )
                
                # Database management section
                with gr.Group():
                    gr.Markdown("### Database Management")
                    
                    with gr.Row():
                        info_btn = gr.Button("📊 View Database Info", size="sm")
                        clear_btn = gr.Button("🗑️ Clear Database", size="sm", variant="secondary")
                    
                    db_info = gr.Textbox(
                        label="Database Information",
                        lines=8,
                        max_lines=15,
                        interactive=False,
                        show_copy_button=True
                    )
                
                # Instructions
                gr.Markdown(
                    """
                    ### 💡 How to Use
                    
                    1. **Upload**: Select your documents using the file picker above
                    2. **Process**: Click "Process Documents" to add them to the knowledge base
                    3. **Chat**: Ask questions about your documents in the chat interface
                    4. **Explore**: Use the database info to see what's been uploaded
                    
                    **Supported Formats**: PDF, DOCX, TXT files (up to 50MB each)
                    """,
                    elem_classes=["instructions"]
                )
            
            # Right column - Chat interface
            with gr.Column(scale=2, min_width=600):
                gr.Markdown("## 💬 Chat with Your Documents")
                
                # Chat interface
                # chatbot = gr.Chatbot(
                #     label="Research Assistant",
                #     height=500,
                #     show_label=False,
                #     placeholder="Your conversations will appear here...",
                #     elem_classes=["chat-container"],
                #     bubble_full_width=False,
                #     show_copy_button=True
                # )
                chatbot = gr.Chatbot(
                    label="Research Assistant",
                    height=500,
                    show_label=False,
                    elem_classes=["chat-container"],
                    bubble_full_width=False,
                    show_copy_button=True
                )

                # Chat input
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Ask a question about your documents...",
                        placeholder="e.g., What are the main findings? Can you summarize the key points?",
                        lines=2,
                        max_lines=5,
                        scale=4,
                        show_label=False
                    )
                    
                    send_btn = gr.Button("📤 Send", variant="primary", scale=1)
                
                # Chat controls
                with gr.Row():
                    clear_chat_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
                    
                    gr.Markdown(
                        "*The assistant maintains context throughout your conversation and can reference previous exchanges.*",
                        elem_classes=["chat-help"]
                    )
                
                # Example questions
                with gr.Accordion("💡 Example Questions", open=False):
                    gr.Markdown(
                        """
                        **General Analysis:**
                        - "What are the main themes in these documents?"
                        - "Can you provide a summary of the key findings?"
                        - "What are the most important conclusions?"
                        
                        **Comparative Analysis:**
                        - "How do the approaches in document A compare to document B?"
                        - "What are the similarities and differences between these papers?"
                        
                        **Specific Information:**
                        - "What does the contract say about payment terms?"
                        - "What methodology was used in the research?"
                        - "Can you extract all the statistics mentioned?"
                        
                        **Research Questions:**
                        - "What are the limitations mentioned in this study?"
                        - "What future research directions are suggested?"
                        - "What are the practical implications of these findings?"
                        """,
                        elem_classes=["examples"]
                    )
        
        # Footer
        gr.Markdown(
            """
            ---
            
            <div style="text-align: center; color: #666; font-size: 14px;">
                🔒 <strong>Privacy Note:</strong> Your documents are processed locally and stored in memory during this session.<br>
                🤖 <strong>Powered by:</strong> Groq AI • Qdrant Vector DB • Sentence Transformers
            </div>
            """,
            elem_classes=["footer"]
        )
        
        # Event handlers
        
        # File upload and processing
        upload_btn.click(
            fn=upload_and_process_files,
            inputs=[file_upload],
            outputs=[upload_status],
            show_progress=True
        )
        
        # Chat interactions
        send_btn.click(
            fn=chat_with_documents,
            inputs=[chat_input, chatbot],
            outputs=[chatbot],
            show_progress=True
        ).then(
            lambda: "",  # Clear input after sending
            outputs=[chat_input]
        )
        
        chat_input.submit(
            fn=chat_with_documents,
            inputs=[chat_input, chatbot],
            outputs=[chatbot],
            show_progress=True
        ).then(
            lambda: "",  # Clear input after sending
            outputs=[chat_input]
        )
        
        # Clear chat
        clear_chat_btn.click(
            fn=clear_chat_history,
            outputs=[chatbot]
        )
        
        # Database management
        info_btn.click(
            fn=get_database_info,
            outputs=[db_info],
            show_progress=True
        )
        
        clear_btn.click(
            fn=clear_database,
            outputs=[db_info],
            show_progress=True
        )
        
        # Auto-load database info on startup
        interface.load(
            fn=get_database_info,
            outputs=[db_info]
        )
    
    return interface


def create_demo_interface() -> gr.Blocks:
    """
    Create a demo interface with sample content for testing.
    
    Returns:
        gr.Blocks: Demo Gradio interface
    """
    with gr.Blocks(title="AI Research Assistant - Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🤖 AI Research Assistant - Demo Mode
            
            This is a demonstration version. To use the full version:
            1. Set up your Groq API key in the `.env` file
            2. Run the application with `python src/main.py`
            
            ---
            """
        )
        
        gr.Markdown(
            """
            ## Features Overview
            
            - **📄 Multi-format Support**: Upload PDF, DOCX, and TXT files
            - **🧠 Vector Database**: Powered by Qdrant for semantic search
            - **💬 Conversational AI**: ChatGPT-like interface with Groq
            - **🔍 Context Awareness**: Maintains conversation history
            - **⚡ Fast Processing**: Optimized for quick responses
            
            ## How It Works
            
            1. **Document Processing**: Your files are converted to text and split into chunks
            2. **Vector Embeddings**: Each chunk is converted to a vector using sentence transformers
            3. **Semantic Search**: When you ask questions, relevant chunks are retrieved
            4. **AI Response**: Groq's LLM generates responses based on retrieved context
            5. **Memory**: All interactions and documents persist in the vector database
            """
        )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Sample Questions You Could Ask:")
                gr.Markdown(
                    """
                    - "What are the main findings in this research paper?"
                    - "Can you summarize the methodology used?"
                    - "What are the key recommendations?"
                    - "Compare the approaches in documents A and B"
                    - "What does the contract say about payment terms?"
                    """
                )
            
            with gr.Column():
                gr.Markdown("### Supported File Types:")
                gr.File(
                    label="Upload Demo Files",
                    file_count="multiple",
                    file_types=[".pdf", ".docx", ".txt"],
                    interactive=False
                )
                gr.Markdown("*File upload disabled in demo mode*")
        
        gr.Markdown(
            """
            ---
            
            **Ready to get started?** Set up your environment and run the full version!
            """
        )
    
    return demo