import logging

import ollama
import yaml
import json
import re
import os
from datetime import datetime
from yggdrasil import Yggdrasil
import tools
from tools import log_conversation, write_file, get_empire_status, create_project_files
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

            ACCURACY RULES:
            - Do not hallucinate facts, figures, or claims.
            - If you are not certain, say: "I don't have that data right now" and propose a verification path.
            - Never invent unfamiliar client names or commitments.
            - Preface inference explicitly.

            Remember — you are the fox. Composed. Sharp. Loyal.
            When Mr. R walks in, you already have the answer.
            You don't perform helpfulness. You demonstrate it.
            """

    def _find_personality_violations(self, text: str) -> list:
        text_lower = text.lower()

        violations = []
        if "next step" in text_lower:
            violations.append("contains prohibited phrase 'next step'")
        if "please specify" in text_lower:
            violations.append("contains prohibited phrase 'please specify'")
        if re.search(r"\b(?:[abcd]|[0-9]+)\)(?:\s|$)", text_lower):
            violations.append("contains menu-style options")
        if "how may i assist you" in text_lower:
            violations.append("contains chatbot-style sentence")
        return violations

    def _sanitize_reply(self, reply: str) -> str:
        lines = []
        for line in reply.splitlines():
            if re.search(r"\b(?:[abcd]|[0-9]+)\)(?:\s|$)", line.strip().lower()):
                continue
            if "next step" in line.strip().lower():
                continue
            if "please specify" in line.strip().lower():
                continue
            if "how may i assist you" in line.strip().lower():
                continue
            lines.append(line)

        cleaned = "\n".join(lines).strip()
        if cleaned:
            return cleaned
        return "I am aligning with Renard persona rules and avoiding menu options or clarification requests."

    def _assert_personality_alignment(self, reply: str) -> str:
        violations = self._find_personality_violations(reply)
        if not violations:
            return reply

        logging.warning("Renard output violated persona rules: %s", "; ".join(violations))
        return self._sanitize_reply(reply)

    def _check_hallucination(self, reply: str) -> str:
        uncertain_patterns = ["i think", "i believe", "maybe", "probably", "could be", "not sure", "i guess"]
        lower = reply.lower()

        if any(p in lower for p in uncertain_patterns):
            warning = (
                "[Renard note: this may be uncertain or inferred; verify against a concrete source.]\n\n"
            )
            return warning + reply

        return reply

    def _classify_request(self, message: str) -> str:
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

        try:
            response = ollama.chat(
                model=self.model_think,
                messages=[{"role": "user", "content": prompt}]
            )
            category = response["message"]["content"].strip().lower()
        except Exception as e:
            logging.error("Classification model failed: %s", e, exc_info=True)
            return "conversation"

        valid = {"code", "plan", "question", "memory", "status", "task", "conversation"}
        return category if category in valid else "conversation"

    def think(self, message: str) -> str:
        """
        Renard's main response loop.
        Classify → Recall → Think → Respond → Remember → Log
        """

        # 1. classify the request
        category = self._classify_request(message)
        model = (self.model_code if category == "code" else self.model_think)
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
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": message}
                ]
            )
            reply = response["message"]["content"].strip()
        except Exception as e:
            logging.error("Ollama request failed: %s", e, exc_info=True)
            reply = (
                "Renard encountered a temporary model error. "
                "I am still here, Mr. R. Please retry in a moment."
            )

        # 6. enforce persona output rules
        reply = self._assert_personality_alignment(reply)

        # 6.5. guard against hallucination language
        reply = self._check_hallucination(reply)

        # 7. if code — extract and save to file automatically
        if category == "code":
            reply = self._handle_code_output(reply, message)

        # 8. save to Yggdrasil
        self.memory.remember(
            user_msg=message,
            agent_reply=reply,
            context=category
        )

        # 8. log to daily log file
        log_conversation(message, reply)

        logging.info(f"Yggdrasil updated. "f"{self.memory.count()} memories stored.")

        return reply

    def _sanitize_project_name(self, request: str) -> str:
        request_lower = request.lower()

        # support explicit folder and project name syntax
        explicit = re.search(r"(?:folder|project)\s*[:=]\s*([\w\- ]+)", request_lower)
        if explicit:
            folder_name = explicit.group(1).strip()
            folder_name = re.sub(r"[^a-z0-9-]+", "-", folder_name.lower())
            folder_name = re.sub(r"-+", "-", folder_name).strip("-")
            if folder_name:
                return folder_name[:80]

        words = re.findall(r"[a-zA-Z0-9_-]+", request_lower)
        filtered = [w for w in words if w not in {
            "build", "create", "make", "a", "an", "the",
            "site", "project", "page", "script", "code", "html",
            "css", "js", "python", "react", "game", "fox"
        }]
        base = "_".join(filtered[:3])
        if not base:
            base = f"renard_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return base[:80]

    def _resolve_target_directory(self, request: str) -> str:
        folder_name = self._sanitize_project_name(request)
        target_dir = os.path.join(tools.OUTPUT_DIR, folder_name)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def _detect_filename(self, request: str, language: str = "py") -> str:
        ext_map = {
            "html": ".html",
            "css": ".css",
            "javascript": ".js",
            "js": ".js",
            "python": ".py",
            "fastapi": ".py",
            "react": ".jsx",
            "yaml": ".yaml",
            "json": ".json",
        }

        for keyword, ext in ext_map.items():
            if keyword in request.lower():
                return f"main{ext}"

        return f"main{ext_map.get(language, '.txt')}"

    def _extract_filename_from_code_block(self, code: str, lang: str, index: int) -> (str, str):
        lines = code.strip().splitlines()
        filename = None

        if lines:
            first = lines[0].strip()
            match = re.match(r"<!--\s*file:\s*([\w\-./]+)\s*-->", first, re.IGNORECASE)
            if not match:
                match = re.match(r"<!--\s*([\w\-./]+)\s*-->", first)
            if not match:
                match = re.match(r"#\s*file:\s*([\w\-./]+)", first, re.IGNORECASE)

            if match:
                filename = match.group(1)
                code = "\n".join(lines[1:]).strip()

        if not filename:
            ext_map = {
                "html": ".html",
                "css": ".css",
                "javascript": ".js",
                "js": ".js",
                "python": ".py",
                "fastapi": ".py",
                "react": ".jsx",
                "yaml": ".yaml",
                "json": ".json",
                "md": ".md"
            }
            ext = ext_map.get(lang.lower().strip(), ".txt")
            filename = f"file_{index}{ext}"

        return filename, code

    def _build_mermaid_diagram(self, project_name: str, files: list) -> str:
        lines = ["```mermaid", "graph TD", f"root[\"{project_name}\"]"]
        for f in files:
            node = re.sub(r"[^a-zA-Z0-9_]+", "_", f)
            lines.append(f"    {node}[\"{f}\"]")
            lines.append(f"    root --> {node}")
        lines.append("```")
        return "\n".join(lines)

    def _handle_code_output(self, reply: str, request: str) -> str:
        """
        If Renard wrote code — extract it and save
        to output folder automatically
        """
        project_name = self._sanitize_project_name(request)
        project_dir = self._resolve_target_directory(request)

        # extract language tagged code blocks: (lang, code)
        code_blocks = re.findall(
            r"```([\w+-]*)\n(.*?)```",
            reply,
            re.DOTALL
        )

        # fallback to generic block if no fenced code
        if not code_blocks:
            stripped = re.sub(r"```+", "", reply).strip()
            if stripped:
                target = os.path.join(project_dir, self._detect_filename(request, "py"))
                with open(target, "w", encoding="utf-8") as f:
                    f.write(stripped)
                reply += (f"\n\n---\nFiles saved under `output/{project_name}`.\n"
                          f"Open it in VS Code to review, {self.founder}.")
                reply += "\n\n" + self._build_mermaid_diagram(project_name, [os.path.basename(target)])
            return reply

        files = {}
        for idx, (lang, code) in enumerate(code_blocks, start=1):
            filename, sanitized_code = self._extract_filename_from_code_block(code, lang, idx)
            if len(code_blocks) == 1 and filename.startswith("file_"):
                filename = self._detect_filename(request, lang or "py")
            files[filename] = sanitized_code

        created_files = []
        for rel_path, content in files.items():
            target = os.path.join(project_dir, rel_path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(os.path.relpath(target, project_dir))

        file_list = "\n".join(f"- {p}" for p in created_files)
        reply += (
            f"\n\n---\nProject created at `output/{project_name}` with files:\n{file_list}\n"
            f"Open it in VS Code to review, {self.founder}."
        )
        reply += "\n\n" + self._build_mermaid_diagram(project_name, created_files)

        return reply

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