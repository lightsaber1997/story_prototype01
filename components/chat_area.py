# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton,
    QListWidgetItem, QStyledItemDelegate, QGraphicsDropShadowEffect,
    QHBoxLayout, QWidget, QSizePolicy
)
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

class ChatMessageDelegate(QStyledItemDelegate): 
    def paint(self, painter, option, index):
        from PySide6.QtGui import QFont, QFontMetrics
        from PySide6.QtCore import QRect
        painter.save()
        
        # 메시지 타입 가져오기
        message_type = index.data(Qt.ItemDataRole.UserRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        # 파스텔톤 색상 설정
        if message_type == "user":
            bg_color = QColor(255, 182, 193)  # 연한 핑크
            text_color = QColor(139, 69, 19)  # 진한 갈색
            is_user = True
        elif message_type == "correction":
            bg_color = QColor(255, 239, 153)  # 연한 노란색
            text_color = QColor(139, 69, 19)  # 진한 갈색
            is_user = False
        elif message_type == "story":
            bg_color = QColor(173, 216, 230)  # 연한 파란색
            text_color = QColor(25, 25, 112)  # 미드나이트 블루
            is_user = False
        else:
            bg_color = QColor(144, 238, 144)  # 연한 초록색
            text_color = QColor(0, 100, 0)  # 다크 그린
            is_user = False
        
        # 폰트 설정
        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        
        # 텍스트 크기 측정
        font_metrics = QFontMetrics(font)
        max_text_width = int(option.rect.width() * 0.7) - 56
        
        text_rect = font_metrics.boundingRect(
            QRect(0, 0, max_text_width, 2000),
            Qt.TextFlag.TextWordWrap,
            text
        )
        
        # 말풍선 크기
        bubble_padding = 28
        bubble_width = text_rect.width() + bubble_padding * 2
        bubble_height = text_rect.height() + bubble_padding * 2
        
        bubble_width = max(bubble_width, 200)
        bubble_height = max(bubble_height, 70)
        
        # 말풍선 위치
        if is_user:
            bubble_x = option.rect.right() - bubble_width - 10
        else:
            bubble_x = option.rect.left() + 10
        
        bubble_y = option.rect.top() + (option.rect.height() - bubble_height) // 2
        bubble_rect = QRect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # # 그림자
        # shadow_offset = 3
        # shadow_rect = bubble_rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        # shadow_color = QColor(0, 0, 0, 30)
        # painter.setBrush(QBrush(shadow_color))
        # painter.setPen(QPen(shadow_color))
        # painter.drawRoundedRect(shadow_rect, 18, 18)
        # 그림자 효과
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(30)
        # shadow.setColor(QColor(139, 111, 71, 51))  # rgba(139, 111, 71, 0.2)
        # shadow.setOffset(0, 10)
        # panel.setGraphicsEffect(shadow)
        
        # layout = QVBoxLayout(panel)
        # layout.setContentsMargins(20, 20, 20, 20)
        # layout.setSpacing(20)
        
        # 배경 
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(0, 0, 0, 0)))
        painter.drawRoundedRect(bubble_rect, 18, 18)
        
        # 테두리 
        border_color = QColor(0, 0, 0, 40)
        if message_type == "user":
            border_color = QColor(139, 69, 19, 80)
        elif message_type == "correction":
            border_color = QColor(218, 165, 32, 80)
        elif message_type == "story":
            border_color = QColor(25, 25, 112, 80)
        else:
            border_color = QColor(0, 100, 0, 80)
        
        painter.setBrush(QBrush())
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(bubble_rect, 18, 18)
        
        # 텍스트 
        painter.setPen(QPen(text_color))
        text_draw_rect = bubble_rect.adjusted(bubble_padding, bubble_padding, -bubble_padding, -bubble_padding)
        
        if is_user:
            painter.drawText(text_draw_rect, Qt.AlignmentFlag.AlignRight | Qt.TextFlag.TextWordWrap, text)
        else:
            painter.drawText(text_draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, text)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        from PySide6.QtGui import QFont, QFontMetrics
        from PySide6.QtCore import QRect, QSize
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return QSize(option.rect.width(), 60)
        
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        
        font_metrics = QFontMetrics(font)
        max_text_width = max(200, int(option.rect.width() * 0.7) - 56)
        
        text_rect = font_metrics.boundingRect(
            QRect(0, 0, max_text_width, 2000),
            Qt.TextFlag.TextWordWrap,
            text
        )
        
        bubble_padding = 28
        height = max(80, text_rect.height() + bubble_padding * 2 + 20)
        
        return QSize(option.rect.width(), height)


class ChatArea(QFrame):
    # 시그널 정의
    messageSent = Signal(str)  # 메시지 전송 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        """채팅 영역 UI 설정"""
        self.setObjectName("chatArea")
        
        self.setStyleSheet("""
            QFrame#chatArea {
                background-image: url(assets/blue.png);
                background-repeat: repeat;
                background-position: center;
                color: white;
                border-right: 2px solid rgba(255, 255, 255, 0.2);
                padding: 0px;
                margin: 0px;
                border-radius: 0px;
            }
        """)
        # border-left: 2px solid rgba(255, 255, 255, 0.2);
        # background-color: #ffca61;
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # UI 컴포넌트들 생성
        self.createComponents()
        
        # 커스텀 델리게이트 설정
        # self.chat_delegate = ChatMessageDelegate()
        # self.chatList.setItemDelegate(self.chat_delegate)

    def _rolePalette(self, message_type: str):
        """역할별 그라데이션/텍스트 색상 반환"""
        if message_type == "user":
            # 오른쪽 오렌지(스크린샷 톤)
            return {
                "grad": ("#FFD08A", "#F5B04B"),  # 밝은 앰버 → 진한 앰버
                "text": "#1F1300",
                "border_mul": 0.90
            }
        elif message_type == "story":
            # 밝은 스카이블루
            return {
                "grad": ("#D6F0FF", "#9BD7FF"),
                "text": "#0B2230",
                "border_mul": 0.90
            }
        else:
            # 기본(AI)
            return {
                "grad": ("#DBEAFE", "#BFDBFE"),
                "text": "#1E3A8A",
                "border_mul": 0.90
            }

    def _createBubbleWidget(self, text: str, role: str, max_width: int) -> QWidget:
        """
        버블(패널+라벨) 위젯을 만들어 반환. QGraphicsDropShadowEffect 적용.
        role: 'user' | 'story' | 'correction' | 'chat'
        """
        # 외곽 래퍼(투명) + 좌우 정렬용
        wrapper = QWidget()
        wrapper.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        h = QHBoxLayout(wrapper)
        h.setContentsMargins(8, 8, 8, 18)
        h.setSpacing(0)

        # 실제 말풍선 패널
        panel = QFrame()
        panel.setObjectName("bubble")
        panel.setStyleSheet("QFrame#bubble { border-radius: 18px; }")

        # 라벨
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setFont(QFont("Arial", 13))

        # 팔레트 적용
        pal = self._rolePalette(role if role in ("user", "story", "correction", "chat") else "chat")
        c1, c2 = pal["grad"]
        txt = pal["text"]
        label.setStyleSheet(f"color: {txt};")

        panel.setStyleSheet(
            f"""
            QFrame#bubble {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c1}, stop:1 {c2});
                border: 1.5px solid rgba(0,0,0,0);  /* 일단 투명, 아래서 계산해 덮어씀 */
                border-radius: 18px;
            }}
            """
        )

        # 그림자
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 60))  # 알파 ~0.24
        shadow.setOffset(0, 6)                # 아래로만
        panel.setGraphicsEffect(shadow)

        # 내부 여백
        v = QVBoxLayout(panel)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)
        v.addWidget(label)
        MAX_RATIO = 0.72
        PAD_X = 16        # panel 좌/우 패딩
        WRAP_M = 8 + 8    # wrapper 좌/우 마진 합
        max_content_w = max(140, int(max_width * MAX_RATIO) - (PAD_X*2) - WRAP_M)
        label.setWordWrap(True)
        label.setMaximumWidth(max_content_w)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        # label.setFixedWidth(content_w)                    # ★ 라벨 폭 고정(줄바꿈 기준)
        # panel.setFixedWidth(content_w + PAD_X*2)          # 패널 폭도 고정
        # panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        # wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # 최대 폭 제한
        # panel.setMaximumWidth(int(max_width * 0.72))  # 리스트 폭의 ~68%
        # panel.setMinimumWidth(120)

        # 테두리 색: 그라데이션 중간색을 살짝 어둡게
        def _hex2rgb(hx): 
            hx = hx.lstrip("#");  return tuple(int(hx[i:i+2], 16) for i in (0,2,4))
        r1,g1,b1 = _hex2rgb(c1); r2,g2,b2 = _hex2rgb(c2)
        mid = ( (r1+r2)//2, (g1+g2)//2, (b1+b2)//2 )
        mul = pal["border_mul"]
        br = QColor(int(mid[0]*mul), int(mid[1]*mul), int(mid[2]*mul), 210)
        panel.setStyleSheet(
            panel.styleSheet().replace("rgba(0,0,0,0)", f"rgba({br.red()},{br.green()},{br.blue()},{br.alpha()})")
        )

        # 정렬: user는 오른쪽, 나머지는 왼쪽
        if role == "user":
            h.addStretch(1)
            h.addWidget(panel, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            h.addWidget(panel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            h.addStretch(1)

        # 내용에 맞춰 높이 계산
        wrapper.adjustSize()
        return wrapper

    
    def createComponents(self):
        """채팅 영역 컴포넌트들 생성"""
        # 채팅 제목
        self.chatTitle = QLabel("✨ Create Your Storybook!", self)
        self.chatTitle.setObjectName("chatTitle")
        
        font_title = QFont()
        font_title.setFamilies(["Pretendard", "Arial"])
        font_title.setPointSize(self._get_relative_font_size(18))
        font_title.setBold(True)
        self.chatTitle.setFont(font_title)
        self.chatTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chatTitle.setStyleSheet("""
            QLabel {
                color: white;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 255, 255, 0.15),
                    stop:1 rgba(255, 255, 255, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                margin-bottom: 10px;
                font-weight: bold;
            }
        """)
        
        # 채팅 리스트
        self.chatList = QListWidget(self)
        self.chatList.setObjectName("chatList")
        self.chatList.setWordWrap(True)
        
        font_chat = QFont()
        font_chat.setFamilies(["Pretendard", "Arial"])
        font_chat.setPointSize(self._get_relative_font_size(14))
        self.chatList.setFont(font_chat)
        # self.chatList.setStyleSheet("""
        #     QListWidget {
        #         background: rgba(255, 255, 255, 0.9);
        #         border: 1px solid rgba(200, 200, 200, 0.3);
        #         border-radius: 15px;
        #         padding: 15px;
        #         color: #333333;
        #         font-size: 14px;
        #     }
        #     QListWidget::item {
        #         padding: 12px 18px;
        #         margin: 6px 15px;
        #         border-radius: 18px;
        #         border: 1px solid rgba(0, 0, 0, 0.1);
        #         line-height: 1.5;
        #         font-weight: 500;
        #         min-height: 25px;
        #         max-width: 80%;
        #     }
        #     QListWidget::item:hover {
        #         opacity: 0.9;
        #     }
        #     QListWidget::item:selected {
        #         outline: none;
        #         border: 2px solid rgba(255, 165, 0, 0.5);
        #     }
        # """)
        self.chatList.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 16px;
                padding: 8px;
            }
            QListWidget::item { margin: 6px 8px; padding: 0px; border: none; }
            QListWidget::item:selected { background: transparent; }
            QListWidget::item:hover { background: transparent; }
        """)

        
        # 입력 영역
        self.textEdit_childStory = QTextEdit(self)
        self.textEdit_childStory.setObjectName("textEdit_childStory")
        self.textEdit_childStory.setMaximumHeight(100)
        self.textEdit_childStory.setPlaceholderText("💭 Write your sentence here...")
        
        font_input = QFont()
        font_input.setFamilies(["Pretendard", "Arial"])
        font_input.setPointSize(self._get_relative_font_size(14))
        self.textEdit_childStory.setFont(font_input)
        self.textEdit_childStory.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                color: #333333;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 2px solid rgba(255, 255, 255, 0.7);
                background: rgba(255, 255, 255, 1.0);
            }
        """)
        
        # 전송 버튼 
        self.btnSendMessage = QPushButton("🚀 Send and Continue", self)
        self.btnSendMessage.setObjectName("btnSendMessage")
        self.btnSendMessage.setFixedHeight(50)
        self.btnSendMessage.setCursor(Qt.PointingHandCursor)


        
        font_btn = QFont()
        font_btn.setFamilies(["Pretendard", "Arial"])
        font_btn.setPointSize(self._get_relative_font_size(14))
        font_btn.setBold(True)
        self.btnSendMessage.setFont(font_btn)
        self.btnSendMessage.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffd54f,
                    stop:1 #ffb300);
                color: #d84315;
                font-weight: bold;
                border: 2px solid transparent;
                border-radius: 12px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffecb3,
                    stop:1 #ffd54f);
                border: 2px solid rgba(255, 213, 79, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb300,
                    stop:1 #ff8f00);
                border: 2px solid rgba(255, 143, 0, 0.7);
            }
        """)
        
        # 레이아웃에 컴포넌트 추가
        self.layout.addWidget(self.chatTitle)
        self.layout.addWidget(self.chatList, 1)  # 확장 가능
        self.layout.addWidget(self.textEdit_childStory)
        self.layout.addWidget(self.btnSendMessage)
    
    def connectSignals(self):
        """시그널 연결"""
        self.btnSendMessage.clicked.connect(self.sendMessage)
        # Enter 키로 메시지 전송
        self.textEdit_childStory.textChanged.connect(self.onTextChanged)
    
    def onTextChanged(self):
        """텍스트 변경 시 Enter 키 처리"""
        # Ctrl+Enter로 메시지 전송하도록 설정할 수 있음
        pass

    def sendMessage(self):
        text = self.textEdit_childStory.toPlainText().strip()
        if text:
            self.messageSent.emit(text)
            self.textEdit_childStory.clear()

    # def addMessage(self, text: str, is_user: bool = False, message_type: str = "normal"):
    #     """채팅 메시지 추가"""
    #     item = QListWidgetItem()
        
    #     if is_user:
    #         display_text = f"{text}"
    #         item.setData(Qt.ItemDataRole.UserRole, "user")
    #     else:
    #         if message_type == "correction":
    #             display_text = f"🔧 {text}"
    #             item.setData(Qt.ItemDataRole.UserRole, "correction")
    #         elif message_type == "story":
    #             display_text = f"📖 AI: {text}"
    #             item.setData(Qt.ItemDataRole.UserRole, "story")
    #         else:
    #             display_text = f"🤖 AI: {text}"
    #             item.setData(Qt.ItemDataRole.UserRole, "chat")
        
    #     item.setText(display_text)
    #     item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        
    #     self.chatList.addItem(item)
    #     self.chatList.scrollToBottom()

    def addMessage(self, text: str, is_user: bool = False, message_type: str = "normal"):
        role = "user" if is_user else (message_type if message_type in ("chat", "story", "correction") else "chat")

        item = QListWidgetItem()
        # 리스트 뷰 폭 기반으로 버블 생성
        viewport_w = self.chatList.viewport().width() or self.chatList.width()
        bubble = self._createBubbleWidget(text, role, viewport_w)
        bubble.layout().activate()
        bubble.adjustSize()

        # message_type 설정
        bubble.message_type = message_type

        size = bubble.sizeHint()
        size.setHeight(size.height() + 14)

        # 높이 힌트 설정
        # bubble.resize(min(int(viewport_w * 0.72), bubble.sizeHint().width()), bubble.sizeHint().height())
        item.setSizeHint(size)

        self.chatList.addItem(item)
        self.chatList.setItemWidget(item, bubble)
        self.chatList.scrollToBottom()
    
    def clearChat(self):
        """채팅 내용 지우기"""
        self.chatList.clear()
    
    def getInputText(self):
        """입력 텍스트 가져오기"""
        return self.textEdit_childStory.toPlainText().strip()
    
    def setInputText(self, text: str):
        """입력 텍스트 설정"""
        self.textEdit_childStory.setPlainText(text)

    def updateStreamingMessage(self, newText: str, message_type: str):
        """
        스트리밍 메시지 UI 업데이트
        """
        # 마지막 버블 확인
        count = self.chatList.count()
        if count > 0:
            last_item = self.chatList.item(count - 1)
            last_widget = self.chatList.itemWidget(last_item)

            # 마지막 버블의 타입을 가져오기
            last_type = getattr(last_widget, "message_type", None)

            if last_type == message_type:
                label = last_widget.findChild(QLabel)
                if label:
                    label.setText(newText)

                    # 폭 제한 & 높이 널널하게 재계산
                    viewport_w = self.chatList.viewport().width() or self.chatList.width()
                    max_w = int(viewport_w * 0.72)
                    label.setWordWrap(True)
                    label.setFixedWidth(max_w)

                    # 레이아웃 다시 계산
                    last_widget.layout().activate()
                    label.adjustSize()

                    # 널널한 높이 반영
                    hint = last_widget.sizeHint()
                    hint.setHeight(hint.height() + 16)  # padding
                    last_item.setSizeHint(hint)

                    self.chatList.scrollToBottom()
                return

        # kind가 다르거나 버블 없음 → 새 버블 추가
        self.addMessage(newText, is_user=False, message_type=message_type)