from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class Ui_StartWidget:
    def setupUi(self, StartWidget):
        StartWidget.setObjectName("StartWidget")
        StartWidget.setWindowTitle("MyStoryPal")

        # StartWidget에 메인 레이아웃을 직접 연결
        self.root_layout = QVBoxLayout(StartWidget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 배경을 담을 컨테이너 위젯 복원 (반응형으로 확장)
        self.background_container = QWidget()
        self.background_container.setObjectName("background_container")

        # 메인 레이아웃 (background_container에 연결)
        self.main_layout = QVBoxLayout(self.background_container)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # 타이틀
        self.title_label = QLabel("MyStoryPal")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignCenter)

        # 서브타이틀
        self.subtitle_label = QLabel("start your story by...")
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        # 버튼 컨테이너
        self.button_container = QWidget()
        self.button_container.setObjectName("button_container")
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setSpacing(20)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        # 텍스팅 버튼
        self.texting_btn = QPushButton("✏️ texting!")
        self.texting_btn.setObjectName("texting_btn")
        self.texting_btn.setFixedHeight(60)

        # 이미지 업로드 버튼
        self.upload_btn = QPushButton("🖼️ upload image")
        self.upload_btn.setObjectName("upload_btn")
        self.upload_btn.setFixedHeight(60)

        # 하단 마법 요소
        self.magic_footer = QLabel("✨ Create magical stories together ✨")
        self.magic_footer.setObjectName("magic_footer")
        self.magic_footer.setAlignment(Qt.AlignCenter)

        # 레이아웃에 위젯 추가 (비율로 공간 분할)
        self.main_layout.addWidget(self.title_label, 1)
        self.main_layout.addWidget(self.subtitle_label, 1)
        self.main_layout.addStretch(1)

        self.button_layout.addWidget(self.texting_btn)
        self.button_layout.addWidget(self.upload_btn)

        # 버튼 컨테이너를 QHBoxLayout에 추가하여 가운데 정렬
        self.button_wrapper_layout = QHBoxLayout()
        self.button_wrapper_layout.addStretch(1)
        self.button_wrapper_layout.addWidget(self.button_container, 2)
        self.button_wrapper_layout.addStretch(1)

        self.main_layout.addLayout(self.button_wrapper_layout, 2)
        self.main_layout.addStretch(2)
        self.main_layout.addWidget(self.magic_footer, 1)

        # root_layout에 background_container 추가
        self.root_layout.addWidget(self.background_container)

        # 스타일 적용
        self.setup_styles(StartWidget)

        # 마법 같은 그림자 효과
        self.setup_effects()

    def setup_styles(self, StartWidget):
        """스타일 설정"""
        # StartWidget 자체는 투명하게 유지
        StartWidget.setStyleSheet("QWidget#StartWidget { background: transparent; }")

        # background_container에만 배경색 적용
        self.background_container.setStyleSheet("""
            QWidget#background_container {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #FFF8DC, stop: 0.3 #FFFACD, 
                                          stop: 0.7 #F5DEB3, stop: 1 #DEB887);
            }
        """)

        # ... (이하 스타일 코드는 원본과 동일) ...

        # 타이틀 스타일
        self.title_label.setStyleSheet("""
            QLabel#title_label {
                font-size: 42px;
                font-weight: bold;
                color: #8B4513;
                margin-bottom: 10px;
                font-family: 'Georgia', serif;
            }
        """)

        # 서브타이틀 스타일
        self.subtitle_label.setStyleSheet("""
            QLabel#subtitle_label {
                font-size: 18px;
                color: #A0522D;
                margin-bottom: 30px;
                font-family: 'Georgia', serif;
            }
        """)

        # 텍스팅 버튼 스타일
        self.texting_btn.setStyleSheet("""
            QPushButton#texting_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #FFE4B5, stop: 1 #DEB887);
                border: 3px solid #CD853F;
                border-radius: 30px;
                font-size: 18px;
                font-weight: bold;
                color: #8B4513;
                font-family: 'Georgia', serif;
                padding: 0 20px;
            }
            QPushButton#texting_btn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #F5DEB3, stop: 1 #D2B48C);
                border: 3px solid #A0522D;
            }
            QPushButton#texting_btn:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #DEB887, stop: 1 #CD853F);
            }
        """)

        # 업로드 버튼 스타일
        self.upload_btn.setStyleSheet("""
            QPushButton#upload_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #E6F3FF, stop: 1 #B0C4DE);
                border: 3px solid #4682B4;
                border-radius: 30px;
                font-size: 18px;
                font-weight: bold;
                color: #2F4F4F;
                font-family: 'Georgia', serif;
                padding: 0 20px;
            }
            QPushButton#upload_btn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #F0F8FF, stop: 1 #87CEEB);
                border: 3px solid #5F9EA0;
            }
            QPushButton#upload_btn:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #B0C4DE, stop: 1 #4682B4);
            }
        """)

        # 푸터 스타일
        self.magic_footer.setStyleSheet("""
            QLabel#magic_footer {
                font-size: 14px;
                color: #DAA520;
                font-style: italic;
                margin-top: 20px;
                font-family: 'Georgia', serif;
            }
        """)

    def setup_effects(self):
        """그래픽 효과 설정"""
        # 마법 같은 그림자 효과
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(139, 69, 19, 80))
        self.title_label.setGraphicsEffect(shadow)