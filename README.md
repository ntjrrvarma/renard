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

## 🚦 New safety & CI features
### Agent behavior hardening
- `renard.py` now validates model output before returning:
  - enforces persona rules (no menu options, no "next step", no "please specify")
  - detects and flags uncertain/hallucinatory phrasing
  - avoids unsafe model exceptions with fallback message
- `yggdrasil.py` stays responsible for memory recall and persistence
- `tools.py` handles file log/output utility functions

### Unit tests
- `test_renard.py` added:
  - `test_find_personality_violations`
  - `test_sanitize_reply_removes_violations`
  - `test_check_hallucination_adds_warning`
  - `test_classify_request_fallback_on_failure`
  - `test_think_code_writes_file`

### Local test run
1. `venv\\Scripts\\python.exe -m pip install -r requirements.txt`
2. `venv\\Scripts\\python.exe -m pytest -q`

### GitHub Actions
- `.github/workflows/python-tests.yml` runs on:
  - `push` to `main` / `master`
  - `pull_request` to `main` / `master`
- Steps:
  1. checkout repo
  2. setup Python 3.11
  3. install requirements + pytest
  4. run `pytest -q`

### If PowerShell activation is blocked
- `powershell -ExecutionPolicy Bypass -NoProfile -Command "cd C:\\Users\\nrrah\\Documents\\renard; .\\venv\\Scripts\\Activate.ps1; pip install -r requirements.txt; pytest -q"`
- or use direct interpreter path:
  - `C:\\Users\\nrrah\\Documents\\renard\\venv\\Scripts\\python.exe -m pytest -q`
