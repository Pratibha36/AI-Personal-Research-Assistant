# 🤖 AI Personal Research Assistant

An intelligent document analysis tool that allows you to chat with your documents using AI. Upload PDFs, Word documents, or text files and get intelligent answers about their content with long-term memory using vector databases.

## ✨ Features

- 📄 **Multi-format Support**: PDF, DOCX, TXT files
- 🧠 **Long-term Memory**: Persistent storage using Qdrant vector database
- 💬 **Conversational Interface**: ChatGPT-like experience with Gradio
- 🔍 **Semantic Search**: Advanced document retrieval using sentence transformers
- 🎯 **Context Awareness**: Maintains conversation history and context
- ⚡ **Fast AI Responses**: Powered by Groq's high-speed inference

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- VS Code (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-research-assistant
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

## 🔧 VS Code Setup

This project includes VS Code configuration for optimal development experience:

- **Extensions**: Recommended extensions are automatically suggested
- **Debugging**: Pre-configured launch configurations
- **Settings**: Python interpreter and formatting settings
- **IntelliSense**: Full autocomplete and type checking

### Recommended VS Code Extensions

- Python
- Pylance
- Python Docstring Generator
- GitLens
- Error Lens

## 📖 Usage

1. **Start the application**: Run `python src/main.py`
2. **Upload documents**: Use the file upload interface to add your documents
3. **Process documents**: Click "Process Documents" to add them to the knowledge base
4. **Start chatting**: Ask questions about your documents in natural language

### Example Queries

- "What are the main findings in this research paper?"
- "Summarize the key points from all uploaded documents"
- "Compare the methodologies used in document A vs document B"
- "What does the contract say about payment terms?"

## 🛠️ Development

### Project Structure

- `src/core/`: Core business logic
- `src/ui/`: User interface components
- `src/utils/`: Utility functions and configuration
- `data/`: Data storage (ignored by git)

### Running Tests

```bash
python -m pytest tests/
```

### Code Formatting

```bash
pip install black
black src/
```

## 🔑 API Keys

You'll need a Groq API key:

1. Sign up at [Groq Console](https://console.groq.com/)
2. Create an API key
3. Add it to your `.env` file

## 📊 Supported Models

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **LLM**: Groq's `llama3-8b-8192` (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
