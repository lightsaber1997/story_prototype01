# ── stdlib
import os
import sys, re, json, textwrap, random, string, collections
from pathlib import Path
from typing import Dict, List

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QHBoxLayout, QWidget
from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QPalette, QBrush, QColor

# 컴포넌트 임포트
from components.navigation_bar import NavigationBar
from components.chat_area import ChatArea
from components.storybook_area import StorybookArea
from components.settings_dialog import SettingsDialog
from components.home_screen import HomeScreen

# AI 엔진 임포트
from core.llm_factory import get_chat_controller
import format_helper
from engines.stable_engine import StableV15Engine
from engines.q_stable_engine import QStableV21Engine
from engines.image_gen_engine import *
from engines.img_to_text_engine import *
from tts.tts_controller import TTSController


class MainApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.setupAI()
        self.connectSignals()

        # 스토리 관리 변수들
        self.current_page_idx = 0
        self.story_pages_list = []  # 각 페이지별 스토리 세그먼트들
        self.page_images: Dict[int, str] = {}  # 각 페이지별 생성된 이미지
        self.story_parts: List[str] = []

        # 초기 상태 설정
        self.updateUI()

        self._new_story_started = False

    def setupUI(self):
        """UI 설정"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.navigationBar = NavigationBar()
        self.chatArea = ChatArea()

        root_path = os.path.dirname(__file__)
        self.storybookArea = StorybookArea(root_path)

        layout.addWidget(self.navigationBar, 1)
        layout.addWidget(self.chatArea, 3)
        layout.addWidget(self.storybookArea, 5)


    def setupAI(self):
        """AI 엔진 설정"""
        try:
            # llm 모델 가져오고 컨트롤러 설정
            self.chat_controller = get_chat_controller(
                result_callback=self._on_chat_reply
            )

            # 시그널 연결
            self.chat_controller.worker.token_chat_Ready.connect(self._on_token_chat)
            self.chat_controller.worker.correction_ready.connect(self._on_correction_ready)
            self.chat_controller.worker.token_story_continue_Ready.connect(self._on_token_story_continue)

            base_dir = os.path.dirname(__file__)  # 또는 os.getcwd() 가능

            text_encoder_path = os.path.join(base_dir, "data", "models", "text_encoder.onnx", "model.onnx")
            vae_decoder_path = os.path.join(base_dir, "data", "models", "vae_decoder.onnx", "model.onnx")
            unet_path = os.path.join(base_dir, "data", "models", "unet.onnx", "model.onnx")

            # 이미지 생성 엔진
            self.image_gen_engine = QStableV21Engine(
                text_encoder=text_encoder_path,
                vae_decoder=vae_decoder_path,
                unet=unet_path,
                scheduler="ddim",
                channel_last_latent=True
            )
            
            self.image_gen_controller = ImageGenController(
                self._on_image_gen_ready,
                self.image_gen_engine
            )

            # self.img_to_text_engine = DummyImgToTextEngine()
            # self.img_to_text_controller = ImgToTextController(
            #     self.img_to_text_engine,
            #     self._on_img_to_text_ready
            # )

            self.img_to_text_engine = ClipImgToTextEngine(base_dir)
            self.img_to_text_controller = ImgToTextController(
                self.img_to_text_engine,
                self._on_img_to_text_ready
            )

            print("AI 엔진 초기화 완료")
        except Exception as e:
            print(f"AI 엔진 초기화 실패: {e}")
            QMessageBox.warning(self, "AI 엔진 오류", f"AI 엔진 초기화에 실패했습니다: {e}")

    def connectSignals(self):
        """시그널 연결"""
        # 네비게이션 바 시그널
        self.navigationBar.homeClicked.connect(self.onHomeClicked)
        self.navigationBar.settingsClicked.connect(self.onSettingsClicked)
        self.navigationBar.helpClicked.connect(self.onHelpClicked)

        # 채팅 영역 시그널
        self.chatArea.messageSent.connect(self.onMessageSent)

        # 스토리북 영역 시그널
        self.storybookArea.pageChanged.connect(self.onPageChanged)
        self.storybookArea.storySaved.connect(self.onStorySaved)

    def closeEvent(self, event):
        """애플리케이션 종료 시 스레드 정리"""
        try:
            if hasattr(self, 'chat_controller'):
                self.chat_controller.workerThread.quit()
                self.chat_controller.workerThread.wait(3000)
            if hasattr(self, 'image_gen_controller'):
                self.image_gen_controller.workerThread.quit()
                self.image_gen_controller.workerThread.wait(3000)
        except:
            pass
        event.accept()

    # ========== 이벤트 핸들러들 ==========

    def onHomeClicked(self):
        """홈 버튼 클릭"""
        main_window: MainWindow = self.window()
        main_window.showHome()

    def onSettingsClicked(self):
        """설정 버튼 클릭"""
        self.navigationBar.setActiveButton("settings")
        dlg = SettingsDialog(
            None,
            current_rate=self.storybookArea.tts_rate,
            current_mode=self.storybookArea.tts_mode,
            current_animated=self.storybookArea.typing_animated,
            current_interval=self.storybookArea.typing_interval,
            current_by_word=self.storybookArea.typing_by_word
        )
        if dlg.exec():
            values = dlg.get_values()
            # 각각 적용
            self.storybookArea.applyTTSSettings(values["rate"], values["mode"])
            self.storybookArea.applyTypewriterSettings(values["animated"], values["interval"], values["by_word"])

    def onHelpClicked(self):
        """도움말 버튼 클릭"""
        # self.navigationBar.setActiveButton("help")
        QMessageBox.information(self, "도움말",
                                "MyStoryPal 사용법:\n\n"
                                "1. 채팅창에 스토리를 입력하세요\n"
                                "2. AI가 문법을 수정하고 스토리를 이어갑니다\n"
                                "3. 오른쪽에서 완성된 스토리북을 확인하세요\n"
                                "4. 이미지가 자동으로 생성됩니다")

    def onMessageSent(self, message: str):
        """메시지 전송 처리"""

        if not message.strip():
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return
        self._new_story_started = True

        # 사용자 메시지를 채팅에 추가
        self.chatArea.addMessage(message, is_user=True)
        # AI에게 메시지 전송
        if hasattr(self, 'chat_controller'):
            self.chat_controller.operate.emit(message)
        else:
            QMessageBox.warning(self, "AI 오류", "AI 엔진이 초기화되지 않았습니다.")

    def onPageChanged(self, page: int):
        """페이지 변경 처리"""
        self.current_page_idx = page
        self.updateStorybookDisplay()

    def onStorySaved(self):
        """스토리 저장 처리"""
        QMessageBox.information(self, "저장 완료", "스토리북이 성공적으로 저장되었습니다!")
        
    def handleImageInput(self, file_path: str):
        """이미지 업로드 입력 처리 (OCR → 스토리 반영)"""
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "파일 오류", "이미지 파일이 존재하지 않습니다.")
            return

        print(f"[Image Input] 업로드된 파일: {file_path}")
        self.img_to_text_controller.operate.emit(file_path)

    def _on_img_to_text_ready(self, payload: dict):
        if payload["type"] == "img2text":
            matches = payload["matches"]
            # select the first one
            text = matches[0]
            print(f"[Img2Text] {text}")
            print(f"_on_img_to_text_ready")

            # 1) ChatArea에도 메시지 추가
            self.chatArea.addMessage(text, is_user=False, message_type="chat")

            # 2) Storybook에도 반영
            self._append_to_story(text)

        elif payload["type"] == "error":
            QMessageBox.critical(self, "이미지 인식 오류", f"OCR 실패: {payload['error']}")

    def _on_chat_reply(self, payload: Dict[str, str]) -> None:
        kind = payload.get("type")
        text = payload.get("text", "")
        print(f"[AI COMPLETE] {kind}: {text}")

        if kind == "story_answer":
            self._append_to_story(text.strip())

        elif kind == "correction_answer":
            # grammar correction 완성본도 storybook 교체
            self._append_to_story(text.strip())
            self.checkImageGeneration()
        return

    def _on_token_chat(self, text: str):
        if not text.strip():
            return
        self.chatArea.updateStreamingMessage(text, message_type="chat")

    def _on_correction_ready(self, payload: dict):
        text = payload.get("text", "")
        if not text.strip():
            return
        # add a full message instead of streaming
        self.chatArea.addMessage(f"Grammar Correction: {text}", is_user=False)
        self._append_to_story(text.strip())
        self.checkImageGeneration()



    def _on_token_story_continue(self, text: str):
        if not text.strip():
            return
        self.chatArea.updateStreamingMessage(text, message_type="story")

    def _on_image_gen_ready(self, payload: dict):
        """이미지 생성 완료 처리"""
        if payload["type"] == "image_generated":
            image = payload["image"]
            prompt = payload["prompt"]
            page_idx = payload["page_idx"]

            # 이미지 저장
            base_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(base_dir, "images")  
            os.makedirs(images_dir, exist_ok=True)

            save_path = os.path.join(images_dir, f"page_{page_idx + 1}.png")
            QStableV21Engine.save_image(image, save_path)
            self.page_images[page_idx] = save_path

            print(f"[Image] Saved to {save_path} from prompt: {prompt}")

            # UI에 이미지 표시
            self.storybookArea.setStoryImage(save_path)
            if page_idx in self._image_gen_in_progress:
                self._image_gen_in_progress.remove(page_idx)

        elif payload["type"] == "error":
            QMessageBox.critical(self, "이미지 생성 오류", f"이미지 생성에 실패했습니다:\n{payload['error']}")

    def _append_to_story(self, segment: str) -> None:
        segment = segment.strip()
        self.story_parts.append(segment)
        self._add_to_story_pages_list(segment)

        # 항상 최신 페이지로 이동
        self.current_page_idx = len(self.story_pages_list) - 1

        def _compose_text(page_idx: int) -> str:
            segments = self.story_pages_list[page_idx]
            return " ".join(s.strip() for s in segments if s and s.strip())

        story_text = _compose_text(self.current_page_idx)

        # 페이지/텍스트 갱신
        self.updateStorybookArea()
        with QSignalBlocker(self.storybookArea):
            self.storybookArea.setCurrentPage(self.current_page_idx)
        self.storybookArea.setStoryText(story_text, page=self.current_page_idx, animated=True)

        # 이미지 동기화
        page_idx = self.current_page_idx
        if page_idx in self.page_images:
            path = self.page_images[page_idx]
            # Only (re)draw if it's different from what’s shown
            shown = getattr(self.storybookArea, "_current_image_path", None)
            if shown != path:
                self.storybookArea.setStoryImage(path)

    def _add_to_story_pages_list(self, segment: str, num_page_segment: int = 4) -> bool:
        """스토리 세그먼트를 페이지별로 관리"""
        if not self.story_pages_list:
            self.story_pages_list.append([segment])
            return True  # 첫 페이지 생성

        last_index = len(self.story_pages_list) - 1
        current_page = self.story_pages_list[last_index]

        if len(current_page) >= num_page_segment:
            self.story_pages_list.append([segment])
            return True  # 새 페이지 생성
        else:
            current_page.append(segment)
            return False  # 기존 페이지에 추가

    def checkImageGeneration(self):
        """이미지 생성 조건 확인 (correction일 때 진행)"""
        if not self.story_pages_list:
            return
        # 페이지별 진행 상태 확인
        if not hasattr(self, "_image_gen_in_progress"):
            self._image_gen_in_progress = set()
        # 이미 생성된 경우
        if self.current_page_idx in self.page_images:
            return
        # 이미 생성 중인 경우
        if self.current_page_idx in self._image_gen_in_progress:
            return

        segments = self.story_pages_list[self.current_page_idx]
        select_idx = 1
        print("[checkImageGeneration 시작]")

        if segments is not None and (len(segments) == select_idx + 1):
            prompt_for_image = segments[select_idx]
            prompt_for_image = format_helper.first_sentence(prompt_for_image)
            prompt_for_image += " children's picture book"
            # DEBUG
            #prompt_for_image = "A magical dragon, children’s storybook style"
            print(f"이미지 생성 프롬프트: {prompt_for_image}")
            self._image_gen_in_progress.add(self.current_page_idx)

            if hasattr(self, 'image_gen_controller'):
                self.image_gen_controller.operate.emit({
                    "prompt": prompt_for_image,
                    "page_idx": self.current_page_idx  # 페이지 번호 확인 가능해야
                })

    # ========== UI 업데이트 ==========

    def updateUI(self):
        """전체 UI 업데이트"""
        self.updateStorybookArea()
        self.updateStorybookDisplay()

    def updateStorybookArea(self):
        """스토리북 영역 업데이트"""
        if self.story_pages_list:
            total_pages = len(self.story_pages_list)
            self.current_page_idx = min(self.current_page_idx, total_pages - 1)

            self.storybookArea.setPageCount(total_pages)
            self.storybookArea.setCurrentPage(self.current_page_idx)

    def updateStorybookDisplay(self):
        """스토리북 내용 표시 업데이트"""
        if self.story_pages_list and self.current_page_idx < len(self.story_pages_list):
            segments = self.story_pages_list[self.current_page_idx]
            story_text = " ".join(s.strip() for s in segments if s and s.strip())
            # 캐시에 있는 텍스트 우선 사용
            cached_text = self.storybookArea._page_texts.get(self.current_page_idx, story_text)
            self.storybookArea.setStoryText(cached_text, page=self.current_page_idx, animated=False)
            if self.current_page_idx in self.page_images:
                self.storybookArea.setStoryImage(self.page_images[self.current_page_idx])
            else:
                self.storybookArea.clearImage()
        else:
            self.storybookArea.setStoryText("", page=self.current_page_idx, animated=False)
            self.storybookArea.clearImage()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyStoryPal")
        self.resize(1200, 700)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 홈 화면&메인 앱
        self.home = HomeScreen(logo_path="assets/logo.png")
        self.mainApp = MainApp()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.mainApp)

        # 시그널 연결
        self.home.startRequested.connect(self.showMainApp)
        self.home.imageUploaded.connect(self.onImageUploaded)

    def showMainApp(self):
        self.stack.setCurrentWidget(self.mainApp)

    def showHome(self):
        self.stack.setCurrentWidget(self.home)

    def onImageUploaded(self, file_path: str):
        self.showMainApp()
        self.mainApp.handleImageInput(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())