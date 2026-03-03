# 🤖 BUYING AND PLANNING AGENTIC AI SYSTEM

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/langgraph-0.0.20-green.svg)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT4--turbo-purple.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A multi-agent AI system for supply chain planning with demand forecasting, size curve optimization, and pricing strategy.

[![Supply Chain Intelligence Platform Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://youtu.be/YOUR_VIDEO_ID)
*Click the image above to watch the complete 7-minute system walkthrough*

---

<!-- ## ✨ Features

| | |
|---|---|
| **🤖 Multi-Agent Architecture** | Specialized agents for different supply chain domains |
| **🧠 Intelligent Routing** | Automatically classifies and routes queries to the right agent |
| **📚 RAG-Enhanced** | Retrieves relevant documentation for grounded responses |
| **💬 Context-Aware** | Maintains conversation history across sessions |
| **📊 Persistent Storage** | SQLite database with thread-safe operations |
| **🔍 Full Observability** | LangSmith integration for tracing and monitoring |
| **🎨 Modern UI** | Gradio-based chat interface with session management | -->

---

## 🏗️ Architecture

User Query → Router → Context Injector → Specialized Agent → Database


### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Router** | GPT-4 + JSON mode | Intent classification (demand, size, price, general) |
| **RAG System** | FAISS + OpenAI embeddings | Document retrieval with similarity search |
| **Database** | SQLite + thread-local | Conversation persistence with session management |
| **Agents** | LangGraph + GPT-4 | Domain experts for specific tasks |
| **UI** | Gradio | Chat interface with session management |
| **Monitoring** | LangSmith | Tracing, token tracking, performance |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11.14
- OpenAI API key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/erYash15/Buying-Planning-Agentic-AI-System.git
cd Buying-Planning-Agentic-AI-System

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
echo "OPENAI_API_KEY=your_key_here" > .env
echo "LANGSMITH_API_KEY=your_key_here" >> .env
echo "LANGCHAIN_PROJECT=adidas-supply-planning" >> .env
echo "LANGCHAIN_TRACING_V2=true" >> .env
echo "LANGSMITH_TRACING=True" >> .env
echo "LANGSMITH_ENDPOINT="https://api.smith.langchain.com/"" >> .env
echo "LANGSMITH_PROJECT="adidas-supply-planning"" >> .env

# 5. Initialize the system
python db.py        # Creates database
python rag.py       # Creates FAISS index with sample docs

# 6. Launch the app
python gradio_ui.py
```

Visit http://127.0.0.1:7860 in your browser.

## 🗂️ Project Structure

BUYING-PLANNING-AGENTIC-AI-SYSTEM/ <BR>
├── agents/<BR>
│   ├── demand_agent.py      # Demand forecasting<BR>
│   ├── price_agent.py       # Price optimization<BR>
│   └── size_curve_agent.py  # Size distribution<BR>
├── data/                     # Database and vector store<BR>
├── config.py                 # Environment configuration<BR>
├── db.py                     # Database manager<BR>
├── rag.py                    # RAG system<BR>
├── router.py                 # Intent classifier<BR>
├── graph.py                  # LangGraph workflow<BR>
├── gradio_ui.py             # Chat interface<BR>
└── requirements.txt         # Dependencies<BR>


### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit changes (git commit -m 'Add amazing feature')
4. Push to branch (git push origin feature/amazing-feature)
5. Open a Pull Request

### 📬 Contact

1. GitHub Issues: Report a bug
2. Email: eryash15@gmail.com

Built with ❤️ as a personal project.
