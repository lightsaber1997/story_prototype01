# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFileDialog)
from pathlib import Path
from components.fx.typewriter_effect import TypewriterEffect
from tts.voice_type import VoiceType
from tts.tts_controller import TTSController
from utils.export_pdf import export_storybook
from datetime import datetime

class StorybookArea(QFrame):
    # 시그널 정의
    pageChanged = Signal(int)  # 페이지 변경 시그널
    storySaved = Signal()      # 스토리 저장 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.total_pages = 1
        # Typewriter
        self._typer = TypewriterEffect(self)
        self._page_texts: dict[int, str] = {}
        self.typing_animated = True
        self.typing_interval = 30
        self.typing_by_word = False
        # TTS
        self.tts_rate = 160
        self.tts_mode = VoiceType.AMERICAN_WOMAN
        self.tts_controller = TTSController(self)

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
                background: #ffffff;
                background-image: url(assets/paper.jpg);
                background-repeat: repeat;
                background-position: center;
                border-left: 2px solid rgba(200, 200, 200, 0.3);
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        # self.layout.setSpacing(20)
        self.layout.setContentsMargins(25, 25, 25, 25)
        
        # UI 컴포넌트들 생성
        self.createComponents()
    
    def createComponents(self):
        """스토리북 영역 컴포넌트들 생성"""
        # 스토리북 제목
        self.storybookTitle = QLabel("CHAPTER 1", self)
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
                background: transparent;
                color: #7f8c8d;
                font-size: 14px;
                font-style: italic;
                margin: 0px 20px;
            }
        """)
        
        # 텍스트 영역 (스크롤 가능)
        self.createTextArea()
        
        # 페이지 네비게이션
        self.createBookPageNavigation()
        
        # 레이아웃에 컴포넌트 추가
        self.layout.addWidget(self.storybookTitle)
        self.layout.addWidget(self.imageArea)
        self.layout.addWidget(self.textScrollArea, 1)
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
        self.btnPrevPage.setCursor(Qt.PointingHandCursor)

        
        # 다음 페이지 버튼
        self.btnNextPage = QPushButton("▶", self.pageNavFrame)
        self.btnNextPage.setObjectName("btnNextPage")
        self.btnNextPage.setFixedSize(45, 45)
        self.btnNextPage.setToolTip("다음 페이지")
        self.btnNextPage.setCursor(Qt.PointingHandCursor)

        
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
        self.textScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textScrollArea.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
                margin: 0px 20px;
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
        
        # 텍스트 폰트 
        font_content = QFont()
        font_content.setFamilies(["Georgia", "Times New Roman", "serif"])  
        font_content.setPointSize(self._get_relative_font_size(18))  
        self.textContent.setFont(font_content)
        self.textContent.setStyleSheet("""
            QLabel {
                color: #2A2935;
                padding: 30px 40px;
                line-height: 1.7;
                background: transparent;
                text-align: justify;
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 18px;
            }
        """)
        
        self.textScrollArea.setWidget(self.textContent)
    
    def createBookPageNavigation(self):
        """페이지 네비게이션 생성"""
        self.pageNavFrame = QFrame(self)
        self.pageNavFrame.setObjectName("pageNavFrame")
        self.pageNavFrame.setFixedHeight(60)
        self.pageNavLayout = QHBoxLayout(self.pageNavFrame)
        self.pageNavLayout.setContentsMargins(40, 15, 40, 15)
        self.pageNavLayout.setSpacing(20)

        # 통일된 아이콘/버튼 박스 크기
        ICON_SIZE = 22
        ICON_PAD  = 6
        BOX = ICON_SIZE + ICON_PAD * 2
        
        # 이전 페이지 버튼
        self.btnPrevPage = QPushButton("‹", self.pageNavFrame)
        self.btnPrevPage.setObjectName("btnPrevPage")
        # self.btnPrevPage.setFixedSize(34, 34)
        self.btnPrevPage.setFixedSize(BOX, BOX)
        self.btnPrevPage.setToolTip("이전 페이지")

        # Read Aloud Button (🔊)
        self.btnReadAloud = QPushButton("", self.pageNavFrame)
        self.btnReadAloud.setObjectName("btnReadAloud")
        self._setReadAloudIdleIcon()
        # self.btnReadAloud.setFixedSize(34, 34)
        self.btnReadAloud.setToolTip("텍스트 읽어주기")
        self.btnReadAloud.setCursor(Qt.PointingHandCursor)


        # 다음 페이지 버튼
        self.btnNextPage = QPushButton("›", self.pageNavFrame)
        self.btnNextPage.setObjectName("btnNextPage")
        # self.btnNextPage.setFixedSize(34, 34)
        self.btnNextPage.setFixedSize(BOX, BOX)
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

        self.btnExportPDF = QPushButton("Export", self.pageNavFrame)
        self.btnExportPDF.setObjectName("btnExportPDF")
        icon_dir = Path("assets/icon")
        pdf_normal = icon_dir / "export_light.svg"
        pdf_hover  = icon_dir / "export_strong.svg"
        self._applySvgIconButton(self.btnExportPDF, str(pdf_normal), str(pdf_hover), size=22, padding=6)
        self.btnExportPDF.setToolTip("Export storybook as PDF")
        self.pageNavLayout.addWidget(self.btnExportPDF)
        self.btnExportPDF.setCursor(Qt.PointingHandCursor)
        


    

    
    def connectSignals(self):
        """시그널 연결"""
        self.btnPrevPage.clicked.connect(self.previousPage)
        self.btnNextPage.clicked.connect(self.nextPage)
        self.btnReadAloud.clicked.connect(self.readAloud)
        self.tts_controller.worker.started.connect(self._onTTSStarted)
        self.tts_controller.worker.finished.connect(self._onTTSFinished)
        self.tts_controller.worker.error.connect(self._onTTSError)
        self.btnExportPDF.clicked.connect(self.saveAllPagesAsPDF)




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

    def setStoryText(self, new_text: str, *, page: int, animated: bool):
        old_text = self._page_texts.get(page, "")
        print(f"[setStoryText] page={page}, animated={animated}, typing_animated={self.typing_animated}")
        print(f"  old_text(len={len(old_text)}): {repr(old_text[:30])}...")
        print(f"  new_text(len={len(new_text)}): {repr(new_text[:30])}...")

        # 캐시에 저장
        self._page_texts[page] = new_text
        print(f"[setStoryText] 캐시 저장 완료 (page={page}, len={len(new_text)})\n")
        
        if not self.typing_animated:
            # 1) 사용자 설정에서 타자기 효과 꺼짐 → 즉시 표시
            print("→ 조건1: typing_animated=False → 즉시 표시")
            if hasattr(self._typer, "stop"):
                self._typer.stop()
            self.textContent.setText(new_text)

        elif not animated:
            # 2) 페이지 이동/복원 → 무조건 즉시 표시
            print("→ 조건2: animated=False (페이지 이동) → 즉시 표시")
            if hasattr(self._typer, "stop"):
                self._typer.stop()
            self.textContent.setText(new_text)

        else:
            # 3) animated=True & typing_animated=True → 타자기 효과
            is_prefix_grow = new_text.startswith(old_text)
            print(f"→ 조건3: animated=True & typing_animated=True, is_prefix_grow={is_prefix_grow}")

            if not old_text or not is_prefix_grow:
                print("   → 하위조건3a: 새 타자기 시작")
                if hasattr(self._typer, "stop"):
                    self._typer.stop()
                if hasattr(self, "textScrollArea"):
                    bar = self.textScrollArea.verticalScrollBar()
                    bar.setValue(bar.minimum())

                self._typer.start(
                    label=self.textContent,
                    text=new_text,
                    base_interval=self.typing_interval,
                    by_word=self.typing_by_word
                )
            else:
                print("   → 하위조건3b: 증분 update")
                self._typer.update(new_text)

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
            if hasattr(self, "_typer"):
                self._typer.stop()
            self.stopTTS()
            self.current_page -= 1
            self.updatePageDisplay()
            self.pageChanged.emit(self.current_page)
    
    def nextPage(self):
        """다음 페이지로 이동"""
        if self.current_page < self.total_pages - 1:
            if hasattr(self, "_typer"):
                self._typer.stop()
            self.stopTTS()
            self.current_page += 1
            self.updatePageDisplay()
            self.pageChanged.emit(self.current_page)
    
    def updatePageDisplay(self):
        """페이지 표시 업데이트"""
        self.pageNumber.setText(str(self.current_page + 1))
        # Chapter 제목 업데이트
        self.storybookTitle.setText(f"CHAPTER {self.current_page + 1}")
    
        # 버튼 활성화/비활성화
        self.btnPrevPage.setEnabled(self.current_page > 0)
        self.btnNextPage.setEnabled(self.current_page < self.total_pages - 1)
    
    def getCurrentPage(self):
        """현재 페이지 번호 반환"""
        return self.current_page
    
    def getTotalPages(self):
        """총 페이지 수 반환"""
        return self.total_pages

    def getStoryText(self) -> str:
        """Return the current story text"""
        return self.textContent.text()
    
    def applyTTSSettings(self, rate: int, mode: VoiceType):
        """Apply TTS settings from the settings dialog"""
        self.tts_rate = rate
        self.tts_mode = mode

    def applyTypewriterSettings(self, animated: bool, interval: int, by_word: bool):
        """Apply typewriter effect settings (animation, interval, by word/character)"""
        self.typing_animated = animated
        self.typing_interval = interval
        self.typing_by_word = by_word


    def _applySvgIconButton(self, btn: QPushButton, normal_svg: str, hover_svg: str, *, size: int = 22, padding: int = 6):
        """
            QPushButton에 SVG 아이콘을 배경으로 깔고, hover시 다른 SVG로 바꿔주는 스타일을 적용.
            버튼 텍스트/아이콘은 비워두고 background-image만 사용.
        """
        btn.setText("")
        btn.setIcon(QIcon()) 
        btn.setCursor(Qt.PointingHandCursor)
        # box = size + padding * 2
        box=34
        btn.setFixedSize(box, box)

        obj = btn.objectName()
        btn.setStyleSheet(f"""
            QPushButton#{obj} {{
                background: transparent;
                border: none;
                padding: {padding}px;
                background-image: url({normal_svg});
                background-repeat: no-repeat;
                background-position: center;
                border-radius: {max(6, padding)}px;
            }}
            QPushButton#{obj}:hover {{
                background-image: url({hover_svg});
                background-color: rgba(42, 41, 53, 0.08);
            }}
            QPushButton#{obj}:pressed {{
                background-color: rgba(42, 41, 53, 0.16);
            }}
            QPushButton#{obj}:disabled {{
                background-image: url({normal_svg});
                opacity: 0.45;
            }}
        """)

    def _setReadAloudIdleIcon(self):
        icon_dir = Path("assets/icon")
        normal = icon_dir / "speaker_light.svg"
        hover  = icon_dir / "speaker_strong.svg"
        self._applySvgIconButton(self.btnReadAloud, str(normal), str(hover), size=22, padding=6)
        self.btnReadAloud.setToolTip("텍스트 읽어주기")

    def _setReadAloudStopIcon(self):
        icon_dir = Path("assets/icon")
        normal = icon_dir / "speaker_strong.svg"
        hover  = icon_dir / "speaker_light.svg"
        self._applySvgIconButton(self.btnReadAloud, str(normal), str(hover), size=22, padding=6)
        self.btnReadAloud.setToolTip("읽기 중지")

    def readAloud(self):
        """Toggle TTS playback for the current text"""
        if self.tts_controller.is_running():
            # If already running, stop playback
            self.stopTTS()
            return

        # Retrieve text either from QTextEdit (toPlainText) or QLabel (text)
        getter = getattr(self.textContent, "toPlainText", None)
        text = (getter() if callable(getter) else self.textContent.text()).strip()
        if not text:
            print("[StorybookArea] No text to read.")
            return

        # Start playback with current TTS settings
        self.tts_controller.start(text, self.tts_mode, self.tts_rate)

    def stopTTS(self):
        """Stop TTS playback"""
        self.tts_controller.stop()
        # Button UI reset is handled in the finished event

    def _onTTSStarted(self):
        """Update button when TTS playback starts"""
        # self.btnReadAloud.setText("⏹")
        # self.btnReadAloud.setToolTip("Stop reading")
        self._setReadAloudIdleIcon()

    def _onTTSFinished(self):
        """Update button when TTS playback finishes"""
        # self.btnReadAloud.setText("🔊")
        # self.btnReadAloud.setToolTip("Read text aloud")
        self._setReadAloudStopIcon()

    def _onTTSError(self, message: str):
        """Handle TTS errors and reset button state"""
        print(f"[StorybookArea] TTS error: {message}")
        # self.btnReadAloud.setText("🔊")
        # self.btnReadAloud.setToolTip("Read text aloud")
        self._setReadAloudIdleIcon()

    def saveAllPagesAsPDF(self):
        """Open save dialog and export all pages into a single PDF (with images + text)."""
        # 현재 날짜/시간을 파일명에 반영
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_name = f"storybook_{timestamp}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            default_name,  # 기본 파일명에 날짜/시간 포함
            "PDF Files (*.pdf)"
        )
        if not filename:
            return
        export_storybook(self, filename)