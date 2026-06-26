# Testing Guide (Other Devices)

This project runs on Google Gemini's free tier (not OpenAI). Follow these steps to set it up on a new machine.

## Prerequisites
- Python 3.9+ (3.11 recommended)
- A free Google AI Studio API key

## 1. Clone and enter the repo
```bash
git clone <repo-url>
cd Buying-Planning-Agentic-AI-System
```

## 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

## 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install "pydantic<2.11"
```
The `pydantic<2.11` pin is required — newer pydantic versions break gradio 4.44.1's API schema introspection (`TypeError: argument of type 'bool' is not iterable`) and the app fails to serve its homepage.

## 4. Get a free Gemini API key
1. Go to https://aistudio.google.com/apikey
2. Click "Create API key" and copy it.

## 5. Create `.env`
```bash
cat > .env <<'EOF'
GOOGLE_API_KEY=your_gemini_key_here
LANGSMITH_API_KEY=your_key_here
LANGCHAIN_PROJECT=adidas-supply-planning
LANGCHAIN_TRACING_V2=true
LANGSMITH_TRACING=True
LANGSMITH_ENDPOINT=https://api.smith.langchain.com/
LANGSMITH_PROJECT=adidas-supply-planning
EOF
```
Replace `your_gemini_key_here` with your real key. The `LANGSMITH_*` values are optional (only needed for tracing) — leave the placeholder if you don't have a LangSmith key.

## 6. Initialize the database and RAG index
```bash
python db.py
python rag.py
```
`rag.py` will create `data/faiss_index` using Gemini's `gemini-embedding-001` model. If you ever see embedding dimension errors, delete `data/faiss_index` and rerun `python rag.py` to rebuild it.

## 7. Launch the app
```bash
python gradio_ui.py
```
Open http://127.0.0.1:7860 in your browser.

## Known limitation: rate limits
Gemini's free tier caps `gemini-2.5-flash` at **5 requests/minute**. If you test multiple queries back-to-back, you may hit a `429 RESOURCE_EXHAUSTED` error — wait ~15 seconds and retry.

## What to test
- Try each sample query button (demand forecast, size curve, price optimization, general).
- Ask a follow-up question (e.g. "What about for running shoes in Europe?") to confirm conversation context carries over.
- Click "New Session" and confirm a fresh session ID/empty chat.
- Click "View Full History" to confirm past conversations are saved (SQLite at `data/adidas_supply.db`).
