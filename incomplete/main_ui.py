# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QBrush, QColor, QCursor, QFont, QPalette)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)

class Ui_StoryMakerMainWindow(object):
    def setupUi(self, StoryMakerMainWindow):
        if not StoryMakerMainWindow.objectName():
            StoryMakerMainWindow.setObjectName(u"StoryMakerMainWindow")
        StoryMakerMainWindow.resize(1000, 700)
        StoryMakerMainWindow.setMinimumSize(800, 600)
        
        palette = QPalette()
        brush = QBrush(QColor(15, 23, 42, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        StoryMakerMainWindow.setPalette(palette)
        
        self.centralwidget = QWidget(StoryMakerMainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a,
                    stop:0.3 #1e293b,
                    stop:0.7 #334155,
                    stop:1 #0f172a);
            }
        """)
        
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(25)
        
        # === 왼쪽 패널 ===
        self.leftFrame = QFrame(self.centralwidget)
        self.leftFrame.setObjectName(u"leftFrame")
        self.leftFrame.setMinimumWidth(350)
        self.leftFrame.setMaximumWidth(450)
        self.leftFrame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.leftFrame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 20px;
                padding: 10px;
            }
        """)
        
        self.leftLayout = QVBoxLayout(self.leftFrame)
        self.leftLayout.setContentsMargins(20, 20, 20, 20)
        self.leftLayout.setSpacing(18)
        
        self.label_title = QLabel(self.leftFrame)
        self.label_title.setObjectName(u"label_title")
        font_title = QFont()
        font_title.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_title.setPointSize(22)
        font_title.setBold(True)
        self.label_title.setFont(font_title)
        self.label_title.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6,
                    stop:0.5 #8b5cf6,
                    stop:1 #ec4899);
                background: transparent;
                padding: 15px;
                border-radius: 12px;
                text-align: center;
            }
        """)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_title.setText("✨ Create Your Storybook!")
        self.leftLayout.addWidget(self.label_title)
        
        # 채팅
        self.chatList = QListWidget(self.leftFrame)
        self.chatList.setObjectName(u"chatList")
        self.chatList.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(51, 65, 85, 0.6),
                    stop:1 rgba(30, 41, 59, 0.6));
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 15px;
                padding: 15px;
                color: #e2e8f0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px 15px;
                margin: 4px 0px;
                border-radius: 10px;
                background: rgba(15, 23, 42, 0.4);
                border: 1px solid rgba(59, 130, 246, 0.1);
            }
            QListWidget::item:hover {
                background: rgba(59, 130, 246, 0.1);
                border-color: rgba(59, 130, 246, 0.3);
            }
            QListWidget::item:selected {
                background: rgba(59, 130, 246, 0.2);
                border-color: rgba(59, 130, 246, 0.5);
            }
        """)
        self.chatList.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.leftLayout.addWidget(self.chatList)
        
        self.textEdit_childStory = QTextEdit(self.leftFrame)
        self.textEdit_childStory.setObjectName(u"textEdit_childStory")
        self.textEdit_childStory.setMaximumHeight(100)
        self.textEdit_childStory.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 250, 252, 0.95),
                    stop:1 rgba(241, 245, 249, 0.95));
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 15px;
                padding: 15px;
                font-size: 14px;
                font-family: "Helvetica Neue", "Arial", "sans-serif";
                color: #1e293b;
                selection-background-color: rgba(59, 130, 246, 0.3);
            }
            QTextEdit:focus {
                border: 2px solid rgba(59, 130, 246, 0.7);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(248, 250, 252, 1.0));
            }
        """)
        self.textEdit_childStory.setPlaceholderText("💭 Write your sentence here...")
        self.leftLayout.addWidget(self.textEdit_childStory)
        
        self.btnContinueStory = QPushButton(self.leftFrame)
        self.btnContinueStory.setObjectName(u"btnContinueStory")
        font_btn = QFont()
        font_btn.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_btn.setPointSize(14)
        font_btn.setBold(True)
        self.btnContinueStory.setFont(font_btn)
        self.btnContinueStory.setMinimumHeight(55)
        self.btnContinueStory.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6,
                    stop:1 #8b5cf6);
                color: white;
                font-weight: bold;
                border: 2px solid transparent;
                border-radius: 15px;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb,
                    stop:1 #7c3aed);
                border: 2px solid rgba(59, 130, 246, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1d4ed8,
                    stop:1 #6d28d9);
            }
        """)
        self.btnContinueStory.setText("🚀 Send and Continue")
        self.leftLayout.addWidget(self.btnContinueStory)
        
        self.mainLayout.addWidget(self.leftFrame)
        
        # === 오른쪽 패널 ===
        self.rightFrame = QFrame(self.centralwidget)
        self.rightFrame.setObjectName(u"rightFrame")
        self.rightFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.rightFrame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(236, 72, 153, 0.2);
                border-radius: 20px;
                padding: 10px;
            }
        """)
        
        self.rightLayout = QVBoxLayout(self.rightFrame)
        self.rightLayout.setContentsMargins(15, 15, 15, 15)
        self.rightLayout.setSpacing(20)
        
        self.pageLayout = QHBoxLayout()
        self.pageLayout.setSpacing(25)
        
        self.label_page_prev = QLabel(self.rightFrame)
        self.label_page_prev.setObjectName(u"label_page_prev")
        font_nav = QFont()
        font_nav.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_nav.setPointSize(22)
        font_nav.setBold(True)
        self.label_page_prev.setFont(font_nav)
        self.label_page_prev.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.15),
                    stop:1 rgba(255, 255, 255, 0.08));
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 22px;
                padding: 12px 16px;
                min-width: 44px;
                min-height: 44px;
            }
            QLabel:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(59, 130, 246, 0.3),
                    stop:1 rgba(59, 130, 246, 0.15));
                color: #3b82f6;
                border-color: rgba(59, 130, 246, 0.4);
            }
        """)
        self.label_page_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_page_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_page_prev.setText("‹")
        self.pageLayout.addWidget(self.label_page_prev)
        
        self.label_page = QLabel(self.rightFrame)
        self.label_page.setObjectName(u"label_page")
        font_page = QFont()
        font_page.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_page.setPointSize(16)
        font_page.setBold(True)
        self.label_page.setFont(font_page)
        self.label_page.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(59, 130, 246, 0.3),
                    stop:1 rgba(59, 130, 246, 0.15));
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 16px;
                padding: 10px 24px;
                font-weight: 600;
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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.15),
                    stop:1 rgba(255, 255, 255, 0.08));
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 22px;
                padding: 12px 16px;
                min-width: 44px;
                min-height: 44px;
            }
            QLabel:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(59, 130, 246, 0.3),
                    stop:1 rgba(59, 130, 246, 0.15));
                color: #3b82f6;
                border-color: rgba(59, 130, 246, 0.4);
            }
        """)
        self.label_page_next.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_page_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_page_next.setText("›")
        self.pageLayout.addWidget(self.label_page_next)
        
        self.rightLayout.addLayout(self.pageLayout)
        
        self.label_generatedImage = QLabel(self.rightFrame)
        self.label_generatedImage.setObjectName(u"label_generatedImage")
        self.label_generatedImage.setMinimumSize(350, 200)
        self.label_generatedImage.setMaximumHeight(300)
        self.label_generatedImage.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        font_img = QFont()
        font_img.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_img.setPointSize(15)
        self.label_generatedImage.setFont(font_img)
        self.label_generatedImage.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.1),
                    stop:0.5 rgba(147, 51, 234, 0.1),
                    stop:1 rgba(236, 72, 153, 0.1));
                border: 2px dashed rgba(100, 116, 139, 0.4);
                border-radius: 18px;
                padding: 25px;
                color: #94a3b8;
                font-weight: 500;
                line-height: 1.5;
            }
        """)
        self.label_generatedImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_generatedImage.setText("🎨 Generated image will appear here")
        self.rightLayout.addWidget(self.label_generatedImage)
        
        self.chatList_2 = QListWidget(self.rightFrame)
        self.chatList_2.setObjectName(u"chatList_2")
        self.chatList_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chatList_2.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(51, 65, 85, 0.6),
                    stop:1 rgba(30, 41, 59, 0.6));
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 18px;
                padding: 25px;
                color: #f1f5f9;
                font-size: 16px;
                font-weight: 400;
                line-height: 1.7;
            }
            QListWidget::item {
                padding: 20px 25px;
                margin: 8px 0px;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 23, 42, 0.8),
                    stop:1 rgba(30, 41, 59, 0.8));
                border: 1px solid rgba(59, 130, 246, 0.2);
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(59, 130, 246, 0.15),
                    stop:1 rgba(59, 130, 246, 0.08));
                border-color: rgba(59, 130, 246, 0.3);
            }
        """)
        
        font_story = QFont()
        font_story.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_story.setPointSize(16)
        font_story.setBold(True)
        font_story.setItalic(True)
        item = QListWidgetItem(self.chatList_2)
        item.setText("🌟 Once upon a time...")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFont(font_story)
        item.setForeground(QBrush(QColor(241, 245, 249, 255)))
        
        self.rightLayout.addWidget(self.chatList_2)
        
        self.btnSaveStory = QPushButton(self.rightFrame)
        self.btnSaveStory.setObjectName(u"btnSaveStory")
        self.btnSaveStory.setMinimumHeight(65)
        font_save = QFont()
        font_save.setFamilies([u"Helvetica Neue", u"Arial", u"sans-serif"])
        font_save.setPointSize(16)
        font_save.setBold(True)
        self.btnSaveStory.setFont(font_save)
        self.btnSaveStory.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ec4899,
                    stop:1 #a855f7);
                color: white;
                font-weight: bold;
                border: 2px solid transparent;
                border-radius: 18px;
                padding: 18px 35px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #db2777,
                    stop:1 #9333ea);
                border: 2px solid rgba(236, 72, 153, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #be185d,
                    stop:1 #7c3aed);
            }
        """)
        self.btnSaveStory.setText("💾 Save Storybook")
        self.rightLayout.addWidget(self.btnSaveStory)
        
        self.mainLayout.addWidget(self.rightFrame)
        
        StoryMakerMainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(StoryMakerMainWindow)
        QMetaObject.connectSlotsByName(StoryMakerMainWindow)

    def retranslateUi(self, StoryMakerMainWindow):
        StoryMakerMainWindow.setWindowTitle(QCoreApplication.translate("StoryMakerMainWindow", u"✨ Edge AI Story Maker", None))