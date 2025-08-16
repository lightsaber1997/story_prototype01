# ── stdlib
import sys, re, json, textwrap, random, string, collections
from pathlib import Path
from typing import Dict, List

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QBrush, QColor

# 컴포넌트 임포트
from components.navigation_bar import NavigationBar
from components.chat_area import ChatArea
from components.storybook_area import StorybookArea

# AI 엔진 임포트
from engines.phi3_mini_engine import Phi3MiniEngine
from engines.chat_engine import *
import format_helper
from engines.stable_engine import StableV15Engine
from engines.image_gen_engine import *


class ModularMainApp(QMainWindow):
    def __init__(self):
        super().__init__()
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
    
    def setupUI(self):
        """UI 설정"""
        self.setWindowTitle("MyStoryPal")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)  # 더 적당한 크기로 조정
        
        # 메인 배경색 설정 - main_ui_colorful.py와 동일한 파란색
        palette = QPalette()
        brush = QBrush(QColor(85, 175, 240, 255))  # main_ui_colorful.py와 동일한 파란색
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        self.setPalette(palette)
        
        # 중앙 위젯 설정
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        # 메인 수평 레이아웃 (둥근 모서리 없이, 세로 전체 차지)
        self.mainLayout = QHBoxLayout(self.centralWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        self.mainLayout.setSpacing(0)  # 간격 제거
        
        # 컴포넌트들 생성 및 추가
        self.navigationBar = NavigationBar()
        self.chatArea = ChatArea()
        self.storybookArea = StorybookArea()
        
        # 레이아웃에 컴포넌트 추가 - 3:5 비율로 조정
        self.mainLayout.addWidget(self.navigationBar)  # 고정 너비 (80px)
        self.mainLayout.addWidget(self.chatArea, 3)    # 채팅 영역 3
        self.mainLayout.addWidget(self.storybookArea, 5)  # 스토리북 영역 5
    
    def setupAI(self):
        """AI 엔진 설정"""
        try:
            from engines.chat_gpt_engine import ChatGPTEngine
            self.llm_engine = ChatGPTEngine()
            self.chat_controller = ChatController(self._on_chat_reply, self.llm_engine)

            # 이미지 생성 엔진
            self.image_gen_engine = StableV15Engine()
            self.image_gen_controller = ImageGenController(
                self._on_image_gen_ready, 
                self.image_gen_engine)
            
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
        self.navigationBar.setActiveButton("home")
        QMessageBox.information(self, "홈", "홈 기능이 구현될 예정입니다.")
    
    def onSettingsClicked(self):
        """설정 버튼 클릭"""
        self.navigationBar.setActiveButton("settings")
        QMessageBox.information(self, "설정", "설정 기능이 구현될 예정입니다.")
    
    def onHelpClicked(self):
        """도움말 버튼 클릭"""
        self.navigationBar.setActiveButton("help")
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
    
    # ========== AI 응답 처리 ==========
    
    def _on_chat_reply(self, payload: Dict[str, str]) -> None:
        """AI 채팅 응답 처리"""
        kind = payload["type"]
        text = payload["text"]

        if kind == "story_line":
            # AI 문법 수정 메시지
            self.chatArea.addMessage(f"문법 수정: {text}", is_user=False, message_type="correction")
            self._append_to_story(text + " ")

        elif kind == "ai_suggestion":
            # AI 스토리 제안 메시지
            self.chatArea.addMessage(text, is_user=False, message_type="story")
            self._append_to_story(text + " ")

        elif kind == "chat_answer":
            # AI 일반 답변 메시지
            self.chatArea.addMessage(text, is_user=False, message_type="chat")
        
        # 스토리 업데이트
        self.updateUI()
        
        # 이미지 생성 조건 확인
        self.checkImageGeneration()
    
    def _on_image_gen_ready(self, payload: dict):
        """이미지 생성 완료 처리"""
        if payload["type"] == "image_generated":
            image = payload["image"]
            prompt = payload["prompt"]

            # 이미지 저장
            page_idx = self.current_page_idx
            save_path = f"images/page_{page_idx + 1}.png"
            StableV15Engine.save_image(image, save_path)
            self.page_images[page_idx] = save_path

            print(f"[Image] Saved to {save_path} from prompt: {prompt}")
            
            # UI에 이미지 표시
            self.storybookArea.setStoryImage(save_path)

        elif payload["type"] == "error":
            QMessageBox.critical(self, "이미지 생성 오류", f"이미지 생성에 실패했습니다:\n{payload['error']}")
    
    # ========== 스토리 관리 ==========
    
    def _append_to_story(self, segment: str) -> None:
        """스토리 세그먼트 추가"""
        self.story_parts.append(segment)
        self._add_to_story_pages_list(segment)
        print(f"story_pages_list: {self.story_pages_list}")
    
    def _add_to_story_pages_list(self, segment: str, num_page_segment: int = 4) -> None:
        """스토리 세그먼트를 페이지별로 관리"""
        if not self.story_pages_list:
            self.story_pages_list.append([segment])
            return

        last_index = len(self.story_pages_list) - 1
        current_page = self.story_pages_list[last_index]

        if len(current_page) == num_page_segment:
            self.story_pages_list.append([segment])
        else:
            current_page.append(segment)
    
    def checkImageGeneration(self):
        """이미지 생성 조건 확인"""
        if not self.story_pages_list:
            return
            
        segments = self.story_pages_list[self.current_page_idx]
        select_idx = 1
        
        if segments is not None and (len(segments) == select_idx + 1):
            prompt_for_image = segments[select_idx]
            prompt_for_image = format_helper.first_sentence(prompt_for_image)
            prompt_for_image += " children's picture book"
            print(f"이미지 생성 프롬프트: {prompt_for_image}")
            
            if hasattr(self, 'image_gen_controller'):
                self.image_gen_controller.operate.emit(prompt_for_image)
    
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
            story_text = " ".join(segments)
            self.storybookArea.setStoryText(story_text)
            
            # 해당 페이지의 이미지가 있으면 표시
            if self.current_page_idx in self.page_images:
                self.storybookArea.setStoryImage(self.page_images[self.current_page_idx])
            else:
                self.storybookArea.clearImage()
        else:
            self.storybookArea.setStoryText("")
            self.storybookArea.clearImage()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModularMainApp()
    window.show()
    sys.exit(app.exec())