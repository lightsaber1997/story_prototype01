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
    correction_ready = Signal(dict)
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
        ####################################
        ### part 1
        ####################################



        classify_prompt = [
            {
            "role": "system",
            "content": textwrap.dedent("""
                You are an assistant in a children's story app.
                Reply with exactly one JSON object only:
                {"is_story":"true"} if the input is part of a story
                {"is_story":"false"} if it is a question or chat
                Always use double quotes for both key and value. No other text.
            """).strip(),
            },
            {"role": "user", "content": user_text},
        ]


        is_story = False
        try:
            generated = self.engine.generate_reply(classify_prompt)
            print(f"[DEBUG] is_story generated={generated}")
            # Use robust fixer instead of raw json.loads
            result = format_helper.single_key_bool_json_fix(generated, field="is_story")

            if result.get("is_story") == "true":
                is_story = True

        except Exception as e:
            print("is_story response error:", e)


        
        ####################################
        ### part 2
        ####################################
        if is_story:
            # fixed_line 구하기
            print("[AI] is_story: True -> result: correction, story_continue")
            fix_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        Correct the grammar/spelling of the following sentence minimally,
                        but keep the child's voice.
                        Respond with ONLY the corrected sentence, nothing else.
                    """).strip(),
                },
                {"role": "user", "content": user_text},
            ]

            try:
                fixed_generated = self.engine.generate_reply(fix_prompt)
                print(f"[DEBUG] fixed_generated={fixed_generated}")
                fixed_line = fixed_generated

            except Exception as e:
                print("JSON parse error in fix:", e, fixed_generated)
                fixed_line = user_text
            
            self.story.append(fixed_line)

            self.correction_ready.emit({"type": "correction", "text": fixed_line})
         
            

            # 이야기 만들기
            story_context = " ".join(self.story[-100:])
            continue_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        You are writing a children's story.
                        Continue the story in exactly 2 lively sentences.
                        Do not repeat the input, and do not explain your answer.
                        Output only the 2 new sentences as plain text, nothing else.
                    """).strip(),
                },
                {
                    "role": "user",
                    "content": f"Here is the story so far:\n{story_context}\n\nPlease continue.",
                },
            ]

            raw_story = self._stream_text(continue_prompt, "story_continue", 120)
            # ✅ UI는 위에서 emit으로 이미 실시간 스트리밍 출력됨
            # ✅ 내부적으로만 최종 JSON 파싱해서 self.story에 append
            if raw_story:
                # Just treat raw_story as plain text continuation
                lines = [s.strip() for s in raw_story.split("\n") if s.strip()]
                for line in lines:
                    self.story.append(line)

        else:
            # chat 답변
            print("[AI] is_story: False -> result: chat")

            chat_prompt = [
                {
                    "role": "system",
                    "content": textwrap.dedent("""
                        You are a helpful assistant for casual chat.
                    """).strip(),
                },
                {"role": "user", "content": user_text}
            ]
            self._stream_text(chat_prompt, "chat", 120)

    # def _stream_and_collect(self, prompt, kind, max_new_tokens):
    #     accumulated = ""
    #     prev_len = 0
    #     buffer = ""
    #     inside_value = False
    #     after_colon = False

    #     story_accum = ""  # story_continue일 때 전체 누적 버퍼
    #     correction_final = None  # fixed_grammar/correction 최종 값 저장

    #     print(f"[DEBUG] _stream_and_collect start (kind={kind}, max_new_tokens={max_new_tokens})")

    #     for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
    #         accumulated += token
    #         delta = accumulated[prev_len:]
    #         prev_len = len(accumulated)
    #         if not delta:
    #             continue

    #         for ch in delta:
    #             if not inside_value:
    #                 # 콜론 본 직후: 공백은 스킵, 첫 비공백이 따옴표면 value 시작
    #                 if ch == ':':
    #                     after_colon = True
    #                     # 콜론 자체는 파싱 상태에만 쓰고 buffer에는 굳이 쌓지 않음
    #                     continue

    #                 if after_colon:
    #                     if ch.isspace():
    #                         # : 뒤 공백 허용
    #                         continue
    #                     if ch == '"':
    #                         inside_value = True
    #                         after_colon = False
    #                         print(f"[DEBUG] Value start detected at pos={prev_len}")
    #                         buffer = ""  # 현재 value 임시 버퍼
    #                         continue
    #                     after_colon = False
    #             else:
    #                 is_escaped = len(buffer) > 0 and buffer[-1] == '\\'
    #                 if ch == '"' and not is_escaped:
    #                     # ✅ value 종료 시점
    #                     final_val = buffer.strip()
    #                     print(f"[DEBUG] Value end detected (final='{final_val}')")

    #                     if kind == "story_continue":
    #                         if story_accum:
    #                             story_accum += " "
    #                         story_accum += final_val
    #                         # 종료된 시점에서 전체 누적 emit
    #                         self.token_story_continue_Ready.emit(story_accum, "story")

    #                     elif kind == "chat":
    #                         self.token_chat_Ready.emit(final_val, "chat")

    #                     elif kind == "correction":
    #                         correction_final = final_val
    #                         self.token_correction_Ready.emit(final_val, "correction")

    #                     buffer = ""
    #                     inside_value = False
    #                 else:
    #                     buffer += ch
    #                     if kind == "story_continue":
    #                         temp_val = buffer.strip()
    #                         if temp_val:
    #                             temp_emit = (story_accum + " " + temp_val).strip()
    #                             self.token_story_continue_Ready.emit(temp_emit, "story")
    #                     elif kind == "chat":
    #                         text = buffer.strip()
    #                         if text:
    #                             self.token_chat_Ready.emit(text, "chat")
    #                     elif kind == "correction":
    #                         text = buffer.strip()
    #                         if text:
    #                             self.token_correction_Ready.emit(text, "correction")

    #     # 스트림이 끝났는데 value가 닫히지 않았을 때
    #     if inside_value and buffer.strip():
    #         final_val = buffer.strip()
    #         if kind == "story_continue":
    #             if story_accum:
    #                 story_accum += " "
    #             story_accum += final_val
    #             self.token_story_continue_Ready.emit(story_accum, "story")
    #         elif kind == "chat":
    #             self.token_chat_Ready.emit(final_val, "chat")
    #         elif kind == "correction":
    #             correction_final = final_val
    #             self.token_correction_Ready.emit(final_val, "correction")

    #     print(f"[DEBUG] _stream_and_collect done (kind={kind}, total_len={len(accumulated)})")
    #     print(f"[DEBUG] story_accum={story_accum}")

    #     # resultReady로 최종 완성본 전달
    #     if kind == "story_continue" and story_accum.strip():
    #         self.resultReady.emit({"type": "story_answer", "text": story_accum.strip()})
    #     elif kind == "correction" and correction_final:
    #         self.resultReady.emit({"type": "correction_answer", "text": correction_final})
    #     return accumulated

    def _stream_text(self, prompt, kind, max_new_tokens):
        """
        Stream plain text from the engine and emit progressively.
        No JSON parsing, only raw text accumulation.
        """
        accumulated = ""
        print(f"[DEBUG] _stream_text start (kind={kind}, max_new_tokens={max_new_tokens})")

        for token in self.engine.generate_reply_stream(prompt, max_new_tokens=max_new_tokens):
            accumulated += token
            text = accumulated.strip()

            if not text:
                continue

            if kind == "story_continue":
                self.token_story_continue_Ready.emit(text, "story")
            elif kind == "chat":
                self.token_chat_Ready.emit(text, "chat")
            elif kind == "correction":
                self.token_correction_Ready.emit(text, "correction")

        print(f"[DEBUG] _stream_text done (kind={kind}, total_len={len(accumulated)})")

        # Final delivery
        if kind == "story_continue" and accumulated.strip():
            self.resultReady.emit({"type": "story_answer", "text": accumulated.strip()})
        elif kind == "correction" and accumulated.strip():
            self.resultReady.emit({"type": "correction_answer", "text": accumulated.strip()})
        elif kind == "chat" and accumulated.strip():
            self.resultReady.emit({"type": "chat_answer", "text": accumulated.strip()})

        return accumulated


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