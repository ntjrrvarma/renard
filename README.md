# Renkai — Renard (Executive Proxy · Level 0)

The first agent of Renkai. Built with Ollama, ChromaDB, and Streamlit.

## Setup

1. Install Ollama and pull models:
   ollama pull llama3.1:8b
   ollama pull qwen2.5-coder:7b

2. Create virtual environment:
   python -m venv venv
   venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run Renard:
   streamlit run app.py

## Stack
- Brain: llama3.1:8b
- Builder: qwen2.5-coder:7b
- Memory: ChromaDB (Yggdrasil)
- UI: Streamlit
- Runtime: Ollama (fully local)

## The Crew
- Renard — Executive Proxy · Level 0 · 1 tail
- More agents coming as the empire grows

*Renkai — the fox who pioneers new worlds.*