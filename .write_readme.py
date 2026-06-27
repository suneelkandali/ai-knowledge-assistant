from pathlib import Path

text = """# 🤖 AI Knowledge & Research Assistant\n\n
git clone <repo-url>\ncd ai-knowledge-assistant\n\n## 🛠 Setup\n\npython -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\n\nEdit `.env` with your Ollama models.\n\nollama pull gemma3:4b\nollama pull nomic-embed-text\n\n## ▶ Run\n\nstreamlit run app.py\n\n## 🧪 Test\n\n1. Streamlit UI: Tab 1 AI Chat, Tab 2 Web Search (MCP), Tab 3 Prompt Lab, Tab 4 Chat with PDF, Tab 5 Research Team (Agent Workflow).\n2. Script check: python -c \"from services.llm_service import check_ollama_connection; print(check_ollama_connection())\"\n"""

Path("/Users/suneelkandali/Documents/Suneel/Training/AI/AgenticAI/POCs/ai-knowledge-assistant/README.md").write_text(text)
print("ok")
