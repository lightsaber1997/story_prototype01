# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea)
from pathlib import Path

class StorybookArea(QFrame):
    # 시그널 정의
    pageChanged = Signal(int)  # 페이지 변경 시그널
    storySaved = Signal()      # 스토리 저장 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.total_pages = 1
        self.setupUI()
        self.connectSignals()
    
    def _get_relative_font_size(self, base_size):
        """DPI에 따른 상대적 폰트 크기 계산"""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            dpi_ratio = screen.logicalDotsPerInch() / 96.0
            return max(8, int(base_size * min(dpi_ratio, 1.5)))
        return base_size
    
    def setupUI(self):
        """스토리북 영역 UI 설정"""
        self.setObjectName("storybookArea")
        
        self.setStyleSheet("""
            QFrame#storybookArea {
                background: #F5F5F5;
                background-image: linear-gradient(90deg, rgba(227,227,227,1) 0%, rgba(247,247,247,0) 18%);
                border-left: 2px solid rgba(200, 200, 200, 0.3);
                padding: 0px;
                margin: 0px;
                box-shadow: 0 0 50px rgba(0, 0, 0, 0.2);
            }
        """)
        
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(25, 25, 25, 25)
        
        # UI 컴포넌트들 생성
        self.createComponents()
    
    def createComponents(self):
        """스토리북 영역 컴포넌트들 생성"""
        # 스토리북 제목
        self.storybookTitle = QLabel("MyStoryPal", self)
        self.storybookTitle.setObjectName("storybookTitle")
        
        font_title = QFont()
        font_title.setFamilies(["Georgia", "Times New Roman", "serif"])  # 책 스타일 폰트
        font_title.setPointSize(self._get_relative_font_size(28))
        font_title.setBold(True)
        self.storybookTitle.setFont(font_title)
        self.storybookTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.storybookTitle.setStyleSheet("""
            QLabel {
                color: #2A2935;
                padding: 30px 20px 20px 20px;
                background: transparent;
                border: none;
                margin-bottom: 10px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 3px;
            }
        """)
        
        # 이미지 영역
        self.imageArea = QLabel(self)
        self.imageArea.setObjectName("imageArea")
        self.imageArea.setFixedHeight(320)
        self.imageArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageArea.setText("")
        
        font_placeholder = QFont()
        font_placeholder.setFamilies(["Georgia", "Times New Roman", "serif"])
        font_placeholder.setPointSize(self._get_relative_font_size(14))
        font_placeholder.setItalic(True)
        self.imageArea.setFont(font_placeholder)
        
        self.imageArea.setStyleSheet("""
            QLabel {
                background: #FAFAFA;
                border: 1px solid rgba(200, 200, 200, 0.4);
                color: #7f8c8d;
                font-size: 14px;
                font-style: italic;
                margin: 10px 20px;
            }
        """)
        
        # 텍스트 영역 (스크롤 가능)
        self.createTextArea()
        
        # 페이지 네비게이션 (책 스타일)
        self.createBookPageNavigation()
        
        # 레이아웃에 컴포넌트 추가
        self.layout.addWidget(self.storybookTitle)
        self.layout.addWidget(self.imageArea)
        self.layout.addWidget(self.textScrollArea, 1)  # 확장 가능
        self.layout.addWidget(self.pageNavFrame)
    
    def createPageNavigation(self):
        """페이지 네비게이션 생성"""
        self.pageNavFrame = QFrame(self)
        self.pageNavFrame.setObjectName("pageNavFrame")
        self.pageNavLayout = QHBoxLayout(self.pageNavFrame)
        self.pageNavLayout.setContentsMargins(0, 10, 0, 10)
        
        # 이전 페이지 버튼
        self.btnPrevPage = QPushButton("◀", self.pageNavFrame)
        self.btnPrevPage.setObjectName("btnPrevPage")
        self.btnPrevPage.setFixedSize(45, 45)
        self.btnPrevPage.setToolTip("이전 페이지")
        
        # 다음 페이지 버튼
        self.btnNextPage = QPushButton("▶", self.pageNavFrame)
        self.btnNextPage.setObjectName("btnNextPage")
        self.btnNextPage.setFixedSize(45, 45)
        self.btnNextPage.setToolTip("다음 페이지")
        
        # 페이지 라벨
        self.pageLabel = QLabel("1 / 1", self.pageNavFrame)
        self.pageLabel.setObjectName("pageLabel")
        self.pageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font_page = QFont()
        font_page.setFamilies(["Pretendard", "Arial"])
        font_page.setPointSize(self._get_relative_font_size(14))
        font_page.setBold(True)
        self.pageLabel.setFont(font_page)
        
        # 네비게이션 버튼
        nav_font = QFont()
        nav_font.setFamilies(["Georgia", "Times New Roman", "serif"])
        nav_font.setPointSize(self._get_relative_font_size(16))
        self.btnPrevPage.setFont(nav_font)
        self.btnNextPage.setFont(nav_font)
        
        # 버튼 스타일
        nav_button_style = """
            QPushButton {
                background: transparent;
                border: 1px solid rgba(42, 41, 53, 0.3);
                font-size: 16px;
                font-weight: normal;
                color: #2A2935;
            }
            QPushButton:hover {
                background: rgba(42, 41, 53, 0.1);
                border-color: rgba(42, 41, 53, 0.5);
            }
            QPushButton:pressed {
                background: rgba(42, 41, 53, 0.2);
            }
            QPushButton:disabled {
                background: transparent;
                border-color: rgba(200, 200, 200, 0.3);
                color: #bdc3c7;
            }
        """
        
        self.btnPrevPage.setStyleSheet(nav_button_style)
        self.btnNextPage.setStyleSheet(nav_button_style)
        
        # 페이지 라벨 
        font_page = QFont()
        font_page.setFamilies(["Georgia", "Times New Roman", "serif"])
        font_page.setPointSize(self._get_relative_font_size(12))
        font_page.setBold(False)
        self.pageLabel.setFont(font_page)
        
        self.pageLabel.setStyleSheet("""
            QLabel {
                color: #2A2935;
                padding: 8px 16px;
                background: transparent;
                border: 1px solid rgba(42, 41, 53, 0.2);
                font-weight: normal;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        
        # 레이아웃에 추가
        self.pageNavLayout.addWidget(self.btnPrevPage)
        self.pageNavLayout.addStretch()
        self.pageNavLayout.addWidget(self.pageLabel)
        self.pageNavLayout.addStretch()
        self.pageNavLayout.addWidget(self.btnNextPage)
    
    def createTextArea(self):
        """텍스트 영역 생성"""
        self.textScrollArea = QScrollArea(self)
        self.textScrollArea.setObjectName("textScrollArea")
        self.textScrollArea.setWidgetResizable(True)
        self.textScrollArea.setStyleSheet("""
            QScrollArea {
                background: #FAFAFA;
                border: none;
                margin: 10px 20px;
            }
            QScrollBar:vertical {
                background: rgba(200, 200, 200, 0.2);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(42, 41, 53, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(42, 41, 53, 0.5);
            }
        """)
        
        self.textContent = QLabel()
        self.textContent.setObjectName("textContent")
        self.textContent.setWordWrap(True)
        self.textContent.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.textContent.setText("")
        
        # 책 스타일 텍스트 폰트 및 스타일
        font_content = QFont()
        font_content.setFamilies(["Georgia", "Times New Roman", "serif"])  
        font_content.setPointSize(self._get_relative_font_size(18))  
        self.textContent.setFont(font_content)
        self.textContent.setStyleSheet("""
            QLabel {
                color: #2A2935;
                padding: 30px 40px;
                line-height: 1.7;
                background: #FAFAFA;
                text-align: justify;
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 18px;
            }
        """)
        
        self.textScrollArea.setWidget(self.textContent)
    
    def createBookPageNavigation(self):
        """책 스타일의 페이지 네비게이션 생성"""
        self.pageNavFrame = QFrame(self)
        self.pageNavFrame.setObjectName("pageNavFrame")
        self.pageNavFrame.setFixedHeight(60)
        self.pageNavLayout = QHBoxLayout(self.pageNavFrame)
        self.pageNavLayout.setContentsMargins(40, 15, 40, 15)
        self.pageNavLayout.setSpacing(20)
        
        # 이전 페이지 버튼
        self.btnPrevPage = QPushButton("‹", self.pageNavFrame)
        self.btnPrevPage.setObjectName("btnPrevPage")
        self.btnPrevPage.setFixedSize(35, 35)
        self.btnPrevPage.setToolTip("이전 페이지")
        
        # 다음 페이지 버튼
        self.btnNextPage = QPushButton("›", self.pageNavFrame)
        self.btnNextPage.setObjectName("btnNextPage")
        self.btnNextPage.setFixedSize(35, 35)
        self.btnNextPage.setToolTip("다음 페이지")
        
        # 페이지 번호 표시
        self.pageNumber = QLabel("1", self.pageNavFrame)
        self.pageNumber.setObjectName("pageNumber")
        self.pageNumber.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pageNumber.setFixedWidth(40)
        
        # 버튼 폰트 설정
        nav_font = QFont()
        nav_font.setFamilies(["Georgia", "Times New Roman", "serif"])
        nav_font.setPointSize(self._get_relative_font_size(18))
        nav_font.setBold(False)
        self.btnPrevPage.setFont(nav_font)
        self.btnNextPage.setFont(nav_font)
        
        # 페이지 번호 폰트 설정
        page_font = QFont()
        page_font.setFamilies(["Georgia", "Times New Roman", "serif"])
        page_font.setPointSize(self._get_relative_font_size(12))
        page_font.setBold(False)
        self.pageNumber.setFont(page_font)
        
        # 버튼 스타일
        nav_button_style = """
            QPushButton {
                background: transparent;
                border: none;
                color: #2A2935;
                font-size: 18px;
                font-weight: normal;
                border-radius: 17px;
            }
            QPushButton:hover {
                background: rgba(42, 41, 53, 0.1);
                color: #1A1925;
            }
            QPushButton:pressed {
                background: rgba(42, 41, 53, 0.2);
                transform: scale(0.95);
            }
            QPushButton:disabled {
                color: rgba(42, 41, 53, 0.3);
                background: transparent;
            }
        """
        
        self.btnPrevPage.setStyleSheet(nav_button_style)
        self.btnNextPage.setStyleSheet(nav_button_style)
        
        # 페이지 번호 스타일
        self.pageNumber.setStyleSheet("""
            QLabel {
                color: #2A2935;
                background: transparent;
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        # 레이아웃에 추가 - 중앙 정렬
        self.pageNavLayout.addStretch()
        self.pageNavLayout.addWidget(self.btnPrevPage)
        self.pageNavLayout.addWidget(self.pageNumber)
        self.pageNavLayout.addWidget(self.btnNextPage)
        self.pageNavLayout.addStretch()
    

    
    def connectSignals(self):
        """시그널 연결"""
        self.btnPrevPage.clicked.connect(self.previousPage)
        self.btnNextPage.clicked.connect(self.nextPage)
    

    
    def setPageCount(self, total_pages: int):
        """총 페이지 수 설정"""
        self.total_pages = max(1, total_pages)
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1
        self.updatePageDisplay()
    
    def setCurrentPage(self, page: int):
        """현재 페이지 설정"""
        if 0 <= page < self.total_pages:
            self.current_page = page
            self.updatePageDisplay()
            self.pageChanged.emit(self.current_page)
    
    def setStoryText(self, text: str):
        """스토리 텍스트 설정"""
        self.textContent.setText(text)
    
    def setStoryImage(self, image_path: str):
        """스토리 이미지 설정"""
        try:
            if Path(image_path).exists():
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.imageArea.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.imageArea.setPixmap(scaled_pixmap)
                    print(f"스토리북에 이미지 표시 완료: {image_path}")
                else:
                    print(f"이미지 로드 실패: {image_path}")
                    self.clearImage()
            else:
                print(f"이미지 파일이 존재하지 않음: {image_path}")
                self.clearImage()
        except Exception as e:
            print(f"이미지 표시 중 오류 발생: {e}")
            self.clearImage()
    
    def clearImage(self):
        """이미지 지우기"""
        self.imageArea.clear()
        self.imageArea.setText("")
    
    def previousPage(self):
        """이전 페이지로 이동"""
        if self.current_page > 0:
            self.current_page -= 1
            self.updatePageDisplay()
            self.pageChanged.emit(self.current_page)
    
    def nextPage(self):
        """다음 페이지로 이동"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.updatePageDisplay()
            self.pageChanged.emit(self.current_page)
    
    def updatePageDisplay(self):
        """페이지 표시 업데이트"""
        self.pageNumber.setText(str(self.current_page + 1))
        
        # 버튼 활성화/비활성화
        self.btnPrevPage.setEnabled(self.current_page > 0)
        self.btnNextPage.setEnabled(self.current_page < self.total_pages - 1)
    
    def setPageCount(self, total_pages: int):
        """총 페이지 수 설정"""
        self.total_pages = max(1, total_pages)
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1
        self.updatePageDisplay()
    
    def setCurrentPage(self, page: int):
        """현재 페이지 설정"""
        if 0 <= page < self.total_pages:
            self.current_page = page
            self.updatePageDisplay()
            self.pageChanged.emit(self.current_page)
    
    def getCurrentPage(self):
        """현재 페이지 번호 반환"""
        return self.current_page
    
    def getTotalPages(self):
        """총 페이지 수 반환"""
        return self.total_pages