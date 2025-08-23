# components/home_screen.py
# -*- coding: utf-8 -*-
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, QSignalBlocker, QPoint, QTimer
    from PySide6.QtGui import QPalette, QBrush, QColor, QPainter
    from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QHBoxLayout, QWidget
    Signal = QtCore.Signal
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore
    from PyQt5.QtCore import Qt, QPoint, QTimer  # type: ignore
    from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QHBoxLayout, QWidget # type: ignore
    Signal = QtCore.pyqtSignal  # type: ignore

import os
from components.image_upload_dialog import ImageUploadDialog

class HomeScreen(QtWidgets.QWidget):
    startRequested = Signal()
    openRecentRequested = Signal()
    settingsRequested = Signal()
    tutorialRequested = Signal()
    imageUploaded = Signal(str) #str: Image Path

    def __init__(self, logo_path: str = "assets/logo.svg", parent=None):
        super().__init__(parent)
        self.setObjectName("HomeRoot")
        self.setMinimumSize(900, 560)
        self._build_ui(logo_path)
        self._apply_styles()

    # ---------------- UI ----------------
    def _build_ui(self, logo_path: str):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 배경을 채우는 컨테이너
        bg = QtWidgets.QWidget(self)
        bg.setObjectName("Background")
        bg_layout = QtWidgets.QVBoxLayout(bg)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        # 별똥별 오버레이
        self.star_overlay = StarOverlay(bg)
        self.star_overlay.lower()  # 기본은 Card보다 밑, 필요하면 raise 조정
        self.star_overlay.resize(bg.size())
        bg.resizeEvent = lambda e: self.star_overlay.resize(bg.size())

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
        cta = QtWidgets.QPushButton("Start with my Image!", card)
        cta.setObjectName("PrimaryButton")
        cta.setMinimumHeight(48)
        cta.setCursor(Qt.PointingHandCursor)
        # cta.clicked.connect(self.startRequested.emit)
        cta.clicked.connect(self._onUploadClicked)
        card_layout.addWidget(cta)

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

    # Upload Image
    def _onUploadClicked(self):
        # 파일 경로 직접 넣는 버전
        # file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        #     self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        # )
        # if file_path:
        #     self.imageUploaded.emit(file_path)
        dialog = ImageUploadDialog(self)
        dialog.fileSelected.connect(self.imageUploaded.emit)
        dialog.exec()
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

class StarOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.stars = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self.spawn_star)
        self.spawn_timer.start(1800)  # 듬성듬성 (1.8초 간격)

    def spawn_star(self):
        import random
        size = random.uniform(1.0, 1.6)  # 작은 별
        # 출발 위치: 윗변 전체 + 좌측 일부
        if random.random() < 0.5:
            x = random.randint(0, self.width())
            y = -20
        else:
            x = -20
            y = random.randint(0, self.height() // 2)

        self.stars.append({
            'x': float(x), 'y': float(y),
            'vx': 4.0, 'vy': 4.0,   # 방향 고정 (↘)
            'size': size, 'opacity': 1.0,
            'length': 120
        })

    def animate(self):
        for star in self.stars[:]:
            star['x'] += star['vx']
            star['y'] += star['vy']
            star['opacity'] -= 0.01

            if (star['x'] > self.width() + 50 or
                star['y'] > self.height() + 50 or
                star['opacity'] <= 0):
                self.stars.remove(star)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for star in self.stars:
            head_x, head_y = int(star['x']), int(star['y'])
            tail_x = head_x - int(star['vx'] * star['length'])
            tail_y = head_y - int(star['vy'] * star['length'])

            # 꼬리: 머리쪽 두껍고 뒤로 갈수록 얇아짐
            grad = QtGui.QLinearGradient(tail_x, tail_y, head_x, head_y)
            grad.setColorAt(0.0, QColor(255, 255, 255, 0))   # 꼬리 끝 투명
            grad.setColorAt(1.0, QColor(255, 255, 255, int(star['opacity'] * 200)))

            # 머리쪽 두껍고, 꼬리쪽 얇게 (펜 두께 조절)
            pen = QtGui.QPen(QBrush(grad), star['size'] * 2.5, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(tail_x, tail_y, head_x, head_y)

            # 별(머리)
            painter.setBrush(QColor(255, 255, 255, int(star['opacity'] * 255)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(head_x - int(star['size']/2),
                                head_y - int(star['size']/2),
                                int(star['size']),
                                int(star['size']))
