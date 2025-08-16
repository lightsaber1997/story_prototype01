# ── stdlib
import sys, re, json, textwrap, random, string, collections
from pathlib import Path
from typing import Dict, List

# ── Qt
from PySide6.QtCore import Qt, QThread, QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget,
    QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
)

import format_helper

# ════════════════════════════════════════════════════════════════════
# ChatWorker (runs in background thread)
# ════════════════════════════════════════════════════════════════════
class ChatWorker(QObject):
    """Does all LLM calls off‑thread."""

    resultReady = Signal(dict)  # dict with keys: type, text

    def __init__(self, engine):  # 🡆 no type hint for engine
        super().__init__()
        self.engine = engine
        self.story: List[str] = []  # authoritative, fixed sentences

    @Slot(str)
    def doWork(self, user_text: str):
        # 1) Classification & minimal correction
        classify_prompt = [
            {
                "role": "system",
                "content": textwrap.dedent(
                    """
                    You are an assistant in a children's story‑builder app.
                    Decide whether the user's message is a STORY SENTENCE
                    or a QUESTION/CHAT. If it is a story sentence, correct
                    grammar/spelling minimally but keep the child's voice.
                    Respond with EXACTLY ONE JSON object, on a single line, no code block
                    markers, no extra text. 
                    {"kind":"story", "fixed_line":"..."}  OR
                    {"kind":"chat",  "answer":"..."}
                    """
                ).strip(),
            },
            {"role": "user", "content": user_text},
        ]
        raw_json = self.engine.generate_reply(classify_prompt, max_new_tokens=128)
        print(raw_json)

        try:
            m = re.search(r"\{.*?\}", raw_json, flags=re.S)
            data = json.loads(m.group(0)) if m else {}
        except Exception:
            data = {"kind": "chat", "answer": "I'm sorry, could you rephrase that?"}

        # 2) Handle story path
        if data.get("kind") == "story":
            fixed_line = data["fixed_line"].strip()
            self.story.append(fixed_line)
            self.resultReady.emit({"type": "story_line", "text": fixed_line})

            # 2b) Ask for continuation
            story_context = " ".join(self.story[-100:])  # truncate for safety
            continue_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent(
                        """
                        Continue this children's story in 2 lively sentences. Make sure the reply forms a complete sentence and ends with a period.
                        Respond with EXACTLY ONE JSON object, on a single line, no code block
                        markers, no extra text. 
                        {"first": "first sentence", "second": "second sentence"},
                        """
                    ).strip(),
                },
                {"role": "user", "content": story_context},
            ]
            raw_next_line = self.engine.generate_reply(continue_prompt, max_new_tokens=120).strip()
            print(f"raw_next_line: {raw_next_line}")

            json_checked_output = format_helper.get_first_json(raw_next_line)
            next_line = json_checked_output["first"] + json_checked_output["second"]

            self.story.append(next_line)
            self.resultReady.emit({"type": "ai_suggestion", "text": next_line})

        else:
            answer = data["answer"].strip()
            print(f"answer {answer}")
            self.resultReady.emit({"type": "chat_answer", "text": answer + " What’s your next line?"})


# ════════════════════════════════════════════════════════════════════
# ChatController (thread wrapper)
# ════════════════════════════════════════════════════════════════════
class ChatController(QObject):
    operate = Signal(str)

    def __init__(self, result_callback, engine):  # 🡆 no type hint
        super().__init__()
        self.workerThread = QThread()
        self.worker = ChatWorker(engine)
        self.worker.moveToThread(self.workerThread)

        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        self.workerThread.start()

    def __del__(self):
        self.workerThread.quit()
        self.workerThread.wait()
