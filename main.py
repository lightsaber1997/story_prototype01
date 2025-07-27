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

# ex) ai_module.py 파일의 ask_ai 메서드라고 가정 
# from ai_module import ask_ai

# 이미지 생성 AI 모듈 (추후 추가될 파일)
# image_generation_ai.py 파일의 ImageGenerationAI 모듈(클래스)라고 가정
# from image_generation_ai import ImageGenerationAI

# 이미지 생성 AI 모듈 예시
# class ImageGenerationAI:
#    def generate_image(self, page_segments: List[str]) -> str:
        # input: page_segments는 4개 문장의 리스트
        # process: AI가 자체적으로 프롬프트 생성 및 이미지 생성
        # output: 생성된 이미지 파일 경로 반환
        # pass
# 4개 문장이 완성될 때마다 자동으로 이미지 생성 요청됨

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_StoryMakerMainWindow()
        self.ui.setupUi(self)
        
        # 현재 페이지 (동적으로 관리)
        self.current_page_idx = 0
        self.story_pages = ["Once upon a time...", "", ""]  # 각 페이지의 스토리 (레거시)
        
        self.story_pages_list = [] # double list. each list inside include [user input, ai response, user input, ai response]

        self.connect_signals()
        
        # initial state
        self.update_page_display()
        self._show_placeholder_text()
        
        # 버튼 연결 해야 할 부분
        # initialization for llm engine
        self.llm_engline = Phi3MiniEngine()
        self.story_parts: List[str] = []
        self.chat_controller = ChatController(self._on_chat_reply, self.llm_engline)
        
        # 이미지 생성 AI 엔진 초기화 (추후 추가될 부분)
        # self.image_ai = ImageGenerationAI()
        
        # 각 페이지별 생성된 이미지 저장
        self.page_images: Dict[int, str] = {}  # {page_index: image_path}

    def closeEvent(self, event):
        """애플리케이션 종료 시 스레드 정리"""
        if hasattr(self, 'chat_controller'):
            self.chat_controller.workerThread.quit()
            self.chat_controller.workerThread.wait()
        event.accept()


    def connect_signals(self):
        """버튼과 이벤트를 연결"""

        self.ui.btnContinueStory.clicked.connect(self._on_chat_send)
        self.ui.btnSaveStory.clicked.connect(self.save_story)
        
        # 페이지 네비게이션
        self.ui.label_page_prev.mousePressEvent = self.previous_page
        self.ui.label_page_next.mousePressEvent = self.next_page

    def _on_chat_send(self) -> None:
        user_input = self.ui.textEdit_childStory.toPlainText().strip()
        
        if not user_input:
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return
            
        item = QListWidgetItem(f"사용자: {user_input}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        # 줄바꿈 추가
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        self.ui.chatList.addItem(item)

        print(f"user_input: {user_input}")
        print(type(user_input))

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
        self._update_current_page_image()
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()
    


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

        if len(current_page) == num_page_segment:
            # Current page is full → request image generation for completed page
            self._request_image_generation(last_index, current_page)
            # Start a new page
            self.story_pages_list.append([segment])
        else:
            current_page.append(segment)
            
            # Check if current page is now complete (4 segments)
            if len(current_page) == num_page_segment:
                self._request_image_generation(last_index, current_page)

    def _request_image_generation(self, page_index: int, page_segments: List[str]) -> None:
        """
        페이지가 4개 문장으로 완성되었을 때 이미지 생성을 요청합니다.
        
        Args:
            page_index: 페이지 인덱스
            page_segments: 해당 페이지의 4개 문장 리스트
        """
        print(f"debugging: [이미지 생성 요청] 페이지 {page_index + 1}")
        print(f"debugging: 문장들: {page_segments}")
        
        self._call_image_generation_ai(page_index, page_segments)
    
    def _call_image_generation_ai(self, page_index: int, page_segments: List[str]) -> None:
        """
        이미지 생성 AI를 호출
        
        Args:
            page_index: 페이지 인덱스
            page_segments: 해당 페이지의 4개 문장 리스트
        """
        print(f"debugging: [이미지 생성 AI 호출] 페이지 {page_index + 1}")
        print(f"debuhging: 전달할 문장들: {page_segments}")
        
        # 실제 이미지 생성 AI 모듈과 연결
        # 아래 주석 풀고 임시 더미 이미지 부분(209~211)을 주석처리 하면 됩니다. print문은 디버깅용이라 지워도 무방
        # 예시:
        # try:
        #     image_path = self.image_ai.generate_image(page_segments)
        #     self.page_images[page_index] = image_path
        #     print(f"이미지 생성 완료: {image_path}")
        #     
        #     # UI 업데이트 (이미지 표시)
        #     self._update_page_image_display(page_index, image_path)
        # except Exception as e:
        #     print(f"이미지 생성 실패: {e}")
        #     self._show_placeholder_text()
        
        # 임시: 더미 이미지 경로 저장
        dummy_image_path = f"assets/generated/page_{page_index + 1}.png"
        self.page_images[page_index] = dummy_image_path
        print(f"[임시] 이미지 경로 저장: {dummy_image_path}")
        
        # UI 업데이트 (이미지 표시)
        self._update_page_image_display(page_index, dummy_image_path)
    
    def _update_page_image_display(self, page_index: int, image_path: str) -> None:
        """
        생성된 이미지를 UI에 표시합니다.
        
        Args:
            page_index: 페이지 인덱스
            image_path: 생성된 이미지 파일 경로
        """
        # 현재 페이지가 해당 페이지인 경우 즉시 표시
        if self.current_page_idx == page_index:
            print(f"현재 페이지 이미지 업데이트: {image_path}")
            self._display_image_on_label(image_path)
    
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
    
    def _show_placeholder_image(self) -> None:
        """더미 이미지나 기본 이미지를 표시합니다."""
        # 기본 배경 이미지가 있다면 사용
        default_image_path = "assets/image/background.png"
        if Path(default_image_path).exists():
            try:
                pixmap = QPixmap(default_image_path)
                if not pixmap.isNull():
                    # 반투명하게 만들어서 플레이스홀더임을 표시
                    scaled_pixmap = pixmap.scaled(
                        self.ui.label_generatedImage.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.ui.label_generatedImage.setPixmap(scaled_pixmap)
                    self.ui.label_generatedImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    return
            except Exception as e:
                print(f"기본 이미지 로드 실패: {e}")
        
        # 기본 이미지도 없으면 텍스트 표시
        self._show_placeholder_text()
    
    def _update_current_page_image(self) -> None:
        """현재 페이지의 이미지를 업데이트합니다."""
        current_image_path = self.get_page_image(self.current_page_idx)
        if current_image_path:
            self._display_image_on_label(current_image_path)
        else:
            self._show_placeholder_text()
    
    def get_page_image(self, page_index: int) -> str:
        return self.page_images.get(page_index, "")
    
    def set_image_generation_ai(self, image_ai):
        self.image_ai = image_ai
    
    def get_all_page_images(self) -> Dict[int, str]:
        return self.page_images.copy()

        
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
            self._update_current_page_image()
            
    def next_page(self, event):
        """다음 페이지로 이동"""
        total_pages = max(len(self.story_pages_list), 1)
        if self.current_page_idx < total_pages - 1:
            self.current_page_idx += 1
            self.update_page_display()
            self.update_story_display(self.current_page_idx)
            self._update_current_page_image()
            
    def update_page_display(self):
        """페이지 표시 업데이트"""
        total_pages = max(len(self.story_pages_list), 1)  # 최소 1페이지
        self.ui.label_page.setText(f"{self.current_page_idx+1}/{total_pages}")
    
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
            
        total_pages = max(len(self.story_pages_list), 1)
        if self.current_page_idx == (total_pages - 1):
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
