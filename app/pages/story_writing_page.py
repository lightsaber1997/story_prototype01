# app/pages/story_writing_page.py
from PySide6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Dict, List

from app.ui.ui_story_maker_main_window import Ui_StoryMakerMainWindow
from chat_engine import ChatController
from image_gen_engine import ImageGenController
import format_helper


class StoryWritingPage(QMainWindow):
    def __init__(self, stacked_widget, llm_engine, image_gen_engine, app_state):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.llm_engine = llm_engine
        self.image_gen_engine = image_gen_engine
        self.app_state = app_state

        self.ui = Ui_StoryMakerMainWindow()
        self.ui.setupUi(self)

        # 페이지 관련 상태
        self.current_page_idx = 0
        self.total_pages = 3
        self.story_parts: List[str] = []
        self.story_pages_list = []  # double list. each list inside include [user input, ai response, user input, ai response]

        # 각 페이지별 생성된 이미지 저장
        self.page_images: Dict[int, str] = {}  # {page_index: image_path}

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

    def connect_signals(self):
        """버튼과 이벤트를 연결"""
        self.ui.btnContinueStory.clicked.connect(self._on_chat_send)
        self.ui.btnSaveStory.clicked.connect(self.save_story)

        # 페이지 네비게이션
        self.ui.label_page_prev.mousePressEvent = self.previous_page
        self.ui.label_page_next.mousePressEvent = self.next_page

    def _on_chat_send(self) -> None:
        """사용자 입력 처리 및 AI에게 전송"""
        user_input = self.ui.textEdit_childStory.toPlainText().strip()

        if not user_input:
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return

        # 채팅 리스트에 사용자 입력 추가
        item = QListWidgetItem(f"사용자: {user_input}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        self.ui.chatList.addItem(item)

        print(f"user_input: {user_input}")

        # 입력 필드 클리어
        self.ui.textEdit_childStory.clear()

        # AI에게 메시지 전송
        self.chat_controller.operate.emit(user_input)

    def _on_chat_reply(self, payload: Dict[str, str]) -> None:
        """AI 응답 처리"""
        kind = payload["type"]
        text = payload["text"]

        # 채팅 리스트에 AI 응답 추가
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

        # 페이지 및 스토리 표시 업데이트
        self.current_page_idx = len(self.story_pages_list) - 1
        self.update_page_display()
        self.update_story_display()
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()

        # 2번째 메시지마다 이미지 생성
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

            # 이미지 저장
            page_idx = self.current_page_idx
            save_path = f"images/page_{page_idx + 1}.png"

            # 디렉토리가 없으면 생성
            Path("images").mkdir(exist_ok=True)

            # StableV15Engine의 save_image 메서드 사용
            from stable_engine import StableV15Engine
            StableV15Engine.save_image(image, save_path)
            self.page_images[page_idx] = save_path

            print(f"[Image] Saved to {save_path} from prompt: {prompt}")

            # UI에 이미지 표시
            self._display_image_on_label(save_path)

        elif payload["type"] == "error":
            QMessageBox.critical(self, "Image Error", f"Failed to generate image:\n{payload['error']}")

    def _display_image_on_label(self, image_path: str) -> None:
        """생성된 이미지를 UI 라벨에 표시"""
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
        """
        텍스트 세그먼트를 story_pages_list에 추가

        • self.story_pages_list는 "페이지"들의 리스트 (각 페이지는 세그먼트들의 리스트)
        • 각 페이지는 최대 num_page_segment개의 세그먼트를 가질 수 있음
        • 현재 페이지가 가득 차면 새 페이지를 시작함
        """
        # 페이지가 없으면 첫 번째 페이지를 이 세그먼트로 생성
        if not self.story_pages_list:
            self.story_pages_list.append([segment])
            return

        # 마지막 (현재) 페이지로 작업
        last_index = len(self.story_pages_list) - 1
        current_page = self.story_pages_list[last_index]

        # 현재 페이지가 가득 찼는지 확인
        if len(current_page) == num_page_segment:
            # 현재 페이지가 가득 참 → 새 페이지 시작
            self.story_pages_list.append([segment])
        else:
            # 여유 공간이 있음 → 현재 페이지에 추가
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

        # 이전 페이지 버튼 스타일링
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

        # 다음 페이지 버튼 스타일링
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

    def update_story_display(self, page_idx=None):
        """현재 페이지의 스토리 표시 업데이트"""
        if page_idx is None:
            page_idx = len(self.story_pages_list) - 1

        self.ui.chatList_2.clear()

        if page_idx >= 0 and page_idx < len(self.story_pages_list):
            list_segment = self.story_pages_list[page_idx]
            if len(list_segment) > 0:
                for seg in list_segment:  # 최대 4개
                    item = QListWidgetItem(seg)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                    self.ui.chatList_2.addItem(item)

    # 호환성을 위한 추가 메서드들
    def generate_story(self, prompt: str) -> str:
        """LLM을 사용해 스토리 생성"""
        # 실제로는 chat_controller를 통해 비동기로 처리되지만
        # 동기적 인터페이스가 필요한 경우를 위한 래퍼
        try:
            return self.llm_engine.generate(prompt)
        except Exception as e:
            print(f"스토리 생성 오류: {e}")
            return "스토리 생성 중 오류가 발생했습니다."

    def generate_image(self, description: str) -> str:
        """이미지 생성 (파일 경로 반환)"""
        try:
            # 실제로는 image_gen_controller를 통해 비동기로 처리되지만
            # 동기적 인터페이스가 필요한 경우를 위한 래퍼
            return self.image_gen_engine.generate(description)
        except Exception as e:
            print(f"이미지 생성 오류: {e}")
            return "images/placeholder.png"

    def update_state(self, page_index: int, content: str):
        """앱 상태 업데이트"""
        if self.app_state and hasattr(self.app_state, 'pages'):
            # app_state의 구조에 따라 조정 필요
            if hasattr(self.app_state.pages, 'page_index'):
                setattr(self.app_state.pages, f'page_{page_index}', content)
            else:
                # 또는 딕셔너리 형태라면
                self.app_state.pages[page_index] = content