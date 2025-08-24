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
    token_chat_Ready = Signal(str, str)
    token_story_fixed_line_Ready = Signal(str, str)
    token_story_continue_Ready = Signal(str, str)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.story: List[str] = []
        self.is_image = True

    @staticmethod
    def is_json_complete(s: str) -> bool:
        """중괄호 개수로 JSON 완성 여부 추적"""
        depth = 0
        in_string = False
        escape = False
        for ch in s:
            if ch == '"' and not escape:  # 문자열 안은 무시
                in_string = not in_string
            if in_string:
                escape = (ch == '\\' and not escape)
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:  # 루트 객체가 닫힘
                    return True
        return False

    @Slot(str)
    def doWork(self, user_text: str):
        if self.is_image is True:
            # TODO: 이야기 만들기
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
            story_text = self._stream_and_collect(continue_prompt, "story_continue", 120)
            try:
                obj = format_helper.get_first_json(story_text)
                first = obj.get("first", "").strip()
                second = obj.get("second", "").strip()
                if first:
                    self.story.append(first)
                if second:
                    self.story.append(second)
            except Exception as e:
                print("JSON parse error in continue:", e, story_text)
                self.story.append(story_text.strip())  # fallback
            self.is_image = False
            return


        classify_prompt = [
            {
                "role": "system",
                "content": textwrap.dedent("""
                    You are an assistant in a children's story-builder app.
                    Answer ONLY with {"is_story":"true"} if the user's message is a STORY SENTENCE,
                    or {"is_story":"false"} if it is a QUESTION/CHAT. No extra words.
                """).strip(),
            },
            {"role": "user", "content": user_text},
        ]

        # Streaming으로 true/false 분류
        buffer = ""
        for token in self.engine.generate_reply_stream(classify_prompt, max_new_tokens=8):
            buffer += token
            if self.is_json_complete(buffer):
                obj = format_helper.get_first_json(buffer)
                is_story_val = obj.get("is_story", False)
                is_story = str(is_story_val).lower() == "true"
                break

        if is_story:
            # TODO: fixed_line 구하기
            print("[AI] is story: True")
            fix_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        Correct the grammar/spelling of the following sentence minimally
                        but keep the child's voice.
                        Respond with EXACTLY ONE JSON object:
                        {"fixed_line":"..."}
                    """).strip(),
                },
                {"role": "user", "content": user_text},
            ]
            fixed_raw = self._stream_and_collect(fix_prompt, "fixed_grammar", 120)
            try:
                obj = format_helper.get_first_json(fixed_raw)
                fixed_line = obj.get("fixed_line", user_text)
            except Exception as e:
                print("JSON parse error in fix:", e, fixed_raw)
                fixed_line = user_text

            self.story.append(fixed_line)

            # TODO: 이야기 만들기
            story_context = " ".join(self.story[-100:])
            continue_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        Continue this children's story in 2 lively sentences. 
                        Make sure the reply forms a complete sentence and ends with a period.
                        Respond with EXACTLY ONE JSON object, on a single line, no code block
                        markers, no extra text. 
                        {"first":"first sentence", "second":"second sentence"}
                    """).strip(),
                },
                {"role": "user", "content": story_context},
            ]
            raw_story = self._stream_and_collect(continue_prompt, "story_continue", 120)
            # ✅ UI는 위에서 emit으로 이미 실시간 스트리밍 출력됨
            # ✅ 내부적으로만 최종 JSON 파싱해서 self.story에 append
            if raw_story:
                try:
                    obj = format_helper.get_first_json(raw_story)
                    first = obj.get("first", "")
                    second = obj.get("second", "")
                    if first:
                        self.story.append(first)
                    if second:
                        self.story.append(second)
                except Exception as e:
                    print("JSON parse error in story_continue:", e, raw_story)
                    self.story.append(raw_story)  # fallback

        else:
            # TODO: 일반 답변
            chat_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        You are a helpful assistant for casual chat.
                        Respond with EXACTLY ONE JSON object:
                        {"answer":"..."}
                    """).strip(),
                },
                {"role": "user", "content": user_text}
            ]
            self._stream_and_collect(chat_prompt, "chat", 120)

    def _stream_and_collect(self, prompt, kind, max_new_tokens):
        accumulated = ""
        prev_len = 0
        buffer = ""
        inside_value = False
        after_colon = False

        story_accum = ""  # story_continue일 때 전체 누적 버퍼

        print(f"[DEBUG] _stream_and_collect start (kind={kind}, max_new_tokens={max_new_tokens})")

        for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
            accumulated += token
            delta = accumulated[prev_len:]
            prev_len = len(accumulated)
            if not delta:
                continue

            for ch in delta:
                if not inside_value:
                    # 콜론 본 직후: 공백은 스킵, 첫 비공백이 따옴표면 value 시작
                    if ch == ':':
                        after_colon = True
                        # 콜론 자체는 파싱 상태에만 쓰고 buffer에는 굳이 쌓지 않음
                        continue

                    if after_colon:
                        if ch.isspace():
                            # : 뒤 공백 허용
                            continue
                        if ch == '"':
                            inside_value = True
                            after_colon = False
                            print(f"[DEBUG] Value start detected at pos={prev_len}")
                            buffer = ""  # 현재 value 임시 버퍼
                            continue
                        after_colon = False
                else:
                    is_escaped = len(buffer) > 0 and buffer[-1] == '\\'
                    if ch == '"' and not is_escaped:
                        # ✅ value 종료 시점
                        final_val = buffer.strip()
                        print(f"[DEBUG] Value end detected (final='{final_val}')")

                        if kind == "story_continue":
                            if story_accum:
                                story_accum += " "
                            story_accum += final_val
                            # 종료된 시점에서 전체 누적 emit
                            self.token_story_continue_Ready.emit(story_accum, "story")
                        elif kind == "chat":
                            self.token_chat_Ready.emit(final_val, "chat")
                        elif kind == "fixed_grammar":
                            self.token_story_fixed_line_Ready.emit(final_val, "correction")

                        buffer = ""
                        inside_value = False
                    else:
                        buffer += ch
                        if kind == "story_continue":
                            temp_val = buffer.strip()
                            if temp_val:
                                # emit 시 항상 누적 + 현재 buffer
                                temp_emit = (story_accum + " " + temp_val).strip()
                                print(f"[DEBUG] Emit growing story='{temp_emit}'")
                                self.token_story_continue_Ready.emit(temp_emit, "story")
                        elif kind == "chat":
                            text = buffer.strip()
                            if text:
                                self.token_chat_Ready.emit(text, "chat")
                        elif kind == "fixed_grammar":
                            text = buffer.strip()
                            if text:
                                self.token_story_fixed_line_Ready.emit(text, "correction")

        # 스트림이 끝났는데 value가 닫히지 않았을 때
        if inside_value and buffer.strip():
            final_val = buffer.strip()
            print(f"[DEBUG] Stream ended with unfinished value → '{final_val}' (kind={kind})")
            if kind == "story_continue":
                if story_accum:
                    story_accum += " "
                story_accum += final_val
                self.token_story_continue_Ready.emit(story_accum, "story")
            elif kind == "chat":
                self.token_chat_Ready.emit(final_val, "chat")
            elif kind == "fixed_grammar":
                self.token_story_fixed_line_Ready.emit(final_val, "correction")

        print(f"[DEBUG] _stream_and_collect done (kind={kind}, total_len={len(accumulated)})")
        print(f"[DEBUG] story_accum={story_accum}")
        return accumulated

    # def _stream_and_collect(self, prompt, kind, max_new_tokens):
    #     buffer = ""
    #     for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
    #         buffer += token
    #
    #         if self.is_json_complete(buffer):  # ✅ JSON이 다 닫혔으면
    #             try:
    #                 obj = format_helper.get_first_json(buffer)
    #                 if kind == "fixed_grammar":
    #                     text = obj.get("fixed_line", "")
    #                     self.token_story_fixed_line_Ready.emit(text)
    #                 elif kind == "story_continue":
    #                     first = obj.get("first", "").strip()
    #                     second = obj.get("second", "").strip()
    #                     text = " ".join([s for s in (first, second) if s])
    #                     self.token_story_continue_Ready.emit(text)
    #                 elif kind == "chat":
    #                     text = obj.get("answer", "")
    #                     self.token_chat_Ready.emit(text)
    #
    #                 return text  # ✅ 파싱 성공 → 종료
    #             except Exception as e:
    #                 print(f"JSON parse error in {kind}:", e, buffer)
    #                 # fallback: 그냥 buffer 그대로 표시
    #                 text = buffer.strip()
    #                 if kind == "fixed_grammar":
    #                     self.token_story_fixed_line_Ready.emit(text)
    #                 elif kind == "story_continue":
    #                     self.token_story_continue_Ready.emit(text)
    #                 elif kind == "chat":
    #                     self.token_chat_Ready.emit(text)
    #                 return text
    #
    #     # fallback: 끝까지 가도 JSON 못 찾음
    #     return buffer.strip()

    # def _stream_and_collect(self, prompt, kind, max_new_tokens):
    #     accumulated = ""
    #     prev_len = 0
    #     buffer = ""
    #     inside_value = False
    #
    #     print(f"[DEBUG] _stream_and_collect start (kind={kind}, max_new_tokens={max_new_tokens})")
    #
    #     for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
    #         accumulated += token
    #         delta = accumulated[prev_len:]
    #         prev_len = len(accumulated)
    #
    #         if not delta:
    #             continue
    #
    #         for ch in delta:
    #             if not inside_value:
    #                 # value 시작 탐지 → :"
    #                 if buffer.endswith(':') and ch == '"':
    #                     inside_value = True
    #                     print(f"[DEBUG] Value start detected at pos={prev_len}")
    #                     buffer = ""  # value 누적 버퍼 리셋
    #                 else:
    #                     buffer += ch
    #             else:
    #                 # value 종료 탐지 → "
    #                 if ch == '"':
    #                     print(f"[DEBUG] Value end detected (final='{buffer.strip()}')")
    #                     # 닫히면 emit 중단 (더 이상 안 보냄)
    #                     buffer = ""
    #                     inside_value = False
    #                 else:
    #                     buffer += ch
    #                     # 🔥 자라나는 부분을 그대로 emit
    #                     text = buffer.strip()
    #                     if text:
    #                         print(f"[DEBUG] Emit growing value='{text}' (kind={kind})")
    #                         if kind == "chat":
    #                             self.token_chat_Ready.emit(text, "chat")
    #                         elif kind == "story_continue":
    #                             self.token_story_continue_Ready.emit(text, "story")
    #                         elif kind == "fixed_grammar":
    #                             self.token_story_fixed_line_Ready.emit(text, "correction")
    #
    #     if inside_value and buffer.strip():
    #         text = buffer.strip()
    #         print(f"[DEBUG] Stream ended with unfinished value → '{text}' (kind={kind})")
    #         if kind == "chat":
    #             self.token_chat_Ready.emit(text, "chat")
    #         elif kind == "story_continue":
    #             self.token_story_continue_Ready.emit(text, "story")
    #         elif kind == "fixed_grammar":
    #             self.token_story_fixed_line_Ready.emit(text, "correction")
    #     print(f"[DEBUG] _stream_and_collect done (kind={kind}, total_len={len(accumulated)})")
    #     print(f"[DEBUG] buffer={buffer}")
    #     return accumulated

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
    #                 You are an assistant in a
    #                 children's story-builder app.
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

    def __init__(self, engine, result_callback):
        super().__init__()
        self.workerThread = QThread()
        self.worker = ChatWorker(engine)
        self.worker.moveToThread(self.workerThread)

        # thread lifecycle
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

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