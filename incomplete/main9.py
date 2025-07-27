# story_app_phi3.py
"""Interactive Story Builder with Phi‑3‑Mini (Transformers).

Two panes:
• Chat pane – shows the raw child input, AI corrections, AI suggestions, and Q&A.
• Story pane – shows the canonical, grammar‑corrected story so far.

Flow
────
1. AI greets and asks for the first line.
2. Child types a message.
3. Worker asks Phi‑3 to:
     – decide if the message is a story sentence or a chat/question,
     – if story, minimally fix grammar/spelling.
4. • If story: fixed line is appended to Story pane and AI proposes the next
     sentence, also added to both panes.
   • If chat: AI answers in the Chat pane only.

Everything (classification, correction, continuation) uses the same Phi‑3 model.
"""

from __future__ import annotations

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

# ── Transformers / Torch
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# JSON
import json
import warnings
from json import JSONDecoder, JSONDecodeError
from typing import Any

# ════════════════════════════════════════════════════════════════════
# Model setup
# ════════════════════════════════════════════════════════════════════
MODEL_NAME = "microsoft/Phi-3-mini-128k-instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto" if torch.cuda.is_available() else None,
)
model.eval()

if torch.cuda.is_available():
    print(f"✅ CUDA device: {torch.cuda.get_device_name(torch.cuda.current_device())}")
else:
    print("ℹ️  CUDA not available; using CPU (or MPS).")
print(f"ℹ️  First parameter device: {next(model.parameters()).device}")

EOS_ID: int = tokenizer.eos_token_id or tokenizer.convert_tokens_to_ids("<|end|>")


# ════════════════════════════════════════════════════════════════════
# String Format helper
# ════════════════════════════════════════════════════════════════════
def get_first_json(s: str) -> Any:
    """
    Scan *s* left‑to‑right and return the first full JSON object.

    If a later opening brace is never matched with a closing brace
    (i.e. an unfinished JSON fragment), emit a RuntimeWarning.

    Raises
    ------
    ValueError
        If no valid JSON object is found.
    """
    decoder = JSONDecoder()
    idx = 0

    while True:
        try:
            # Find the next candidate '{'
            start = s.index('{', idx)
        except ValueError:
            raise ValueError("No JSON object found in the supplied string.") from None

        try:
            obj, end = decoder.raw_decode(s, start)
            # ---- Found the first complete JSON object ----
            # Check the remainder for unmatched opening brace(s)
            tail = s[end:]
            if tail.count('{') > tail.count('}'):
                warnings.warn(
                    "Trailing text looks like an incomplete JSON object.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            return obj
        except JSONDecodeError:
            # Not a valid object starting here; move one character forward
            idx = start + 1

# ════════════════════════════════════════════════════════════════════
# LLM helper
# ════════════════════════════════════════════════════════════════════
def build_prompt(messages: List[Dict[str, str]]) -> str:
    """Apply chat template if available; otherwise build manually."""
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    parts = [f"<|{m['role']}|>\n{m['content']}<|end|>" for m in messages]
    parts.append("<|assistant|>\n")
    return "\n".join(parts)


@torch.inference_mode()
def generate_reply(messages: List[Dict[str, str]], *, max_new_tokens: int = 128) -> str:
    prompt = build_prompt(messages)
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(model.device) for k, v in enc.items()}

    out_ids = model.generate(
        **enc,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        eos_token_id=EOS_ID,
        pad_token_id=tokenizer.pad_token_id or EOS_ID,
    )

    gen = out_ids[0][enc["input_ids"].shape[1] :]
    reply = tokenizer.decode(gen, skip_special_tokens=True)

    # clean stray template tokens
    for tag in ("<|assistant|>", "<|end|>"):
        if tag in reply:
            reply = reply.split(tag)[0]
    return reply.strip()


def rand_id(k: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


# ════════════════════════════════════════════════════════════════════
# ChatWorker (runs in background thread)
# ════════════════════════════════════════════════════════════════════
class ChatWorker(QObject):
    """Does all LLM calls off‑thread."""

    resultReady = Signal(dict)  # dict with keys: type, text

    def __init__(self) -> None:
        super().__init__()
        self.story: List[str] = []  # authoritative, fixed sentences

    @Slot(str)
    def doWork(self, user_text: str) -> None:
        """Classify the user turn, correct if needed, continue story if applicable."""
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
        raw_json = generate_reply(classify_prompt, max_new_tokens=128)
        print(raw_json)

        try:
            m = re.search(r"\{.*?\}", raw_json, flags=re.S)
            data = json.loads(m.group(0)) if m else {}
        except Exception:
            data = {
                "kind": "chat",
                "answer": "I'm sorry, could you rephrase that?",
            }

        # 2) Handle story path
        if data.get("kind") == "story":
            fixed_line: str = data["fixed_line"].strip()
            self.story.append(fixed_line)
            self.resultReady.emit({"type": "story_line", "text": fixed_line})

            # 2b) Ask for continuation
            story_context = " ".join(self.story[-100:])  # truncate for safety
            continue_prompt = [
                {
                    "role": "system",
                    "content":    textwrap.dedent(
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
            raw_next_line = generate_reply(continue_prompt, max_new_tokens=120).strip()
            
            print(f"raw_next_line: {raw_next_line}")

            json_checked_output = get_first_json(raw_next_line)
            next_line = ""
            next_line += json_checked_output["first"]
            next_line += json_checked_output["second"]

            self.story.append(next_line)
            self.resultReady.emit({"type": "ai_suggestion", "text": next_line})
        else:
            # Chat path
            answer = data["answer"].strip()
            print(f"answer {answer}")
            # self.resultReady.emit({"type": "chat_answer", "text": answer})
            followup_prompt = " What’s your next line?"
            self.resultReady.emit({"type": "chat_answer", "text": answer + followup_prompt})


# ════════════════════════════════════════════════════════════════════
# ChatController (thread wrapper)
# ════════════════════════════════════════════════════════════════════
class ChatController(QObject):
    operate = Signal(str)

    def __init__(self, result_callback: callable) -> None:
        super().__init__()
        self.workerThread = QThread()
        self.worker = ChatWorker()
        self.worker.moveToThread(self.workerThread)

        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        self.workerThread.start()

    def __del__(self):
        self.workerThread.quit()
        self.workerThread.wait()


# ════════════════════════════════════════════════════════════════════
# Main Window (GUI)
# ════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Story Builder – Phi‑3")
        self.resize(1000, 640)

        self.story_parts: List[str] = []
        self.controller = ChatController(self._on_ai_reply)

        # Layout ----------------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(splitter)

        # Left pane – Chat
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.addWidget(QLabel("Chat"))
        self.chat_list = QListWidget()
        left_lay.addWidget(self.chat_list, 1)

        input_row = QHBoxLayout()
        self.input_line = QLineEdit()
        self.send_btn = QPushButton("Send")
        input_row.addWidget(self.input_line, 1)
        input_row.addWidget(self.send_btn)
        left_lay.addLayout(input_row)

        # Right pane – Story
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.addWidget(QLabel("Story"))
        self.story_view = QTextEdit()
        self.story_view.setReadOnly(True)
        right_lay.addWidget(self.story_view, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 2)

        # Signals --------------------------------------------------------------
        self.send_btn.clicked.connect(self._on_send)
        self.input_line.returnPressed.connect(self._on_send)

        # Greeting after window shows
        QTimer.singleShot(
            0,
            lambda: self.chat_list.addItem(
                "AI: Let's start our story! Type your first line ⤵︎"
            ),
        )

    # ------------- Slots -----------------------------------------------------
    def _on_send(self) -> None:
        raw = self.input_line.text().strip()
        if not raw:
            return
        self.input_line.clear()

        self.chat_list.addItem(f"Child: {raw}")
        self.controller.operate.emit(raw)

    def _on_ai_reply(self, payload: Dict[str, str]) -> None:
        kind = payload["type"]
        text = payload["text"]

        if kind == "story_line":
            self.chat_list.addItem(f"AI (fixed): {text}")
            self._append_to_story(text + " ")

        elif kind == "ai_suggestion":
            self.chat_list.addItem(f"AI: {text}")
            self._append_to_story(text + " ")

        elif kind == "chat_answer":
            self.chat_list.addItem(f"AI: {text}")

    # ------------- Helpers ---------------------------------------------------
    def _append_to_story(self, segment: str) -> None:
        self.story_parts.append(segment)
        self.story_view.setPlainText("".join(self.story_parts))

        print(self.story_parts)


# ════════════════════════════════════════════════════════════════════
# Entrypoint
# ════════════════════════════════════════════════════════════════════

def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    if not torch.cuda.is_available():
        print("⚠️  Running on CPU – inference will be slow.", file=sys.stderr)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
