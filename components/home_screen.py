# components/home_screen.py
# -*- coding: utf-8 -*-
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt
    Signal = QtCore.Signal
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore
    from PyQt5.QtCore import Qt  # type: ignore
    Signal = QtCore.pyqtSignal  # type: ignore

import os


class HomeScreen(QtWidgets.QWidget):
    startRequested = Signal()
    openRecentRequested = Signal()
    settingsRequested = Signal()
    tutorialRequested = Signal()

    def __init__(self, logo_path: str = "assets/logo.svg", parent=None):
        super().__init__(parent)
        self.setObjectName("HomeRoot")
        self.setMinimumSize(900, 560)
        self._build_ui(logo_path)
        self._apply_styles()

    # ---------------- UI ----------------
    def _build_ui(self, logo_path: str):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        # 배경을 채우는 컨테이너
        bg = QtWidgets.QWidget(self)
        bg.setObjectName("Background")
        bg_layout = QtWidgets.QVBoxLayout(bg)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        # 중앙 카드
        card = QtWidgets.QFrame(bg)
        card.setObjectName("Card")
        card.setMinimumWidth(560)
        card.setMaximumWidth(720)

        # 그림자
        shadow = QtWidgets.QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 32)
        card_layout.setSpacing(18)

        # 로고
        logo = QtWidgets.QLabel(card, alignment=Qt.AlignCenter)
        if os.path.exists(logo_path):
            pix = QtGui.QPixmap(logo_path)
            if not pix.isNull():
                pix = pix.scaledToWidth(180, Qt.SmoothTransformation)
                logo.setPixmap(pix)
        else:
            logo.setText("MyStoryPal")
            logo.setStyleSheet("font-size:28px; font-weight:700; color:#111827;")
        card_layout.addWidget(logo)

        # 타이틀
        title = QtWidgets.QLabel("Create Your Own Story ✨", card)
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QtWidgets.QLabel("A story studio that automatically generates pictures from a single sentence.", card)
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        # CTA 버튼
        cta = QtWidgets.QPushButton("Let's Start!", card)
        cta.setObjectName("PrimaryButton")
        cta.setMinimumHeight(48)
        cta.setCursor(Qt.PointingHandCursor)
        cta.clicked.connect(self.startRequested.emit)
        card_layout.addWidget(cta)

        # 보조 버튼들
        # extras = QtWidgets.QHBoxLayout()
        # extras.setSpacing(12)
        # extras.setContentsMargins(0, 8, 0, 0)

        # btn_recent = QtWidgets.QPushButton("최근 프로젝트 열기", card)
        # btn_recent.setObjectName("GhostButton")
        # btn_recent.setCursor(Qt.PointingHandCursor)
        # btn_recent.clicked.connect(self.openRecentRequested.emit)

        # btn_settings = QtWidgets.QPushButton("설정", card)
        # btn_settings.setObjectName("GhostButton")
        # btn_settings.setCursor(Qt.PointingHandCursor)
        # btn_settings.clicked.connect(self.settingsRequested.emit)

        # btn_tutorial = QtWidgets.QPushButton("튜토리얼", card)
        # btn_tutorial.setObjectName("GhostButton")
        # btn_tutorial.setCursor(Qt.PointingHandCursor)
        # btn_tutorial.clicked.connect(self.tutorialRequested.emit)

        # extras.addStretch(1)
        # extras.addWidget(btn_recent)
        # extras.addWidget(btn_settings)
        # extras.addWidget(btn_tutorial)
        # extras.addStretch(1)
        # card_layout.addLayout(extras)

        # 푸터 라벨(버전 표기 등)
        footer = QtWidgets.QLabel("v0.9 • Stable Diffusion v1.5 • Phi-3 Mini", card)
        footer.setObjectName("Footer")
        footer.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(footer)

        # 중앙 정렬
        center = QtWidgets.QHBoxLayout()
        center.addStretch(1)
        center.addWidget(card)
        center.addStretch(1)

        # 상하 여백
        bg_layout.addStretch(1)
        bg_layout.addLayout(center)
        bg_layout.addStretch(1)

        root.addWidget(bg)

        # 단축키: Enter → 시작
        cta_shortcut = QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Return), self)
        cta_shortcut.activated.connect(self.startRequested.emit)
        cta_shortcut2 = QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Enter), self)
        cta_shortcut2.activated.connect(self.startRequested.emit)

    # ---------------- Style ----------------
    def _apply_styles(self):
        self.setStyleSheet("""
            #Background {
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:1,
                    stop:0 #e9f2ff, stop:1 #f6f9ff
                );
                background-image: url(assets/space.png);
                background-repeat: repeat;
                background-position: center;
            }
            #HomeRoot {
                background: #f5f7ff;
            }

            /* 중앙 카드 */
            #Card {
                background: #ffffff;
                border-radius: 18px;
                border: 1px solid rgba(17, 24, 39, 0.06);
            }

            /* 타이틀/서브타이틀 */
            #Title {
                font-size: 22px;
                font-weight: 700;
                color: #111827;
                padding-top: 6px;
            }
            #Subtitle {
                font-size: 14px;
                color: #4B5563;
            }

            /* 메인 CTA */
            QPushButton#PrimaryButton {
                margin-top: 10px;
                font-size: 16px; 
                font-weight: 700;
                padding: 12px 20px;
                border-radius: 10px;
                color: white;
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB
                );
                border: 0px;
            }
            QPushButton#PrimaryButton:hover {
            }
            QPushButton#PrimaryButton:pressed {
                transform: translateY(1px);
            }

            /* 보조 버튼 */
            QPushButton#GhostButton {
                font-size: 13px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 8px;
                color: #1F2937;
                background: rgba(31, 41, 55, 0.06);
                border: 1px solid rgba(31, 41, 55, 0.08);
            }
            QPushButton#GhostButton:hover {
                background: rgba(31, 41, 55, 0.1);
            }
            QPushButton#GhostButton:pressed {
                background: rgba(31, 41, 55, 0.14);
            }

            /* 푸터 */
            #Footer {
                margin-top: 6px;
                color: #6B7280;
                font-size: 12px;
            }
        """)
