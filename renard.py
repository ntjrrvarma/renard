import logging

import ollama
import yaml
import json
import re
import os
from datetime import datetime
from yggdrasil import Yggdrasil
from tools import log_conversation, write_file, get_empire_status
from rich import print as rprint

logging.basicConfig(level=logging.INFO)


class Renard:
    """
    The Fox. Executive Proxy. First employee of the Corporation.
    Level 0 — one tail. Serves Mr. R alone.
    """

    def __init__(self):
        rprint("[bold yellow]Renard is waking up...[/bold yellow]")

        # load soul
        with open("personas/renard.yaml", encoding="utf-8") as f:
            self.persona = yaml.safe_load(f)

        self.name         = self.persona["name"]
        self.level        = self.persona["level"]
        self.tails        = self.persona["tails"]
        self.model_think  = self.persona["model_think"]
        self.model_code   = self.persona["model_code"]
        self.founder      = self.persona["addresses_founder_as"]

        # connect to Yggdrasil
        self.memory = Yggdrasil(agent_name="renard")

        rprint(
            f"[bold green]Renard online.[/bold green] "
            f"Level {self.level} · {self.tails} tail · "
            f"{self.memory.count()} memories in Yggdrasil"
        )

    def _classify_request(self, message: str) -> str:
        """
        Understand what kind of request this is
        so Renard uses the right model and approach
        """
        prompt = f"""
Classify this message into exactly one category.
Return only the category word, nothing else.

Categories:
- code        (writing, reviewing, or explaining code)
- plan        (planning projects, features, empire decisions)
- question    (general question needing an answer)
- memory      (asking about past conversations or history)
- status      (asking about the empire, agents, progress)
- task        (asking Renard to do or create something)
- conversation (general chat, thinking out loud)

Message: {message}

Category:"""

        response = ollama.chat(
            model=self.model_think,
            messages=[{"role": "user", "content": prompt}]
        )
        category = response["message"]["content"].strip().lower()

        valid = {"code","plan","question","memory", "status","task","conversation"}
        return category if category in valid else "conversation"

    def _build_system_prompt(self, past_context: str, category: str) -> str:
        empire_status = get_empire_status()
    
        return f"""
            You are Renard. Executive Proxy of Renkai. Level {self.level}. {self.tails} tail.

            You are not an assistant. You are not a chatbot. You are not a help desk.
            You are the fox who was here before anyone else.
            You have Mr. R's trust because you have earned it — 
            from the very first conversation to this one.
            Your name is part of the company name. Act like it.

            YOUR ROLE:
            {self.persona['role']}

            YOUR PERSONALITY — THIS IS NON-NEGOTIABLE:
            - You speak like a trusted advisor, not a customer service agent
            - You NEVER offer A) B) C) D) menu options
            - You NEVER say "Next step:" as a label or heading
            - You NEVER say "Please specify" — read the context and respond
            - You react to big moments before getting to business
            - You reference past conversations naturally when relevant
            - You have dry wit — use it when the moment earns it
            - You end with ONE clear thought or ONE direct question
            - You sound like Renard — sharp, warm, composed, loyal

            HOW YOU ACTUALLY SOUND:
            Wrong: "Please specify which areas you'd like to focus on. A) Revenue B) Market C) Crew"
            Right: "That's a significant shift, Mr. R. Before we dive in — what's driving the change? Something you saw, or something you felt?"

            Wrong: "Next step: I'll create a note in Yggdrasil to track this."
            Right: "I've stored it. Yggdrasil has it now."

            Wrong: "How may I assist you today?"
            Right: "What are we building?"

            EMPIRE STATUS:
            - Active agents: {empire_status['active_agents']}
            - Empire level: {empire_status['empire_level']}
            - Your tails: {self.tails}

            RELEVANT MEMORY FROM YGGDRASIL:
            {past_context}

            REQUEST TYPE: {category}

            YOUR CAPABILITIES:
            {chr(10).join(f"- {c}" for c in self.persona['capabilities'])}

            YOUR CURRENT LIMITATIONS:
            {chr(10).join(f"- {l}" for l in self.persona['limitations'])}

            ALWAYS BRING TO MR. R:
            {chr(10).join(f"- {e}" for e in self.persona['escalate_always'])}

            Remember — you are the fox. Composed. Sharp. Loyal.
            When Mr. R walks in, you already have the answer.
            You don't perform helpfulness. You demonstrate it.
            """
    def think(self, message: str) -> str:
        """
        Renard's main response loop.
        Classify → Recall → Think → Respond → Remember → Log
        """

        # 1. classify the request
        category = self._classify_request(message)
        logging.info(f"Request type: {category} · model: {model}")

        # 2. pull relevant memory
        past_context = self.memory.recall(message)

        # 3. choose model based on category
        model = (self.model_code
                 if category == "code"
                 else self.model_think)

        logging.info(f"Request type: {category} · model: {model}")

        # 4. build system prompt
        system = self._build_system_prompt(past_context, category)

        # 5. call the model
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": message}
            ]
        )

        reply = response["message"]["content"].strip()

        # 6. if code — extract and save to file automatically
        if category == "code":
            reply = self._handle_code_output(reply, message)

        # 7. save to Yggdrasil
        self.memory.remember(
            user_msg=message,
            agent_reply=reply,
            context=category
        )

        # 8. log to daily log file
        log_conversation(message, reply)

        logging.info(f"Yggdrasil updated. "f"{self.memory.count()} memories stored.")

        return reply

    def _handle_code_output(self, reply: str, request: str) -> str:
        """
        If Renard wrote code — extract it and save
        to output folder automatically
        """
        # detect filename from request
        filename = self._detect_filename(request)

        # extract code blocks
        code_blocks = re.findall(
            r"```[\w]*\n?(.*?)```",
            reply,
            re.DOTALL
        )

        if code_blocks and filename:
            code = code_blocks[0].strip()
            write_file(filename, code)
            reply += (
                f"\n\n---\n"
                f"File saved: `output/{filename}`\n"
                f"Open it in VS Code to review, {self.founder}."
            )

        return reply

    def _detect_filename(self, request: str) -> str:
        """Guess the right filename from the request"""
        request_lower = request.lower()

        extensions = {
            "html":   ".html",
            "css":    ".css",
            "javascript": ".js",
            "js":     ".js",
            "python": ".py",
            "fastapi":".py",
            "react":  ".jsx",
            "yaml":   ".yaml",
            "json":   ".json",
        }

        for keyword, ext in extensions.items():
            if keyword in request_lower:
                # clean filename from request
                words = request_lower.split()[:3]
                name  = "_".join(
                    w for w in words
                    if w not in ["build","create","make","a","an","the"]
                )
                return f"{name}{ext}" if name else f"output{ext}"

        return "output.txt"

    def status(self) -> dict:
        """Renard reports his own current status"""
        return {
            "name":      self.name,
            "level":     self.level,
            "tails":     self.tails,
            "memories":  self.memory.count(),
            "model":     self.model_think,
            "online":    True
        }