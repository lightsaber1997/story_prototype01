# main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from app.pages.start_page_widget import StartPageWidget
from app.pages.writing_page_widget import WritingPageWidget
from app.core.llm_factory import get_llm_engine
from stable_engine import StableV15Engine
from app.core.app_state import AppState

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 공용 상태 및 엔진 초기화
        self.app_state = AppState()
        # QStackedWidget: 페이지 스위칭 컨테이너
        self.stack = QStackedWidget()

        self.llm_engine = get_llm_engine()
        self.image_gen_engine = StableV15Engine()

        # 페이지 생성
        self.start_page_widget = StartPageWidget(self.stack, self.app_state)
        self.writing_page_widget = WritingPageWidget(
            stacked_widget=self.stack,
            llm_engine=self.llm_engine,
            image_gen_engine=self.image_gen_engine,
            app_state=self.app_state
        )

        # 페이지 등록
        self.stack.addWidget(self.start_page_widget)         # index 0
        self.stack.addWidget(self.writing_page_widget) # index 1
        self.stack.setCurrentIndex(0)  # 시작 페이지부터

        # 중앙 위젯 설정
        self.setCentralWidget(self.stack)

    def _on_image_gen_ready(self, payload: dict):
        pass  # Optional: 이미지 생성 완료 핸들러
