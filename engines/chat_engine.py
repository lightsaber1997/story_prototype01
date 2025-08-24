# ── stdlib
import sys, re, json, textwrap
from typing import List

# ── Qt
from PySide6.QtCore import QThread, QObject, Signal, Slot
import format_helper

# ════════════════════════════════════════════════════════════════════
# ChatWorker (runs in background thread)
# ════════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════
# ChatWorker (runs in background thread)
# ════════════════════════════════════════════════════════════════════
class ChatWorker(QObject):
    """Does all LLM calls off-thread."""

    resultReady = Signal(dict)

    # Streaming
    token_story_fixed_line_Ready = Signal(str)
    token_chat_Ready = Signal(str)
    token_story_continue_Ready = Signal(str)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.story: List[str] = []

    def _classify_with_stream(self, classify_prompt, max_new_tokens=8) -> bool:
        """Streaming으로 true/false 분류"""
        buffer = ""
        for token in self.engine.generate_reply_stream(classify_prompt, max_new_tokens=max_new_tokens):
            buffer += token.strip().lower()
            # 조기 판정
            if "true" in buffer:
                return True
            if "false" in buffer:
                return False
        # fallback
        return False

    @Slot(str)
    def doWork(self, user_text: str):
        classify_prompt = [
            {
                "role": "system",
                "content": textwrap.dedent("""
                    You are an assistant in a children's story-builder app.
                    Answer ONLY with "true" if the user's message is a STORY SENTENCE,
                    or "false" if it is a QUESTION/CHAT. No extra words.
                """).strip(),
            },
            {"role": "user", "content": user_text},
        ]

        is_story = self._classify_with_stream(classify_prompt)

        if is_story:
            fixed_line = self._nl2space(user_text)  # 여기선 바로 user_text 쓰거나 최소 보정
            self.story.append(fixed_line)
            self.resultReady.emit({"type": "story_line_complete", "text": fixed_line})

            story_context = " ".join(self.story[-100:])
            continue_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        Continue this children's story in 2 lively sentences. 
                        Make sure the reply forms a complete sentence and ends with a period.
                        Respond with EXACTLY ONE JSON object, on a single line, no code block
                        markers, no extra text. 
                        {"first": "first sentence", "second": "second sentence"}
                    """).strip(),
                },
                {"role": "user", "content": story_context},
            ]
            self._stream_and_collect(continue_prompt, "story_continue", 120)

        else:
            chat_prompt = [{"role": "user", "content": user_text}]
            self._stream_and_collect(chat_prompt, "chat", 120)

    def _stream_and_collect(self, prompt, kind, max_new_tokens):
        accumulated = ""
        for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
            accumulated += token
            if kind == "story_fixed":
                self.token_story_fixed_line_Ready.emit(token)
            elif kind == "story_continue":
                self.token_story_continue_Ready.emit(token)
            elif kind == "chat":
                self.token_chat_Ready.emit(token)

        clean = self._nl2space(accumulated)
        # dict 형태로 emit해야 MainApp에서 payload["type"], payload["text"]로 안전하게 받음
        self.resultReady.emit({"type": kind, "text": clean})

    #
    # @Slot(str)
    # def doWork(self, user_input: str):
    #     self._stream_buffer = ""
    #     try:
    #         data = json.loads(user_input)
    #         is_ocr = data.get("source") == "ocr"
    #         user_text = data.get("text")
    #     except Exception:
    #         is_ocr = False
    #         user_text = user_input
    #
    #     if is_ocr:
    #         self.story.append(user_text)
    #         self.doStoryContinue()
    #     else:
    #         self.doClassify(user_text)
    #
    # # 1) Classification → streaming
    # def doClassify(self, user_text: str):
    #     classify_prompt = [
    #         {
    #             "role": "system",
    #             "content": textwrap.dedent("""
    #                 You are an assistant in a children's story-builder app.
    #                 Decide whether the user's message is a STORY SENTENCE
    #                 or a QUESTION/CHAT. If it is a story sentence, correct
    #                 grammar/spelling minimally but keep the child's voice.
    #                 Respond with EXACTLY ONE JSON object:
    #                 {"is_story": true, "fixed_line":"..."} OR
    #                 {"is_story": false, "answer":"..."}
    #             """).strip(),
    #         },
    #         {"role": "user", "content": user_text},
    #     ]
    #
    #     buffer = ""
    #     for token in self.engine.generate_reply_stream(classify_prompt, max_new_tokens=128):
    #         buffer += token
    #         self.token_chat_Ready.emit(token)  # 분류 과정도 바로바로 전달
    #
    #     try:
    #         parsed = format_helper.get_first_json(buffer)
    #         if str(parsed.get("is_story", "")).lower() == "true":
    #             fixed_line = parsed.get("fixed_line", user_text)
    #             self.story.append(fixed_line)
    #             # grammar fix + story 이어쓰기
    #             self.doFixGrammar(fixed_line)
    #             self.doStoryContinue()
    #         else:
    #             answer = parsed.get("answer", "")
    #             if answer:
    #                 self.token_chat_Ready.emit(answer)
    #     except Exception as e:
    #         print("JSON parse error in classify:", e, buffer)
    #
    # # 2) Fix Grammar → streaming
    # def doFixGrammar(self, text: str) -> str:
    #     fix_prompt = [
    #         {
    #             "role": "system",
    #             "content": textwrap.dedent("""
    #                 Correct the grammar/spelling of the following sentence minimally
    #                 but keep the child's voice.
    #                 Respond with EXACTLY ONE JSON object:
    #                 {"fixed_line":"..."}
    #             """).strip(),
    #         },
    #         {"role": "user", "content": text},
    #     ]
    #
    #     buffer = ""
    #     for token in self.engine.generate_reply_stream(fix_prompt, max_new_tokens=128):
    #         buffer += token
    #         self.token_story_fixed_line_Ready.emit(token)
    #
    #     try:
    #         parsed = format_helper.get_first_json(buffer)
    #         return parsed.get("fixed_line", text)
    #     except Exception as e:
    #         print("JSON parse error in fix:", e, buffer)
    #         return text
    #
    # # 3) Chat Answer → streaming
    # def doChatAnswer(self, text: str):
    #     chat_prompt = [
    #         {
    #             "role": "system",
    #             "content": textwrap.dedent("""
    #                 You are a helpful assistant for casual chat.
    #                 Respond with EXACTLY ONE JSON object:
    #                 {"answer":"..."}
    #             """).strip(),
    #         },
    #         {"role": "user", "content": text},
    #     ]
    #
    #     buffer = ""
    #     for token in self.engine.generate_reply_stream(chat_prompt, max_new_tokens=128):
    #         buffer += token
    #         self.token_chat_Ready.emit(token)
    #
    #     try:
    #         parsed = format_helper.get_first_json(buffer)
    #         answer = parsed.get("answer", "")
    #         if answer:
    #             self.token_chat_Ready.emit(answer)
    #     except Exception as e:
    #         print("JSON parse error in chat:", e, buffer)
    #
    # # 4) Story Continue → streaming
    # def doStoryContinue(self):
    #     story_context = " ".join(self.story[-100:])
    #     continue_prompt = [
    #         {
    #             "role": "system",
    #             "content": textwrap.dedent("""
    #                 Continue this children's story in 2 lively sentences.
    #                 Respond with EXACTLY ONE JSON object:
    #                 {"first": "...", "second": "..."}
    #             """).strip(),
    #         },
    #         {"role": "user", "content": story_context},
    #     ]
    #
    #     buffer = ""
    #     for token in self.engine.generate_reply_stream(continue_prompt, max_new_tokens=120):
    #         buffer += token
    #         self.token_story_continue_Ready.emit(token)
    #
    #     try:
    #         parsed = format_helper.get_first_json(buffer)
    #         first = parsed.get("first", "").strip()
    #         second = parsed.get("second", "").strip()
    #         if first:
    #             self.story.append(first)
    #         if second:
    #             self.story.append(second)
    #     except Exception as e:
    #         print("JSON parse error in story_continue:", e, buffer)

    @staticmethod
    def _nl2space(s: str) -> str:
        if not isinstance(s, str):
            return s
        s = re.sub(r'[\r\n]+', ' ', s)
        s = s.replace("\\n", " ")
        s = re.sub(r' {2,}', ' ', s)
        return s.strip()

# ════════════════════════════════════════════════════════════════════
# ChatController (thread wrapper)
# ════════════════════════════════════════════════════════════════════
class ChatController(QObject):
    operate = Signal(str)

    def __init__(self, engine, result_callback, token_callback=None):
        super().__init__()
        self.workerThread = QThread()
        self.worker = ChatWorker(engine)
        self.worker.moveToThread(self.workerThread)

        # thread lifecycle
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        if token_callback:
            self.worker.token_story_fixed_line_Ready.connect(token_callback["story_fixed"])
            self.worker.token_chat_Ready.connect(token_callback["chat"])
            self.worker.token_story_continue_Ready.connect(token_callback["story_continue"])
        self.workerThread.start()
        self._closed = False  # 안전 종료 플래그

    def __del__(self):
        """Gracefully stop the worker thread"""
        if self._closed:
            return
        self._closed = True

        if self.workerThread.isRunning():
            self.workerThread.quit()
            finished = self.workerThread.wait(3000) # timeout
            if not finished:
                print("[ChatController] Warning: worker thread did not quit cleanly")