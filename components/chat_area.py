# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QListWidget, 
                               QTextEdit, QPushButton, QListWidgetItem, QStyledItemDelegate)
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

class ChatMessageDelegate(QStyledItemDelegate):
    """채팅 메시지를 위한 커스텀 델리게이트"""
    
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
        
        # 말풍선 크기 계산
        bubble_padding = 28
        bubble_width = text_rect.width() + bubble_padding * 2
        bubble_height = text_rect.height() + bubble_padding * 2
        
        bubble_width = max(bubble_width, 100)
        bubble_height = max(bubble_height, 50)
        
        # 말풍선 위치 계산
        if is_user:
            bubble_x = option.rect.right() - bubble_width - 10
        else:
            bubble_x = option.rect.left() + 10
        
        bubble_y = option.rect.top() + (option.rect.height() - bubble_height) // 2
        bubble_rect = QRect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # # 그림자 그리기
        # shadow_offset = 3
        # shadow_rect = bubble_rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        # shadow_color = QColor(0, 0, 0, 30)
        # painter.setBrush(QBrush(shadow_color))
        # painter.setPen(QPen(shadow_color))
        # painter.drawRoundedRect(shadow_rect, 18, 18)
        # 그림자 효과
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(139, 111, 71, 51))  # rgba(139, 111, 71, 0.2)
        shadow.setOffset(0, 10)
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 배경 그리기
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(0, 0, 0, 0)))
        painter.drawRoundedRect(bubble_rect, 18, 18)
        
        # 테두리 그리기
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
        
        # 텍스트 그리기
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
                background-color: rgba(90, 119, 236, 0.5);
                color: white;
                border-left: 2px solid rgba(255, 255, 255, 0.2);
                border-right: 2px solid rgba(255, 255, 255, 0.2);
                padding: 0px;
                margin: 0px;
                border-radius: 0px;
            }
        """)
        
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # UI 컴포넌트들 생성
        self.createComponents()
        
        # 커스텀 델리게이트 설정
        self.chat_delegate = ChatMessageDelegate()
        self.chatList.setItemDelegate(self.chat_delegate)
    
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
        self.chatList.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(200, 200, 200, 0.3);
                border-radius: 15px;
                padding: 15px;
                color: #333333;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px 18px;
                margin: 6px 15px;
                border-radius: 18px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                line-height: 1.5;
                font-weight: 500;
                min-height: 25px;
                max-width: 80%;
            }
            QListWidget::item:hover {
                opacity: 0.9;
            }
            QListWidget::item:selected {
                outline: none;
                border: 2px solid rgba(255, 165, 0, 0.5);
            }
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
        """메시지 전송"""
        text = self.textEdit_childStory.toPlainText().strip()
        if text:
            self.messageSent.emit(text)
            self.textEdit_childStory.clear()
    
    def addMessage(self, text: str, is_user: bool = False, message_type: str = "normal"):
        """채팅 메시지 추가"""
        item = QListWidgetItem()
        
        if is_user:
            display_text = f"{text}"
            item.setData(Qt.ItemDataRole.UserRole, "user")
        else:
            if message_type == "correction":
                display_text = f"🔧 {text}"
                item.setData(Qt.ItemDataRole.UserRole, "correction")
            elif message_type == "story":
                display_text = f"📖 AI: {text}"
                item.setData(Qt.ItemDataRole.UserRole, "story")
            else:
                display_text = f"🤖 AI: {text}"
                item.setData(Qt.ItemDataRole.UserRole, "chat")
        
        item.setText(display_text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        
        self.chatList.addItem(item)
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