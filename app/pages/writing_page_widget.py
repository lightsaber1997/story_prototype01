from PySide6.QtWidgets import QWidget, QMessageBox, QListWidgetItem, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Dict, List

from app.ui.ui_story_maker_main_window import Ui_StoryMakerMainWindow
from chat_engine import ChatController
from image_gen_engine import ImageGenController
import format_helper


class WritingPageWidget(QWidget):  # QMainWindow -> QWidget으로 변경
    def __init__(self, stacked_widget, llm_engine, image_gen_engine, app_state):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.llm_engine = llm_engine
        self.image_gen_engine = image_gen_engine
        self.app_state = app_state

        self.ui = Ui_StoryMakerMainWindow()

        # QWidget은 setupUi의 인자로 self를 직접 전달하여 UI를 설정
        self.ui.setupUi(self)

        # QWidget에는 setCentralWidget이 없으므로 레이아웃을 사용
        # Ui_StoryMakerMainWindow.setupUi가 레이아웃을 생성하므로 추가적인 레이아웃 설정은 불필요

        # 페이지 관련 상태
        self.current_page_idx = 0
        self.total_pages = 3
        self.story_parts: List[str] = []
        self.story_pages_list = []

        # 각 페이지별 생성된 이미지 저장
        self.page_images: Dict[int, str] = {}

        # 엔진 초기화
        self.chat_controller = ChatController(self._on_chat_reply, self.llm_engine)
        self.image_gen_controller = ImageGenController(
            self._on_image_gen_ready,
            self.image_gen_engine
        )

        # 시그널 연결
        self.connect_signals()

        # 초기 상태 설정
        self.update_page_display()

    # 이하 메서드는 원본과 동일하게 유지
    def connect_signals(self):
        """버튼과 이벤트를 연결"""
        self.ui.btnContinueStory.clicked.connect(self._on_chat_send)
        self.ui.btnSaveStory.clicked.connect(self.save_story)

        self.ui.label_page_prev.mousePressEvent = self.previous_page
        self.ui.label_page_next.mousePressEvent = self.next_page

    def _on_chat_send(self) -> None:
        """사용자 입력 처리 및 AI에게 전송"""
        user_input = self.ui.textEdit_childStory.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return

        item = QListWidgetItem(f"사용자: {user_input}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        self.ui.chatList.addItem(item)
        print(f"user_input: {user_input}")
        self.ui.textEdit_childStory.clear()
        self.chat_controller.operate.emit(user_input)

    def _on_chat_reply(self, payload: Dict[str, str]) -> None:
        """AI 응답 처리"""
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

        self.current_page_idx = len(self.story_pages_list) - 1
        self.update_page_display()
        self.update_story_display()
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()
        segments = self.story_pages_list[self.current_page_idx]
        select_idx = 1
        if segments is not None and (len(segments) == select_idx + 1):
            prompt_for_image = segments[select_idx]
            prompt_for_image = format_helper.first_sentence(prompt_for_image)
            prompt_for_image += " children's picture book"
            print(f"Generating image with prompt: {prompt_for_image}")
            self.image_gen_controller.operate.emit(prompt_for_image)

    def _on_image_gen_ready(self, payload: dict):
        """이미지 생성 완료 처리"""
        if payload["type"] == "image_generated":
            image = payload["image"]
            prompt = payload["prompt"]
            page_idx = self.current_page_idx
            save_path = f"images/page_{page_idx + 1}.png"
            Path("images").mkdir(exist_ok=True)
            from stable_engine import StableV15Engine
            StableV15Engine.save_image(image, save_path)
            self.page_images[page_idx] = save_path
            print(f"[Image] Saved to {save_path} from prompt: {prompt}")
            self._display_image_on_label(save_path)
        elif payload["type"] == "error":
            QMessageBox.critical(self, "Image Error", f"Failed to generate image:\n{payload['error']}")

    def _display_image_on_label(self, image_path: str) -> None:
        """생성된 이미지를 UI 라벨에 표시"""
        try:
            if Path(image_path).exists():
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
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
                self._show_placeholder_image()
        except Exception as e:
            print(f"이미지 표시 중 오류 발생: {e}")
            self._show_placeholder_text()

    def _show_placeholder_text(self) -> None:
        """플레이스홀더 텍스트를 표시"""
        self.ui.label_generatedImage.clear()
        self.ui.label_generatedImage.setText("🎨 Generated image will appear here")
        self.ui.label_generatedImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _show_placeholder_image(self) -> None:
        """플레이스홀더 이미지를 표시"""
        self._show_placeholder_text()

    def _append_to_story(self, segment: str) -> None:
        """스토리에 새로운 세그먼트 추가"""
        self.story_parts.append(segment)
        self._add_to_story_pages_list(segment)
        print(f"self.story_pages_list: {self.story_pages_list}")

    def _add_to_story_pages_list(self, segment: str, num_page_segment: int = 4) -> None:
        """텍스트 세그먼트를 story_pages_list에 추가"""
        if not self.story_pages_list:
            self.story_pages_list.append([segment])
            return
        last_index = len(self.story_pages_list) - 1
        current_page = self.story_pages_list[last_index]
        if len(current_page) == num_page_segment:
            self.story_pages_list.append([segment])
        else:
            current_page.append(segment)

    def save_story(self):
        """스토리북 저장"""
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
        self.ui.label_page.setText(f"{self.current_page_idx + 1}/{self.total_pages}")
        if self.current_page_idx == 0:
            self.ui.label_page_prev.setStyleSheet("""
                QLabel { color: #666666; background: rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 10px 15px; min-width: 40px; min-height: 40px; }
            """)
        else:
            self.ui.label_page_prev.setStyleSheet("""
                QLabel { color: #ffffff; background: rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 10px 15px; min-width: 40px; min-height: 40px; }
                QLabel:hover { background: rgba(255, 255, 255, 0.2); color: #ffd54f; }
            """)
        if self.current_page_idx == (self.total_pages - 1):
            self.ui.label_page_next.setStyleSheet("""
                QLabel { color: #666666; background: rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 10px 15px; min-width: 40px; min-height: 40px; }
            """)
        else:
            self.ui.label_page_next.setStyleSheet("""
                QLabel { color: #ffffff; background: rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 10px 15px; min-width: 40px; min-height: 40px; }
                QLabel:hover { background: rgba(255, 255, 255, 0.2); color: #ffd54f; }
            """)

    def update_story_display(self, page_idx=None):
        """현재 페이지의 스토리 표시 업데이트"""
        if page_idx is None:
            page_idx = len(self.story_pages_list) - 1
        self.ui.chatList_2.clear()
        if page_idx >= 0 and page_idx < len(self.story_pages_list):
            list_segment = self.story_pages_list[page_idx]
            if len(list_segment) > 0:
                for seg in list_segment:
                    item = QListWidgetItem(seg)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                    self.ui.chatList_2.addItem(item)

    def generate_story(self, prompt: str) -> str:
        """LLM을 사용해 스토리 생성"""
        try:
            return self.llm_engine.generate(prompt)
        except Exception as e:
            print(f"스토리 생성 오류: {e}")
            return "스토리 생성 중 오류가 발생했습니다."

    def generate_image(self, description: str) -> str:
        """이미지 생성 (파일 경로 반환)"""
        try:
            return self.image_gen_engine.generate(description)
        except Exception as e:
            print(f"이미지 생성 오류: {e}")
            return "images/placeholder.png"

    def update_state(self, page_index: int, content: str):
        """앱 상태 업데이트"""
        if self.app_state and hasattr(self.app_state, 'pages'):
            if hasattr(self.app_state.pages, 'page_index'):
                setattr(self.app_state.pages, f'page_{page_index}', content)
            else:
                self.app_state.pages[page_index] = content