import os
import tempfile

import pytest

import renard as renard_module
from renard import Renard
import tools


def test_find_personality_violations():
    r = Renard()
    text = "Next step: do this. Please specify details. a) option" 
    violations = r._find_personality_violations(text)
    assert "contains prohibited phrase 'next step'" in violations
    assert "contains prohibited phrase 'please specify'" in violations
    assert "contains menu-style options" in violations


def test_sanitize_reply_removes_violations():
    r = Renard()
    reply = "Next step: do it.\n1) First option\nWhat do you want?"
    cleaned = r._sanitize_reply(reply)
    assert "Next step" not in cleaned
    assert "1)" not in cleaned
    assert "What do you want" in cleaned


def test_check_hallucination_adds_warning():
    r = Renard()
    reply = "I think this is likely correct. It should work."
    checked = r._check_hallucination(reply)
    assert "may be uncertain" in checked.lower()
    assert "I think this is likely correct" in checked


def test_classify_request_fallback_on_failure(monkeypatch):
    r = Renard()

    def bad_chat(*args, **kwargs):
        raise RuntimeError("model not available")

    monkeypatch.setattr(renard_module.ollama, "chat", bad_chat)

    category = r._classify_request("What is your name?")
    assert category == "conversation"


def test_think_code_writes_file(tmp_path, monkeypatch):
    r = Renard()

    # Ensure output directory is isolated to tmp_path
    monkeypatch.setattr(tools, "OUTPUT_DIR", str(tmp_path))

    # Mock memory engine behavior to avoid persistence side effects
    r.memory.recall = lambda _msg: "No memories stored yet"
    r.memory.remember = lambda **kwargs: None

    def fake_chat(model, messages):
        text = messages[0]["content"]
        if "Classify this message" in text:
            return {"message": {"content": "code"}}
        return {"message": {"content": "```python\nprint('hello')\n```"}}

    monkeypatch.setattr(renard_module.ollama, "chat", fake_chat)

    reply = r.think("Build a Python script to print hello")

    assert "Project created at" in reply

    project_dir_name = r._sanitize_project_name("Build a Python script to print hello")
    project_path = os.path.join(str(tmp_path), project_dir_name)

    assert os.path.isdir(project_path)

    saved_files = os.listdir(project_path)
    assert len(saved_files) == 1
    assert saved_files[0] == 'main.py'

