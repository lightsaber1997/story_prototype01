# ── stdlib
import sys, re, json, textwrap, random, string, collections
from pathlib import Path
from typing import Dict, List

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


from main_ui_colorful import Ui_StoryMakerMainWindow
# ── Transformers / Torch
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM



from phi3_mini_engine import Phi3MiniEngine
from chat_engine import *
import format_helper

from stable_engine import StableV15Engine
from image_gen_engine import *



# ex) ai_module.py 파일의 ask_ai 메서드라고 가정 
# from ai_module import ask_ai

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_StoryMakerMainWindow()
        self.ui.setupUi(self)
        
        # 현재 페이지 (임시)
        self.current_page_idx = 0
        self.total_pages = 3
        self.story_pages = ["Once upon a time...", "", ""]  # 각 페이지의 스토리
        
        self.story_pages_list = [] # double list. each list inside include [user input, ai response, user input, ai response]

        self.connect_signals()
        
        # initial state
        self.update_page_display()
        
        # GPT API 활용
        # from chat_gpt_engine import ChatGPTEngine
        # # initialization for llm engine
        # self.llm_engine = ChatGPTEngine()
        
        # phi3_mini 활용
        from phi3_mini_engine import Phi3MiniEngine
        self.llm_engine = Phi3MiniEngine()
        self.story_parts: List[str] = []
        self.chat_controller = ChatController(self._on_chat_reply, self.llm_engine)

        # For image generation
        self.image_gen_engine = StableV15Engine()
        self.image_gen_controller = ImageGenController(
            self._on_image_gen_ready, 
            self.image_gen_engine)

        # 각 페이지별 생성된 이미지 저장
        self.page_images: Dict[int, str] = {}  # {page_index: image_path}


    def connect_signals(self):
        """버튼과 이벤트를 연결"""

        self.ui.btnContinueStory.clicked.connect(self._on_chat_send)
        self.ui.btnSaveStory.clicked.connect(self.save_story)
        
        # 페이지 네비게이션
        self.ui.label_page_prev.mousePressEvent = self.previous_page
        self.ui.label_page_next.mousePressEvent = self.next_page
    
    def _on_image_gen_ready(self, payload: dict):
        if payload["type"] == "image_generated":
            image = payload["image"]
            prompt = payload["prompt"]

            # Optional: Save or display
            page_idx = self.current_page_idx
            save_path = f"images/page_{page_idx + 1}.png"
            StableV15Engine.save_image(image, save_path)
            self.page_images[page_idx] = save_path

            print(f"[Image] Saved to {save_path} from prompt: {prompt}")

            # Optional: show in UI (e.g., QLabel pixmap)
            # self.ui.imageLabel.setPixmap(QPixmap(save_path))

        elif payload["type"] == "error":
            QMessageBox.critical(self, "Image Error", f"Failed to generate image:\n{payload['error']}")


        
        self._display_image_on_label(save_path)


    def _on_chat_send(self) -> None:
        user_input = self.ui.textEdit_childStory.toPlainText().strip()
        
        if not user_input:
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return
            
        item = QListWidgetItem(f"사용자: {user_input}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        # 줄바꿈을 위한 플래그 설정
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        self.ui.chatList.addItem(item)

        print(f"user_input: {user_input}")
        print(type(user_input))
        
        self.ui.textEdit_childStory.clear()

        self.chat_controller.operate.emit(user_input)


    def _on_chat_reply(self, payload: Dict[str, str]) -> None:
        kind = payload["type"]
        text = payload["text"]

        if kind == "story_line":
            item = QListWidgetItem(f"AI (fixed): {text}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
            self.ui.chatList.addItem(item)
            self._append_to_story(text + " ")

        elif kind == "ai_suggestion":
            item = QListWidgetItem(f"AI: {text}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
            self.ui.chatList.addItem(item)
            self._append_to_story(text + " ")

        elif kind == "chat_answer":
            item = QListWidgetItem(f"AI: {text}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
            self.ui.chatList.addItem(item)
            # self.chat_list.addItem()
        
        self.current_page_idx = len(self.story_pages_list) - 1
        self.update_page_display()
        self.update_story_display()
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()

        # print every 2nd message in a page
        segments = self.story_pages_list[self.current_page_idx]
        select_idx = 1
        if segments is not None and (len(segments) == select_idx + 1):
            prompt_for_image = segments[select_idx]
            prompt_for_image = format_helper.first_sentence(prompt_for_image)
            prompt_for_image += " children's picture book"
            print(prompt_for_image)
            self.image_gen_controller.operate.emit(prompt_for_image)

        

    def _display_image_on_label(self, image_path: str) -> None:
        try:
            if Path(image_path).exists():
                pixmap = QPixmap(image_path)

                if not pixmap.isNull():
                    # label 크기에 맞게 이미지 스케일링 (비율 유지)
                    scaled_pixmap = pixmap.scaled(
                        self.ui.label_generatedImage.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    self.ui.label_generatedImage.setPixmap(scaled_pixmap)
                    self.ui.label_generatedImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    print(f"이미지 표시 완료: {image_path}")
                else:
                    print(f"이미지 로드 실패: {image_path}")
                    self._show_placeholder_text()
            else:
                print(f"이미지 파일이 존재하지 않음: {image_path}")
                # 더미 이미지의 경우 기본 배경 이미지나 플레이스홀더 표시
                self._show_placeholder_image()
                
        except Exception as e:
            print(f"이미지 표시 중 오류 발생: {e}")
            self._show_placeholder_text()
    
    def _show_placeholder_text(self) -> None:
        """플레이스홀더 텍스트를 표시합니다."""
        self.ui.label_generatedImage.clear()
        self.ui.label_generatedImage.setText("🎨 Generated image will appear here")
        self.ui.label_generatedImage.setAlignment(Qt.AlignmentFlag.AlignCenter)


    # ------------- Helpers ---------------------------------------------------
    def _append_to_story(self, segment: str) -> None:
        self.story_parts.append(segment)
        self._add_to_story_pages_list(segment)
        print(f"self.story_pages_list: {self.story_pages_list}")
    
    def _add_to_story_pages_list(self, segment: str, num_page_segment: int = 4) -> None:
        """
        Add a text *segment* to self.story_pages_list.

        • self.story_pages_list is a list of “pages” (each page is a list of segments).
        • Each page can hold at most *num_page_segment* segments.
        • When the current (last) page is full, start a new page.
        """

        # If no pages exist yet, create the first one with this segment.
        if not self.story_pages_list:
            self.story_pages_list.append([segment])
            return

        # Work with the last (current) page.
        last_index = len(self.story_pages_list) - 1
        current_page = self.story_pages_list[last_index]

        # ▸ BUG FIX: compare the **length of the page** to the capacity,
        #   not the page itself.  Originally `len(self.story_pages_list[last_index] == num_page_segment)`
        #   evaluated the boolean first, then tried to take len() of True/False.
        if len(current_page) == num_page_segment:
            # Current page is full → start a new page.
            self.story_pages_list.append([segment])
        else:
            # There is room → append to current page.
            current_page.append(segment)

    
    


        
        # ai 에 메세지 보내기
    def continue_story(self):
        """스토리 계속하기 버튼 클릭 시 실행"""
        user_input = self.ui.textEdit_childStory.toPlainText().strip()
        
        if not user_input:
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return
            
        item = QListWidgetItem(f"사용자: {user_input}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        self.ui.chatList.addItem(item)
        
        # AI 응답 (실제로는 AI 모델 호출 예정)
        # 아래 48th line을 주석 해제하고 49th line을 주석처리 하시면 됩니다.
        # ai_response = ask_ai(user_input)
        ai_response = f"AI가 '{user_input}'을 바탕으로 스토리를 계속 만들어갑니다..."
        ai_item = QListWidgetItem(f"AI: {ai_response}")
        ai_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        ai_item.setFlags(ai_item.flags() | Qt.ItemFlag.ItemIsEnabled)
        self.ui.chatList.addItem(ai_item)
        
        self.story_pages[self.current_page - 1] += f" {user_input}"
        self.update_story_display()
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()
        
    def save_story(self):
        """스토리북 저장 버튼 클릭 시 실행"""
        QMessageBox.information(self, "저장 완료", "스토리북이 성공적으로 저장되었습니다!")
        
    def previous_page(self, event):
        """이전 페이지로 이동"""
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.update_page_display()
            self.update_story_display(self.current_page_idx)
            
    def next_page(self, event):
        """다음 페이지로 이동"""
        if self.current_page_idx < self.total_pages - 1:
            self.current_page_idx += 1
            self.update_page_display()
            self.update_story_display(self.current_page_idx)
            
    def update_page_display(self):
        """페이지 표시 업데이트"""
        self.ui.label_page.setText(f"{self.current_page_idx+1}/{self.total_pages}")
    
        if self.current_page_idx == 0:
            self.ui.label_page_prev.setStyleSheet("""
                QLabel {
                    color: #666666;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
            """)
        else:
            self.ui.label_page_prev.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
                QLabel:hover {
                    background: rgba(255, 255, 255, 0.2);
                    color: #ffd54f;
                }
            """)
            
        if self.current_page_idx == (self.total_pages - 1):
            self.ui.label_page_next.setStyleSheet("""
                QLabel {
                    color: #666666;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
            """)
        else:
            self.ui.label_page_next.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
                QLabel:hover {
                    background: rgba(255, 255, 255, 0.2);
                    color: #ffd54f;
                }
            """)
            
    # def update_story_display(self):
    #     """현재 페이지의 스토리 표시 업데이트"""
    #     current_story = self.story_pages[self.current_page - 1]
        
    #     self.ui.chatList_2.clear()
    #     if current_story:
    #         item = QListWidgetItem(current_story)
    #         item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.ui.chatList_2.addItem(item)

    
    def update_story_display(self, page_idx=None):
        """현재 페이지의 스토리 표시 업데이트"""
        # self.story_pages: ["adsfdfdsfa", "dfadfasdfa", "dfadfadf"]
        # self.story_pages_list = [
        #     ["asdfadsfadsf", "Adfadfadf", "afdafadf", "dfadfadf"],
        #     ["asdfadsfadsf", "Adfadfadf", "afdafadf", "dfadfadf"]
        #     ,
        #     ["asdfadsfadsf", "Adfadfadf", "afdafadf", "dfadfadf"],
        #     ["asdfadsfadsf", "Adfadfadf", "afdafadf", "dfadfadf"]
        # ]
        if page_idx is None:

            page_idx = len(self.story_pages_list) - 1
            
        self.ui.chatList_2.clear()

        
        
        if page_idx >= 0 and page_idx < len(self.story_pages_list):
            list_segment = self.story_pages_list[page_idx]
            if len(list_segment) > 0:
                for seg in list_segment:                   # already at most 4
                    item = QListWidgetItem(seg)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # 줄바꿈 추가
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                    self.ui.chatList_2.addItem(item)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
