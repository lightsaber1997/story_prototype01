# ── stdlib
import sys, re, json, textwrap, random, string, collections
from pathlib import Path
from typing import Dict, List

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QStyledItemDelegate
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen, QBrush


from main_ui_colorful import Ui_StoryMakerMainWindow
# ── Transformers / Torch
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM



from phi3_mini_engine import Phi3MiniEngine
from chat_engine import *
import format_helper

from stable_engine import StableV15Engine
from image_gen_engine import *

class ChatMessageDelegate(QStyledItemDelegate):
    """채팅 메시지를 위한 커스텀 델리게이트"""
    
    def paint(self, painter, option, index):
        from PySide6.QtGui import QFont, QFontMetrics
        from PySide6.QtCore import QRect
        painter.save()
        
        # 메시지 타입 가져오기
        message_type = index.data(Qt.ItemDataRole.UserRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        # 파스텔톤 색상 설정
        if message_type == "user":
            bg_color = QColor(255, 182, 193)  # 연한 핑크 (라이트 핑크)
            text_color = QColor(139, 69, 19)  # 진한 갈색
            is_user = True
        elif message_type == "correction":
            bg_color = QColor(255, 239, 153)  # 연한 노란색 (라이트 골든로드 옐로우)
            text_color = QColor(139, 69, 19)  # 진한 갈색
            is_user = False
        elif message_type == "story":
            bg_color = QColor(173, 216, 230)  # 연한 파란색 (라이트 블루)
            text_color = QColor(25, 25, 112)  # 미드나이트 블루
            is_user = False
        else:
            bg_color = QColor(144, 238, 144)  # 연한 초록색 (라이트 그린)
            text_color = QColor(0, 100, 0)  # 다크 그린
            is_user = False
        
        # 폰트 설정 (굵게)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        
        # 텍스트 크기 측정
        font_metrics = QFontMetrics(font)
        
        # 최대 너비 설정 (전체 너비의 70%)
        max_text_width = int(option.rect.width() * 0.7) - 56  # 패딩과 여백 고려
        
        text_rect = font_metrics.boundingRect(
            QRect(0, 0, max_text_width, 2000),  # 충분한 높이 제공
            Qt.TextFlag.TextWordWrap,
            text
        )
        
        # 말풍선 크기 계산 (패딩 20 적용)
        bubble_padding = 20
        bubble_width = text_rect.width() + bubble_padding * 2
        bubble_height = text_rect.height() + bubble_padding * 2
        
        # 최소 크기 보장
        bubble_width = max(bubble_width, 100)  # 최소 너비
        bubble_height = max(bubble_height, 50)  # 최소 높이
        
        # 말풍선 위치 계산
        if is_user:
            # 사용자 메시지 - 오른쪽 정렬
            bubble_x = option.rect.right() - bubble_width - 2
        else:
            # AI 메시지 - 왼쪽 정렬
            bubble_x = option.rect.left() + 2
        
        bubble_y = option.rect.top() + (option.rect.height() - bubble_height) // 2
        bubble_rect = QRect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # 자연스러운 그림자 그리기 (여러 레이어로 블러 효과)
        shadow_layers = [
            (1, 1, 8),   # (x_offset, y_offset, alpha)
            (2, 2, 6),
            (3, 3, 4),
        ]
        
        for x_offset, y_offset, alpha in shadow_layers:
            shadow_rect = bubble_rect.adjusted(x_offset, y_offset, x_offset, y_offset)
            shadow_color = QColor(0, 0, 0, alpha)  # 매우 연한 그림자
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(QPen(shadow_color))
            painter.drawRoundedRect(shadow_rect, 18, 18)
        
        # 배경 그리기
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(0, 0, 0, 0)))  # 투명한 펜
        painter.drawRoundedRect(bubble_rect, 18, 18)
        
        # 자연스러운 테두리 그리기
        border_color = QColor(0, 0, 0, 25)  # 매우 연한 검은색 테두리
        if message_type == "user":
            border_color = QColor(139, 69, 19, 40)  # 핑크 말풍선에는 연한 갈색 테두리
        elif message_type == "correction":
            border_color = QColor(218, 165, 32, 40)  # 노란색 말풍선에는 연한 골든로드 테두리
        elif message_type == "story":
            border_color = QColor(25, 25, 112, 40)  # 파란색 말풍선에는 연한 네이비 테두리
        else:
            border_color = QColor(0, 100, 0, 40)  # 초록색 말풍선에는 연한 다크그린 테두리
        
        painter.setBrush(QBrush())  # 투명한 브러시
        painter.setPen(QPen(border_color, 1))  # 1px 두께의 연한 테두리
        painter.drawRoundedRect(bubble_rect, 18, 18)
        
        # 텍스트 그리기
        painter.setPen(QPen(text_color))
        text_draw_rect = bubble_rect.adjusted(bubble_padding, bubble_padding, -bubble_padding, -bubble_padding)
        
        if is_user:
            painter.drawText(text_draw_rect, Qt.AlignmentFlag.AlignRight | Qt.TextFlag.TextWordWrap, text)
        else:
            painter.drawText(text_draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, text)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """아이템 크기 힌트 - 텍스트 길이에 따라 동적 크기 조절"""
        from PySide6.QtGui import QFont, QFontMetrics
        from PySide6.QtCore import QRect, QSize
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return QSize(option.rect.width(), 60)
        
        # 폰트 설정
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        
        # 텍스트 크기 측정
        font_metrics = QFontMetrics(font)
        
        # 최대 너비 설정 (전체 너비의 70%)
        max_text_width = max(200, int(option.rect.width() * 0.7) - 56)
        
        text_rect = font_metrics.boundingRect(
            QRect(0, 0, max_text_width, 2000),
            Qt.TextFlag.TextWordWrap,
            text
        )
        
        # 패딩을 포함한 높이 계산
        bubble_padding = 20
        height = max(80, text_rect.height() + bubble_padding * 2 + 20)  # 최소 높이 80px, 여백 20px
        
        return QSize(option.rect.width(), height)



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
        
        # 버튼 연결 해야 할 부분

        from chat_gpt_engine import ChatGPTEngine
        # initialization for llm engine
        self.llm_engine = ChatGPTEngine()
        self.story_parts: List[str] = []
        self.chat_controller = ChatController(self._on_chat_reply, self.llm_engine)

        # For image generation
        self.image_gen_engine = StableV15Engine()
        self.image_gen_controller = ImageGenController(
            self._on_image_gen_ready, 
            self.image_gen_engine)

        # 각 페이지별 생성된 이미지 저장
        self.page_images: Dict[int, str] = {}  # {page_index: image_path}
        
        # 채팅 리스트에 커스텀 델리게이트 설정
        self.chat_delegate = ChatMessageDelegate()
        self.ui.chatList.setItemDelegate(self.chat_delegate)
    
    def closeEvent(self, event):
        """애플리케이션 종료 시 스레드 정리"""
        try:
            if hasattr(self, 'chat_controller'):
                self.chat_controller.workerThread.quit()
                self.chat_controller.workerThread.wait(3000)  # 3초 대기
            if hasattr(self, 'image_gen_controller'):
                self.image_gen_controller.workerThread.quit()
                self.image_gen_controller.workerThread.wait(3000)  # 3초 대기
        except:
            pass
        event.accept()


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
            
        # 사용자 메시지 - 오른쪽 정렬, 파란색 배경
        self._add_chat_message(user_input, is_user=True)

        print(f"user_input: {user_input}")
        print(type(user_input))
        
        self.ui.textEdit_childStory.clear()

        self.chat_controller.operate.emit(user_input)


    def _on_chat_reply(self, payload: Dict[str, str]) -> None:
        kind = payload["type"]
        text = payload["text"]

        if kind == "story_line":
            # AI 문법 수정 메시지 - 왼쪽 정렬, 연한 회색 배경
            self._add_chat_message(f"문법 수정: {text}", is_user=False, message_type="correction")
            self._append_to_story(text + " ")

        elif kind == "ai_suggestion":
            # AI 스토리 제안 메시지 - 왼쪽 정렬, 초록색 배경
            self._add_chat_message(text, is_user=False, message_type="story")
            self._append_to_story(text + " ")

        elif kind == "chat_answer":
            # AI 일반 답변 메시지 - 왼쪽 정렬, 회색 배경
            self._add_chat_message(text, is_user=False, message_type="chat")
        
        # 스토리 페이지가 있을 때만 업데이트
        if self.story_pages_list:
            self.current_page_idx = len(self.story_pages_list) - 1
            self.update_page_display()
            self.update_story_display()
            
            # print every 2nd message in a page
            segments = self.story_pages_list[self.current_page_idx]
            select_idx = 1
            if segments is not None and (len(segments) == select_idx + 1):
                prompt_for_image = segments[select_idx]
                prompt_for_image = format_helper.first_sentence(prompt_for_image)
                prompt_for_image += " children's picture book"
                print(prompt_for_image)
                self.image_gen_controller.operate.emit(prompt_for_image)
        
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()

        

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
    
    def _add_chat_message(self, text: str, is_user: bool = False, message_type: str = "normal") -> None:
        """메신저 스타일의 채팅 메시지를 추가합니다."""
        from PySide6.QtWidgets import QWidget, QLabel
        from PySide6.QtCore import Qt
        
        # 커스텀 위젯을 만들어서 스타일 적용
        item = QListWidgetItem()
        
        if is_user:
            # 사용자 메시지 - 오른쪽 정렬, 빨간색 말풍선
            item.setText(f"나: {text}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            # 직접 스타일시트 적용
            item.setData(Qt.ItemDataRole.UserRole, "user")
        else:
            # AI 메시지 - 왼쪽 정렬
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # 메시지 타입에 따른 색상 구분
            if message_type == "correction":
                item.setText(f"🔧 문법수정: {text}")
                item.setData(Qt.ItemDataRole.UserRole, "correction")
            elif message_type == "story":
                item.setText(f"📖 AI: {text}")
                item.setData(Qt.ItemDataRole.UserRole, "story")
            else:
                item.setText(f"🤖 AI: {text}")
                item.setData(Qt.ItemDataRole.UserRole, "chat")
        
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        
        self.ui.chatList.addItem(item)
        self.ui.chatList.scrollToBottom()
        
        # 아이템 추가 후 스타일 적용
        self._apply_message_style(self.ui.chatList.count() - 1)
        print(f"메시지 추가됨: {'사용자' if is_user else 'AI'} - {text[:50]}...")
    
    def _apply_message_style(self, row: int) -> None:
        """메시지 아이템에 스타일을 적용합니다."""
        item = self.ui.chatList.item(row)
        if not item:
            return
            
        message_type = item.data(Qt.ItemDataRole.UserRole)
        
        if message_type == "user":
            # 사용자 메시지 - 빨간색
            item.setBackground(QColor(220, 20, 60))
            item.setForeground(QColor(255, 255, 255))
        elif message_type == "correction":
            # 문법 수정 - 노란색
            item.setBackground(QColor(255, 215, 0))
            item.setForeground(QColor(0, 0, 0))
        elif message_type == "story":
            # 스토리 제안 - 파란색
            item.setBackground(QColor(30, 144, 255))
            item.setForeground(QColor(255, 255, 255))
        else:
            # 일반 채팅 - 초록색
            item.setBackground(QColor(34, 139, 34))
            item.setForeground(QColor(255, 255, 255))


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
            
        # 사용자 메시지 추가
        self._add_chat_message(user_input, is_user=True)
        
        # AI 응답 (실제로는 AI 모델 호출 예정)
        # 아래 48th line을 주석 해제하고 49th line을 주석처리 하시면 됩니다.
        # ai_response = ask_ai(user_input)
        ai_response = f"AI가 '{user_input}'을 바탕으로 스토리를 계속 만들어갑니다..."
        self._add_chat_message(ai_response, is_user=False, message_type="story")
        
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
