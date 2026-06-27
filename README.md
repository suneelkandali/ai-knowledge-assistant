# 🤖 AI Knowledge & Research Assistant

> **A local, Ollama-powered Streamlit application** that demonstrates five key AI patterns in one unified interface: conversational chat, web search, prompt engineering, RAG (Retrieval-Augmented Generation) over PDFs, and a multi-agent research workflow.

Built entirely with **local models via [Ollama](https://ollama.com/)** — no cloud API keys required. Uses **ChromaDB** for vector storage, **pymupdf** for PDF text extraction, and **Streamlit** for the UI.

> ⚡ **Pure Python project — no LangChain, no LangGraph, no heavy AI frameworks.** Just direct Ollama API calls, raw ChromaDB operations, and standard Python libraries.

---

## ✨ Features

- **💬 AI Chat** — Pure local LLM conversation without web search. Use this for general knowledge, creative tasks, or chat that doesn’t need live information.
- **🌐 Web Search** — Search DuckDuckGo and answer **strictly from search results**. No internal model knowledge is used.
- **🧪 Prompt Lab** — Experiment with 5 prompt templates (Beginner Explanation, Executive Summary, Detailed Analysis, Action Plan, Blog Article)
- **📄 Chat with PDF** — Upload a PDF, extract & chunk its text, index into ChromaDB, then ask questions using RAG
- **👥 Research Team** — A 4-agent sequential workflow (Planner → Researcher → Writer → Reviewer) that produces a final report on any topic, optionally grounded in an uploaded PDF

---

## 📁 Project Structure

```
ai-knowledge-assistant/
│
├── app.py                       # Main Streamlit application (5 tabs)
├── config.py                    # Environment configuration loader
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (model names, paths)
│
├── agents/                      # Multi-agent research workflow
│   ├── __init__.py
│   └── research_team.py         # Planner, Researcher, Writer, Reviewer agents
│
├── services/                    # LLM integration & web search layer
│   ├── __init__.py
│   ├── llm_service.py           # Ollama chat, generate, embed, connection check
│   └── web_search.py            # DuckDuckGo web search (free, no API key)
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── pdf_utils.py             # PDF text extraction & chunking
│
├── rag/                         # RAG / Vector store layer
│   ├── __init__.py
│   └── vector_store.py          # ChromaDB indexing, retrieval, formatting
│
├── prompts/                     # Prompt templates
│   ├── __init__.py
│   └── templates.py             # 5 prompt templates + builder function
│
├── data/                        # Persistent data (auto-created)
│   └── chroma/                  # ChromaDB persistent storage (auto-created)
│
└── README.md                    # ← You are here
```

---

## 🚀 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.10+ — [Download from python.org](https://www.python.org/downloads/)
- **Ollama** (latest) — [Download from ollama.com](https://ollama.com/download/)
- **Pip** — (comes bundled with Python)

### Required Ollama Models

Pull these models **after** installing Ollama:

```bash
# Chat model (default: gemma2:9b)
ollama pull gemma2:9b

# Embedding model (used for RAG vector search)
ollama pull nomic-embed-text
```

> You can change the models in `.env` by updating `OLLAMA_CHAT_MODEL` and `OLLAMA_EMBEDDING_MODEL`.

---

## 🛠️ Setup Instructions

### 1. Clone or navigate to the project

```bash
git clone https://github.com/suneelkandali/ai-knowledge-assistant.git
cd ai-knowledge-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

The `.env` file is already provided. You can adjust it as needed:

```env
OLLAMA_CHAT_MODEL=gemma3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_PATH=data/chroma
RAG_TOP_K=4
```

- **`OLLAMA_CHAT_MODEL`** — Model used for chat, prompts, and agents (default: `gemma2:9b`)
- **`OLLAMA_EMBEDDING_MODEL`** — Model used for generating text embeddings (default: `nomic-embed-text`)
- **`CHROMA_PATH`** — Directory where ChromaDB persists vector data (default: `data/chroma`)
- **`RAG_TOP_K`** — Number of document chunks to retrieve per query (default: `4`)

### 5. Start Ollama

Make sure the Ollama application is running (background service). Verify it:

```bash
ollama list
```

You should see your pulled models listed.

---

## ▶️ Running the Application

### Start the Streamlit app

```bash
streamlit run app.py
```

This opens your browser at `http://localhost:8501` with the AI Knowledge & Research Assistant interface.

### Verify Ollama connection

In the sidebar, click **"Check Ollama connection"**. You should see a green success message.

---

## 🎯 How to Use Each Tab

### Tab 1: 💬 AI Chat

A straightforward conversational interface with the local LLM only.

1. Type your message in the text input and press **Send**
2. The assistant responds using the configured Ollama model
3. The full conversation history is maintained in the session
4. Use the **"Clear chat history"** button in the sidebar to reset

**Example prompts:**
- "Explain retrieval-augmented generation simply."
- "What are the main types of machine learning?"
- "Write a short poem about artificial intelligence."

### Tab 2: 🌐 Web Search

Searches DuckDuckGo and answers **only** from live web results.

1. Type your question in the text input and press **Search and answer**
2. The app searches DuckDuckGo for the latest information
3. The LLM answers strictly from those search results
4. No internal model knowledge is used

**Best for:**
- Latest news and current events
- Real-time information
- Questions about recent developments

**Example questions:**
- "What are today's top tech headlines?"
- "Latest stock market news USA"
- "Current weather in New York"

Experiment with different prompt engineering styles.

1. Select a **template** from the dropdown (Beginner Explanation, Executive Summary, etc.)
2. Enter your **subject or request**
3. Optionally provide **additional context**
4. Click **"Generate response"**

The available templates are:

- **Beginner Explanation** — Best for explaining technical concepts to non-technical audiences
- **Executive Summary** — Best for concise overviews for decision-makers
- **Detailed Analysis** — Best for in-depth examination of a topic
- **Action Plan** — Best for step-by-step implementation plans
- **Blog Article** — Best for writing educational blog content

### Tab 3: 📄 Chat with PDF (RAG)

Upload a PDF and ask questions about its content.

1. **Upload a PDF** using the file uploader
2. Wait for indexing to complete (you'll see a success message with chunk count)
3. Type your question about the PDF content
4. The system retrieves the most relevant chunks from ChromaDB and feeds them to the LLM as context
5. Retrieved sources are shown below the answer

**How it works internally:**
1. PDF text is extracted page by page using `pymupdf`
2. Text is split into overlapping chunks (default: 900 chars, 150 char overlap)
3. Each chunk is embedded using `nomic-embed-text` via Ollama
4. Chunks + embeddings are stored in a ChromaDB collection
5. On each question, the query is embedded and similarity search finds the top-K chunks
6. Retrieved chunks are formatted as context and injected into the LLM prompt

### Tab 4: 👥 Research Team (Multi-Agent)

A sequential 4-agent research and writing workflow.

1. Enter a **research topic** (e.g., "How can organizations introduce AI agents responsibly?")
2. Optionally check **"Use the active PDF as source context"** (if you uploaded one in Tab 3)
3. Click **"Run the four-agent team"**
4. The agents run in sequence:
   - **Planner Agent** — Creates a research plan with objectives, questions, and structure
   - **Researcher Agent** — Gathers information from the PDF context or model knowledge
   - **Writer Agent** — Produces a full professional report draft
   - **Reviewer Agent** — Reviews and revises the draft into the final report
5. Expand each agent's output to inspect intermediate results
6. Download the final report as a Markdown file using the **"Download final report"** button


---

## 📄 File-by-File Explanation

### Root Files

#### `app.py` — Main Application

The entry point for the Streamlit app. It:

- Configures the page (title: "AI Knowledge and Research Assistant", wide layout)
- Initializes 4 session state variables: `chat_messages`, `rag_collection`, `rag_filename`, `research_outputs`
- Builds a sidebar with configuration info (model names), connectivity check, and chat reset
- Creates 4 tabs using `st.tabs()`:
  - **Tab 1 (AI Chat):** Renders chat history, accepts user input via `st.form`, calls `generate_chat_response()` and appends to session
  - **Tab 2 (Prompt Lab):** Template selector dropdown, subject/context text areas, calls `build_prompt()` → `generate_response()`
  - **Tab 3 (Chat with PDF):** File uploader → `extract_pages_from_pdf()` → `chunk_pages()` → `index_chunks()` → stores collection name; then accepts questions → `retrieve_chunks()` → `generate_response()` with context
  - **Tab 4 (Research Team):** Topic input, optional PDF context checkbox, calls `run_research_team()`, displays expandable agent outputs, download button

**Dependencies:** All other modules in the project.

#### `config.py` — Configuration

Loads environment variables from `.env` using `python-dotenv`. Provides:

- `CHAT_MODEL` — Ollama model for conversation (default: `gemma3:4b`)
- `EMBEDDING_MODEL` — Ollama model for embeddings (default: `nomic-embed-text`)
- `CHROMA_PATH` — Pathlib Path for ChromaDB persistence (default: `data/chroma`)
- `RAG_TOP_K` — Number of chunks to retrieve (default: `4`)

Automatically creates the ChromaDB directory if it doesn't exist.

#### `requirements.txt` — Dependencies

```
streamlit
ollama
pymupdf
chromadb
python-dotenv
```

> ⚡ **Zero AI framework dependencies.** No LangChain, LangGraph, or similar — just the Ollama Python SDK, raw ChromaDB, and standard Python libraries.

- **`streamlit`** — Web UI framework
- **`duckduckgo_search`** — Free web search (no API key needed) for live chat answers
- **`ollama`** — Python client for local Ollama server
- **`pymupdf`** — PDF text extraction (MuPDF bindings)
- **`chromadb`** — Vector database for RAG
- **`python-dotenv`** — Load `.env` file into environment

#### `.env` — Environment Variables

```
OLLAMA_CHAT_MODEL=llama3.1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_PATH=data/chroma
RAG_TOP_K=4
```

> **Note:** `.env` is excluded from version control (add to `.gitignore`). It contains only local configuration — no secrets, since everything runs locally.

---

### `agents/` — Multi-Agent Research Workflow

#### `agents/research_team.py` — Research Team Agents

Implements a **sequential multi-agent workflow** with 4 specialized agents:

- **Planner** — Creates a research plan (objectives, questions, structure, risks) — temperature: 0.1 — *"You are the Planner Agent. Decompose topics into logical and useful plans."*
- **Researcher** — Gathers information from PDF context or model knowledge — temperature: 0.2 — *"You are the Researcher Agent. Gather and organize reliable material for the Writer Agent."*
- **Writer** — Produces a professional report (title, summary, findings, examples, recommendations) — temperature: 0.3 — *"You are the Writer Agent. Turn research notes into a clear and useful report."*
- **Reviewer** — Reviews and revises the draft (accuracy, consistency, readability, uncertainty) — temperature: 0.1 — *"You are the Reviewer Agent. Produce the strongest and most responsible final version."*

**Key function:** `run_research_team(topic, source_context)` runs all 4 agents sequentially.

---

### `services/` — LLM Integration Layer

#### `services/llm_service.py` — LLM Service

The sole interface to Ollama. Provides 4 functions:

- **`generate_response(prompt, system_prompt, temperature)`** — Single-turn prompt → response using `CHAT_MODEL`
- **`generate_chat_response(history, system_prompt)`** — Multi-turn chat with history using `CHAT_MODEL`
- **`embed_texts(texts)`** — Batch text → embedding vectors using `EMBEDDING_MODEL`
- **`check_ollama_connection()`** — Verify Ollama is reachable by calling `ollama.list()`

All functions include error handling that raises `RuntimeError` with actionable messages.

#### `services/web_search.py` — Web Search Service

Free web search using DuckDuckGo — no API key required. Used by the AI Chat tab when web search is enabled.

**`search_web(query, max_results=5, region="wt-wt")`** — Performs a web search and returns a list of dicts with `title`, `url`, and `snippet`.

**`format_search_results(results)`** — Converts raw search results into a numbered text block for LLM context.

**`build_web_search_context(query, max_results=5)`** — Convenience function that searches and returns a ready-to-use context string with a source label. Returns an empty string on failure.

---

### `utils/` — Utility Functions

#### `utils/pdf_utils.py` — PDF Utilities

**`extract_pages_from_pdf(pdf_bytes)`** — Opens PDF from bytes using `pymupdf`, extracts text page by page. Returns `list[PageText]`.

**`chunk_pages(pages, chunk_size=900, overlap=150)`** — Splits page text into overlapping chunks. Returns `list[TextChunk]`.

---

### `rag/` — Vector Store & RAG Layer

#### `rag/vector_store.py` — Vector Store

**`_client()`** — Creates ChromaDB persistent client at `CHROMA_PATH`.

**`make_collection_name(filename, file_bytes)`** — Creates unique collection name via SHA-256 hash.

**`index_chunks(collection_name, chunks, source_name, batch_size=32)`** — Deletes old collection, creates new one, batches chunks + embeddings, adds to ChromaDB.

**`retrieve_chunks(collection_name, question, top_k=4)`** — Embeds query, searches ChromaDB, returns ranked chunks with metadata.

**`format_retrieved_context(retrieved)`** — Formats chunks as `[Source N: file, page X]` blocks for LLM consumption.

---

### `prompts/` — Prompt Templates

#### `prompts/templates.py` — Prompt Templates

5 curated templates: Beginner Explanation, Executive Summary, Detailed Analysis, Action Plan, Blog Article.

**`build_prompt(template_name, subject, context="")`** — Returns `(system_prompt, user_prompt)` tuple.

---

## Testing

### Manual Testing (Streamlit UI)

```bash
streamlit run app.py
# Tab 1: Type a message and verify response
# Tab 2: Try each template with a subject
# Tab 3: Upload a PDF, ask a question
# Tab 4: Enter topic, run the 4-agent team
```

### Script-level Testing

```bash
# Test Ollama connection
python -c "from services.llm_service import check_ollama_connection; print(check_ollama_connection())"

# Test config
python -c "from config import CHAT_MODEL; print(f'Model: {CHAT_MODEL}')"
```

---

## Troubleshooting

- **`Ollama could not be reached`** — Ollama not running → Start Ollama or run `ollama serve`
- **`model not found`** — Model not pulled → Run `ollama pull gemma2:9b`
- **`No selectable text`** — PDF is scanned → Use OCR or a text-based PDF
- **Slow responses** — Large model → Switch to smaller model in `.env`

---

## Architecture Diagram

```
Streamlit UI (app.py) ─── 4 Tabs
    │
    ├── Tab 1: AI Chat ──────── llm_service.py (ollama.chat)
    ├── Tab 2: Prompt Lab ───── templates.py + llm_service.py
    ├── Tab 3: Chat w/ PDF ──── pdf_utils.py → vector_store.py → llm_service.py
    └── Tab 4: Research Team ── research_team.py (4 agents) → llm_service.py
```

---

## Learning Path

1. **AI Chat** — Basic LLM interaction
2. **Web Search** - MCP Integration
2. **Prompt Lab** — Prompt engineering
3. **Chat with PDF** — RAG fundamentals
4. **Research Team** — Multi-agent workflows

---

## License

Educational purposes only. All rights reserved.