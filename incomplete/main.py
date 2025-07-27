import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem
from PySide6.QtCore import Qt
from main_ui import Ui_StoryMakerMainWindow
# ex) ai_module.py 파일의 ask_ai 메서드라고 가정 
# from ai_module import ask_ai

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_StoryMakerMainWindow()
        self.ui.setupUi(self)
        
        # 현재 페이지 (임시)
        self.current_page = 1
        self.total_pages = 3
        self.story_pages = ["Once upon a time...", "", ""]  # 각 페이지의 스토리
        
        self.connect_signals()
        
        # initial state
        self.update_page_display()
        
        # 버튼 연결 해야 할 부분
    def connect_signals(self):
        """버튼과 이벤트를 연결"""

        self.ui.btnContinueStory.clicked.connect(self.continue_story)
        self.ui.btnSaveStory.clicked.connect(self.save_story)
        
        # 페이지 네비게이션
        self.ui.label_page_prev.mousePressEvent = self.previous_page
        self.ui.label_page_next.mousePressEvent = self.next_page
        
        # ai 에 메세지 보내기
    def continue_story(self):
        """스토리 계속하기 버튼 클릭 시 실행"""
        user_input = self.ui.textEdit_childStory.toPlainText().strip()
        
        if not user_input:
            QMessageBox.warning(self, "입력 오류", "스토리를 입력해주세요!")
            return
            
        item = QListWidgetItem(f"사용자: {user_input}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ui.chatList.addItem(item)
        
        # AI 응답 (실제로는 AI 모델 호출 예정)
        # 아래 48th line을 주석 해제하고 49th line을 주석처리 하시면 됩니다.
        # ai_response = ask_ai(user_input)
        ai_response = f"AI가 '{user_input}'을 바탕으로 스토리를 계속 만들어갑니다..."
        ai_item = QListWidgetItem(f"AI: {ai_response}")
        ai_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.ui.chatList.addItem(ai_item)
        
        self.story_pages[self.current_page - 1] += f" {user_input}"
        self.update_story_display()
        self.ui.textEdit_childStory.clear()
        self.ui.chatList.scrollToBottom()
        
    def save_story(self):
        """스토리북 저장 버튼 클릭 시 실행"""
        QMessageBox.information(self, "저장 완료", "스토리북이 성공적으로 저장되었습니다!")
        
    def previous_page(self, event):
        """이전 페이지로 이동"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page_display()
            self.update_story_display()
            
    def next_page(self, event):
        """다음 페이지로 이동"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_page_display()
            self.update_story_display()
            
    def update_page_display(self):
        """페이지 표시 업데이트"""
        self.ui.label_page.setText(f"{self.current_page}/{self.total_pages}")
    
        if self.current_page == 1:
            self.ui.label_page_prev.setStyleSheet("""
                QLabel {
                    color: #666666;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
            """)
        else:
            self.ui.label_page_prev.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
                QLabel:hover {
                    background: rgba(255, 255, 255, 0.2);
                    color: #ffd54f;
                }
            """)
            
        if self.current_page == self.total_pages:
            self.ui.label_page_next.setStyleSheet("""
                QLabel {
                    color: #666666;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
            """)
        else:
            self.ui.label_page_next.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 10px 15px;
                    min-width: 40px;
                    min-height: 40px;
                }
                QLabel:hover {
                    background: rgba(255, 255, 255, 0.2);
                    color: #ffd54f;
                }
            """)
            
    def update_story_display(self):
        """현재 페이지의 스토리 표시 업데이트"""
        current_story = self.story_pages[self.current_page - 1]
        
        self.ui.chatList_2.clear()
        if current_story:
            item = QListWidgetItem(current_story)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.chatList_2.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
