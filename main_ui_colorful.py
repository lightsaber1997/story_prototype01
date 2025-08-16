# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QBrush, QColor, QCursor, QFont, QPalette, QPixmap)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)

class Ui_StoryMakerMainWindow(object):
    def _get_relative_font_size(self, base_size):
        """DPI에 따른 상대적 폰트 크기 계산"""
        from PySide6.QtWidgets import QApplication
        # 시스템 DPI 스케일링 팩터 가져오기
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            dpi_ratio = screen.logicalDotsPerInch() / 96.0  # 96 DPI가 기본
            return max(8, int(base_size * min(dpi_ratio, 1.5)))  # 최대 1.5배까지만 확대
        return base_size
    
    def setupUi(self, StoryMakerMainWindow):
        if not StoryMakerMainWindow.objectName():
            StoryMakerMainWindow.setObjectName(u"StoryMakerMainWindow")
        StoryMakerMainWindow.resize(1000, 700)
        StoryMakerMainWindow.setMinimumSize(800, 600)
        
        palette = QPalette()
        brush = QBrush(QColor(85, 175, 240, 255))  
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        StoryMakerMainWindow.setPalette(palette)
        
        self.centralwidget = QWidget(StoryMakerMainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        try:
            background_pixmap = QPixmap('assets/image/background.png')
            if not background_pixmap.isNull():
                # 배경색 설정
                palette = QPalette()
                brush = QBrush(background_pixmap)
                brush.setStyle(Qt.BrushStyle.TexturePattern)
                palette.setBrush(QPalette.ColorRole.Window, brush)
                self.centralwidget.setPalette(palette)
                self.centralwidget.setAutoFillBackground(True)
            else:
                self.centralwidget.setStyleSheet("background-color: #55afef;")
        except:
            self.centralwidget.setStyleSheet("background-color: #55afef;")
        
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)
        
        # 왼쪽 레이아웃
        self.leftFrame = QFrame(self.centralwidget)
        self.leftFrame.setObjectName(u"leftFrame")
        self.leftFrame.setMinimumWidth(350)
        self.leftFrame.setMaximumWidth(450)
        self.leftFrame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.leftFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(90, 119, 236, 0.5);
                color: white;
                padding: 10px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        self.leftLayout = QVBoxLayout(self.leftFrame)
        self.leftLayout.setContentsMargins(20, 20, 20, 20)
        self.leftLayout.setSpacing(18)
        
        self.label_title = QLabel(self.leftFrame)
        self.label_title.setObjectName(u"label_title")
        font_title = QFont()
        font_title.setFamilies([u"Pretendard"])
        font_title.setPointSize(self._get_relative_font_size(22))
        font_title.setBold(True)
        self.label_title.setFont(font_title)
        self.label_title.setStyleSheet("""
            QLabel {
                color: white;
                padding: 15px;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 255, 255, 0.15),
                    stop:1 rgba(255, 255, 255, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_title.setText("✨ Create Your Storybook!")
        self.leftLayout.addWidget(self.label_title)
        
        # 채팅
        self.chatList = QListWidget(self.leftFrame)
        self.chatList.setObjectName(u"chatList")
        self.chatList.setWordWrap(True)  # 줄바꿈 활성화
        font_chat = QFont()
        font_chat.setFamilies([u"Pretendard"])
        font_chat.setPointSize(self._get_relative_font_size(14))  # 폰트 크기 증가
        self.chatList.setFont(font_chat)
        self.chatList.setStyleSheet("""
            QListWidget {
                background: rgba(255, 248, 220, 0.9);
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
                background: #ff6b6b;
                color: white;
            }
            QListWidget::item:hover {
                opacity: 0.9;
                background: #ff5252;
            }
            QListWidget::item:selected {
                outline: none;
                border: 2px solid rgba(255, 165, 0, 0.5);
                background: #ff4444;
            }
        """)
        self.chatList.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.leftLayout.addWidget(self.chatList)
        
        self.textEdit_childStory = QTextEdit(self.leftFrame)
        self.textEdit_childStory.setObjectName(u"textEdit_childStory")
        self.textEdit_childStory.setMaximumHeight(120)  # 높이 증가
        self.textEdit_childStory.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  # 줄바꿈 설정
        font_input = QFont()
        font_input.setFamilies([u"Pretendard"])
        font_input.setPointSize(self._get_relative_font_size(14))  # 폰트 크기 증가
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
        self.textEdit_childStory.setPlaceholderText("💭 Write your sentence here...")
        self.leftLayout.addWidget(self.textEdit_childStory)
        
        self.btnContinueStory = QPushButton(self.leftFrame)
        self.btnContinueStory.setObjectName(u"btnContinueStory")
        font_btn = QFont()
        font_btn.setFamilies([u"Pretendard"])
        font_btn.setPointSize(self._get_relative_font_size(16))
        font_btn.setBold(True)
        self.btnContinueStory.setFont(font_btn)
        self.btnContinueStory.setMinimumHeight(50)
        self.btnContinueStory.setStyleSheet("""
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
        self.btnContinueStory.setText("🚀 Send and Continue")
        self.leftLayout.addWidget(self.btnContinueStory)
        
        self.mainLayout.addWidget(self.leftFrame)
        
        # 오른쪽 
        self.rightFrame = QFrame(self.centralwidget)
        self.rightFrame.setObjectName(u"rightFrame")
        self.rightFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.rightFrame.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        
        self.rightLayout = QVBoxLayout(self.rightFrame)
        self.rightLayout.setContentsMargins(15, 12, 15, 15)
        self.rightLayout.setSpacing(16)
        
        self.pageLayout = QHBoxLayout()
        self.pageLayout.setSpacing(15)
        
        self.label_page_prev = QLabel(self.rightFrame)
        self.label_page_prev.setObjectName(u"label_page_prev")
        font_nav = QFont()
        font_nav.setFamilies([u"Pretendard"])
        font_nav.setPointSize(self._get_relative_font_size(18))
        font_nav.setBold(True)
        self.label_page_prev.setFont(font_nav)
        self.label_page_prev.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 4px 16px;
                max-height: 35px;
                min-height: 35px;
                font-weight: bold;
            }
            QLabel:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.label_page_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_page_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_page_prev.setText("‹")
        self.pageLayout.addWidget(self.label_page_prev)
        
        self.label_page = QLabel(self.rightFrame)
        self.label_page.setObjectName(u"label_page")
        font_page = QFont()
        font_page.setFamilies([u"Pretendard"])
        font_page.setPointSize(self._get_relative_font_size(16))
        font_page.setBold(True)
        self.label_page.setFont(font_page)
        self.label_page.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 4px 16px;
                max-height: 35px;
                min-height: 35px;
                font-weight: bold;
            }
        """)
        self.label_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_page.setText("1/3")
        self.pageLayout.addWidget(self.label_page)
        
        self.label_page_next = QLabel(self.rightFrame)
        self.label_page_next.setObjectName(u"label_page_next")
        self.label_page_next.setFont(font_nav)
        self.label_page_next.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 4px 16px;
                max-height: 35px;
                min-height: 35px;
                font-weight: bold;
            }
            QLabel:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.label_page_next.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_page_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_page_next.setText("›")
        self.pageLayout.addWidget(self.label_page_next)
        
        self.rightLayout.addLayout(self.pageLayout)
        
        self.label_generatedImage = QLabel(self.rightFrame)
        self.label_generatedImage.setObjectName(u"label_generatedImage")
        self.label_generatedImage.setMinimumSize(350, 260)
        self.label_generatedImage.setMaximumHeight(320)
        self.label_generatedImage.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        font_img = QFont()
        font_img.setFamilies([u"Pretendard"])
        font_img.setPointSize(self._get_relative_font_size(18))
        font_img.setBold(True)
        self.label_generatedImage.setFont(font_img)
        self.label_generatedImage.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff3e0,
                    stop:1 #ffe0b2);
                border: 2px solid rgba(255, 193, 7, 0.4);
                padding: 30px;
                border-radius: 15px;
                color: #8d6e63;
                font-weight: bold;
            }
        """)
        self.label_generatedImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_generatedImage.setText("🎨 Generated image will appear here")
        self.rightLayout.addWidget(self.label_generatedImage)
        
        self.chatList_2 = QListWidget(self.rightFrame)
        self.chatList_2.setObjectName(u"chatList_2")
        self.chatList_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chatList_2.setWordWrap(True)  
        font_story_list = QFont()
        font_story_list.setFamilies([u"Pretendard"])
        font_story_list.setPointSize(self._get_relative_font_size(16))  # 폰트 크기 증가
        self.chatList_2.setFont(font_story_list)
        self.chatList_2.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.15),
                    stop:1 rgba(255, 255, 255, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 20px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 500;
            }
            QListWidget::item {
                padding: 18px 25px;
                margin: 6px 0px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                line-height: 1.5;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.4);
            }
        """)
        
        font_story = QFont()
        font_story.setFamilies([u"Pretendard"])
        font_story.setPointSize(self._get_relative_font_size(18))
        font_story.setBold(True)
        font_story.setItalic(True)
        item = QListWidgetItem(self.chatList_2)
        item.setText("🌟 Once upon a time...")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFont(font_story)
        item.setForeground(QBrush(QColor(255, 255, 255, 255)))
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        
        self.rightLayout.addWidget(self.chatList_2)
        
        self.btnSaveStory = QPushButton(self.rightFrame)
        self.btnSaveStory.setObjectName(u"btnSaveStory")
        self.btnSaveStory.setMinimumHeight(60)
        font_save = QFont()
        font_save.setFamilies([u"Pretendard"])
        font_save.setPointSize(self._get_relative_font_size(18))
        font_save.setBold(True)
        self.btnSaveStory.setFont(font_save)
        self.btnSaveStory.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnSaveStory.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff7043,
                    stop:1 #e64a19);
                color: white;
                font-weight: bold;
                border: 2px solid transparent;
                border-radius: 16px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff8a65,
                    stop:1 #ff7043);
                border: 2px solid rgba(255, 112, 67, 0.6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e64a19,
                    stop:1 #d84315);
                border: 2px solid rgba(216, 67, 21, 0.8);
            }
        """)
        self.btnSaveStory.setText("💾 Save Storybook")
        self.rightLayout.addWidget(self.btnSaveStory)
        
        self.mainLayout.addWidget(self.rightFrame)
        
        StoryMakerMainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(StoryMakerMainWindow)
        QMetaObject.connectSlotsByName(StoryMakerMainWindow)

    def retranslateUi(self, StoryMakerMainWindow):
        StoryMakerMainWindow.setWindowTitle(QCoreApplication.translate("StoryMakerMainWindow", u"Edge AI Story Maker", None))