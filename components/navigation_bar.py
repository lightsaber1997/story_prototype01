# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton

class NavigationBar(QFrame):
    # 시그널 정의
    homeClicked = Signal()
    settingsClicked = Signal()
    helpClicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.connectSignals()
    
    def setupUI(self):
        """네비게이션 바 UI 설정"""
        self.setObjectName("navigationBar")
        self.setFixedWidth(180)
        
        # 스타일 설정 - main_ui_colorful.py의 메인 배경색 적용
        self.setStyleSheet("""
            QFrame#navigationBar {
                background-color: #172261;
                padding: 0px;
                margin: 0px;
            }
        """)
        # border-right: 2px solid rgba(255, 255, 255, 0.2);

        
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(15, 30, 15, 30)
        
        # 버튼들 생성
        self.createButtons()
    
    def createButtons(self):
        """네비게이션 버튼들 생성"""
        button_style = """
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: semibold;
                color: white;
                padding: 8px 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        """
        
        # 홈 버튼
        self.btnHome = QPushButton(" Home", self)
        self.btnHome.setObjectName("btnHome")
        self.btnHome.setToolTip("홈")
        self.btnHome.setIcon(QIcon("assets/icon/home.svg"))
        self.btnHome.setIconSize(QSize(22, 22))
        self.btnHome.setStyleSheet(button_style)

        # 새 스토리 버튼
        self.btnNewStory = QPushButton(" New Story", self)
        self.btnNewStory.setObjectName("btnNewStory")
        self.btnNewStory.setToolTip("새 스토리")
        self.btnNewStory.setIcon(QIcon("assets/icon/chat.svg"))
        self.btnNewStory.setIconSize(QSize(22, 22))
        self.btnNewStory.setStyleSheet(button_style)

        # 저장된 스토리 버튼
        self.btnSavedStories = QPushButton(" List", self)
        self.btnSavedStories.setObjectName("btnSavedStories")
        self.btnSavedStories.setToolTip("저장된 스토리")
        self.btnSavedStories.setIcon(QIcon("assets/icon/book.svg"))
        self.btnSavedStories.setIconSize(QSize(22, 22))
        self.btnSavedStories.setStyleSheet(button_style)
        
        # 설정 버튼
        self.btnSettings = QPushButton(" Settings", self)
        self.btnSettings.setObjectName("btnSettings")
        self.btnSettings.setToolTip("설정")
        self.btnSettings.setIcon(QIcon("assets/icon/setting.svg"))
        self.btnSettings.setIconSize(QSize(22, 22))
        self.btnSettings.setStyleSheet(button_style)
        
        # 도움말 버튼
        self.btnHelp = QPushButton(" Help", self)
        self.btnHelp.setObjectName("btnHelp")
        self.btnHelp.setToolTip("도움말")
        self.btnHelp.setIcon(QIcon("assets/icon/help.svg"))
        self.btnHelp.setIconSize(QSize(22, 22))
        self.btnHelp.setStyleSheet(button_style)
        
        
        
        
        
        # 레이아웃에 버튼 추가
        self.layout.addWidget(self.btnHome)
        self.layout.addWidget(self.btnNewStory)
        self.layout.addWidget(self.btnSavedStories)
        self.layout.addStretch()  # 중간에 여백
        self.layout.addWidget(self.btnSettings)
        self.layout.addWidget(self.btnHelp)
    
    def connectSignals(self):
        """시그널 연결"""
        self.btnHome.clicked.connect(self.homeClicked.emit)
        self.btnSettings.clicked.connect(self.settingsClicked.emit)
        self.btnHelp.clicked.connect(self.helpClicked.emit)
    
    def setActiveButton(self, button_name: str):
        """활성 버튼 표시"""
        # 모든 버튼을 기본 상태로 리셋
        buttons = [self.btnHome, self.btnSettings, self.btnHelp, self.btnNewStory, self.btnSavedStories]
        for btn in buttons:
            btn.setProperty("active", False)
        
        # 선택된 버튼을 활성 상태로 설정
        if button_name == "home":
            self.btnHome.setProperty("active", True)
        elif button_name == "settings":
            self.btnSettings.setProperty("active", True)
        elif button_name == "help":
            self.btnHelp.setProperty("active", True)
        elif button_name == "new_story":
            self.btnNewStory.setProperty("active", True)
        elif button_name == "saved_stories":
            self.btnSavedStories.setProperty("active", True)
        
        # 스타일 업데이트
        self.style().unpolish(self)
        self.style().polish(self)