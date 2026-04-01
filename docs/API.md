# API Reference: Renkai — Renard

This reference documents the core Python classes and methods used in the Renard project. It is intended for developers who want to extend or integrate with the system.

## 🦊 Renard Class (`renard.py`)

The main agent orchestration class.

### `Renard()`
**Constructor**
Initialize Renard with his soul (persona), connects to Yggdrasil (memory), and wakes the brain (Ollama).

### `think(message: str) -> str`
**Core Response Loop**
The primary entry point for interaction.
- **`message`**: The input string from Mr. R.
- **Returns**: A sanitized, character-aligned response string.
- **Process**: Classify → Recall (Memory) → Generate (LLM) → Sanitize → Remember (Memory) → Log.

### `status() -> dict`
**Agent Health**
Returns a dictionary with the current status, level, tails, and memory count.

---

## 🌳 Yggdrasil Class (`yggdrasil.py`)

The memory engine representing the World Tree of the empire.

### `Yggdrasil(agent_name: str)`
**Constructor**
Initialize the ChromaDB persistent client and connect to the agent's specific collection (branch).

### `remember(user_msg: str, agent_reply: str, context: str = "general")`
**Store Memory**
Plants a new conversation branch into the tree.
- **`user_msg`**: The prompt from Mr. R.
- **`agent_reply`**: Renard's response.
- **`context`**: Optional category (e.g., "code", "plan").

### `recall(query: str, n: int = 4) -> str`
**Search Memory**
Performs a semantic search for memories relevant to the query.
- **`query`**: The string to search for.
- **`n`**: Number of relevant memories to return.
- **Returns**: A formatted string containing the retrieved context.

### `count() -> int`
**Memory Count**
Returns the total number of memories stored for the current agent.

---

## 🛠️ Tools Module (`tools.py`)

A collection of utility functions for system-level operations.

### `write_file(filename: str, content: str) -> str`
Writes generated code to the `output/` directory and returns the absolute path.

### `log_conversation(user_msg: str, renard_reply: str)`
Appends the conversation to a daily log file in the `logs/` directory.

### `get_empire_status() -> dict`
Returns the global state of the Renkai empire (total agents, empire level, etc.).

---

## 🧪 Testing

### `test_renard.py`
The testing suite for the project. Run with `pytest -q` to verify:
- Response sanitization.
- Personality violations detection.
- Memory integration.
- Code extraction logic.
