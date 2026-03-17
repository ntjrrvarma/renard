import os
import json
from datetime import datetime
from rich import print as rprint


LOG_DIR    = "./logs"
OUTPUT_DIR = "./output"


def write_file(filename: str, content: str) -> str:
    """Write any file Renard creates into the output folder"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    rprint(f"[green]Renard created:[/green] {filepath}")
    return filepath


def log_conversation(user_msg: str, renard_reply: str):
    """Log every conversation to a daily log file"""
    os.makedirs(LOG_DIR, exist_ok=True)
    today     = datetime.now().strftime("%Y-%m-%d")
    log_file  = os.path.join(LOG_DIR, f"renard_log_{today}.txt")
    timestamp = datetime.now().strftime("%H:%M:%S")

    entry = (
        f"\n[{timestamp}]\n"
        f"Mr. R: {user_msg}\n"
        f"Renard: {renard_reply}\n"
        f"{'─' * 60}"
    )

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


def list_output_files() -> list:
    """List everything Renard has created"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = os.listdir(OUTPUT_DIR)
    return files if files else []


def get_empire_status() -> dict:
    """Current state of the empire — grows as agents are added"""
    return {
        "active_agents":   ["Renard (Level 0)"],
        "total_agents":    1,
        "empire_level":    "Founding",
        "tails":           1,
        "divisions":       0,
        "clients":         0,
        "status":          "Empire initialising. The fox is at his desk."
    }