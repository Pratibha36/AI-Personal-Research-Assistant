"""
AI Research Assistant - Main Entry Point

This module initializes and runs the AI Research Assistant application.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ui.gradio_interface import create_interface
from utils.config import load_config
from core.research_assistant import ResearchAssistant


def main():
    """Main entry point for the application."""
    print("🤖 Starting AI Research Assistant...")
    
    try:
        # Load configuration
        config = load_config()
        print(f"✅ Configuration loaded")
        
        # Initialize the research assistant
        research_assistant = ResearchAssistant()
        print("✅ Research Assistant initialized")
        
        # Create and launch the interface
        app = create_interface(research_assistant)
        print("✅ Gradio interface created")
        
        print(f"""
🚀 AI Research Assistant is starting...

📊 Configuration:
   • Server: {config.get('server_name', '0.0.0.0')}:{config.get('server_port', 7860)}
   • Debug Mode: {config.get('debug', True)}
   • Share: {config.get('share', False)}

💡 Usage:
   1. Upload your documents (PDF, DOCX, TXT)
   2. Process them using the 'Process Documents' button
   3. Start chatting with your documents!

🔗 Open your browser and navigate to the URL shown below:
        """)
        
        # Launch the application
        app.launch(
            server_name=config.get('server_name', '0.0.0.0'),
            server_port=config.get('server_port', 7860),
            share=config.get('share', False),
            debug=config.get('debug', True),
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        print(f"📝 Make sure you have:")
        print(f"   • Set GROQ_API_KEY in your .env file")
        print(f"   • Installed all requirements: pip install -r requirements.txt")
        print(f"   • Python 3.8+ installed")
        sys.exit(1)


if __name__ == "__main__":
    main()