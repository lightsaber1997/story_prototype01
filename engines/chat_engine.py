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
    """Does all LLM calls off-thread."""

    resultReady = Signal(dict)  # dict with keys: type, text
    tokenReady = Signal(str)    # streaming token

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.story: List[str] = []
        self.use_streaming = hasattr(engine, 'generate_reply_stream')

    @Slot(str)
    def doWork(self, user_text: str):
        # 1) Classification
        classify_prompt = [
            {
                "role": "system",
                "content": textwrap.dedent(
                    """
                    You are an assistant in a children's story-builder app.
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
        raw_json = self._nl2space(self.engine.generate_reply(classify_prompt, max_new_tokens=128))
        print(raw_json)

        data = self._safe_json(raw_json, fallback={"kind": "chat", "answer": "I'm sorry, could you rephrase that?"})

        # 2) Handle story path
        if data.get("kind") == "story":
            fixed_line = self._nl2space(data.get("fixed_line", ""))
            self.story.append(fixed_line)
            self.resultReady.emit({"type": "story_line", "text": fixed_line})

            story_context = " ".join(self.story[-100:])
            continue_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent(
                        """
                        Continue this children's story in 2 lively sentences. Make sure the reply forms a complete sentence and ends with a period.
                        Respond with EXACTLY ONE JSON object, on a single line, no code block
                        markers, no extra text. 
                        """
                    ).strip(),
                },
                {"role": "user", "content": story_context},
            ]
            if self.use_streaming:
                self._stream_and_collect(
                    continue_prompt,
                    start_event="ai_suggestion_start",
                    complete_event="ai_suggestion_complete",
                    max_new_tokens=120
                )
            else:
                self._non_stream_and_emit(
                    continue_prompt,
                    event_type="ai_suggestion",
                    max_new_tokens=120
                )
        else:
            if self.use_streaming:
                self._handle_streaming_chat(data, user_text)
            else:
                answer = self._nl2space(data.get("answer", ""))
                self.resultReady.emit({"type": "chat_answer", "text": answer + " What's your next line?"})

    def _stream_and_collect(self, prompt, start_event, complete_event, max_new_tokens):
        """공통 스트리밍 수집"""
        self.resultReady.emit({"type": start_event, "text": ""})
        accumulated = ""
        for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
            accumulated += token
            self.tokenReady.emit(token)

        clean = self._nl2space(accumulated)
        if complete_event.startswith("ai_suggestion"):
            self.story.append(clean)
        self.resultReady.emit({"type": complete_event, "text": clean})

    def _non_stream_and_emit(self, prompt, event_type, max_new_tokens):
        """공통 비스트리밍 처리"""
        raw = self._nl2space(self.engine.generate_reply(prompt, max_new_tokens=max_new_tokens))
        if event_type.startswith("ai_suggestion"):
            self.story.append(raw)
        self.resultReady.emit({"type": event_type, "text": raw})

    def _handle_streaming_chat(self, data, user_text):
        """Handle chat response with streaming"""
        if data.get("answer"):
            answer = self._nl2space(data.get("answer", ""))
            self.resultReady.emit({"type": "chat_answer", "text": answer + " What's your next line?"})
            return

        chat_prompt = [
            {"role": "system", "content": "You are a helpful assistant in a children's story app. Answer briefly and ask what's their next story line."},
            {"role": "user", "content": user_text},
        ]
        self._stream_and_collect(
            chat_prompt,
            start_event="chat_answer_start",
            complete_event="chat_answer_complete",
            max_new_tokens=80,
        )
    @staticmethod
    def _safe_json(raw: str, fallback: dict) -> dict:
        """안전한 JSON 추출"""
        try:
            m = re.search(r"\{.*?\}", raw, flags=re.S)
            return json.loads(m.group(0)) if m else fallback
        except Exception:
            return fallback

    @staticmethod
    def _nl2space(s: str) -> str:
        if not isinstance(s, str):
            return s
        s = re.sub(r'[\r\n]+', ' ', s)
        s = s.replace("\\n", " ")
        return re.sub(r' {2,}', ' ', s).strip()

# ════════════════════════════════════════════════════════════════════
# ChatController (thread wrapper)
# ════════════════════════════════════════════════════════════════════
class ChatController(QObject):
    operate = Signal(str)

    def __init__(self, result_callback, engine, token_callback=None):
        super().__init__()
        self.workerThread = QThread()
        self.worker = ChatWorker(engine)
        self.worker.moveToThread(self.workerThread)

        # thread lifecycle
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        if token_callback:
            self.worker.tokenReady.connect(token_callback)

        self.workerThread.start()
        self._closed = False  # 안전 종료 플래그

    def close(self, timeout: int = 3000):
        """Gracefully stop the worker thread"""
        if self._closed:
            return
        self._closed = True

        if self.workerThread.isRunning():
            self.workerThread.quit()
            finished = self.workerThread.wait(timeout)
            if not finished:
                print("[ChatController] Warning: worker thread did not quit cleanly")

    def __del__(self):
        self.close()
