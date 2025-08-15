from PySide6.QtWidgets import QWidget, QFileDialog
from app.ui.ui_start_widget import Ui_StartWidget

class StartPageWidget(QWidget):
    def __init__(self, stacked_widget, app_state):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.app_state = app_state

        # UI 설정
        self.ui = Ui_StartWidget()
        self.ui.setupUi(self)

        # 시그널 연결
        self.connect_signals()

    def connect_signals(self):
        """버튼 시그널 연결"""
        self.ui.texting_btn.clicked.connect(self.on_texting_clicked)
        self.ui.upload_btn.clicked.connect(self.on_upload_clicked)

    def on_texting_clicked(self):
        """텍스트로 시작하기 버튼 클릭 시"""
        self.app_state.start_mode = "text_only"
        self.go_to_next_page()

    def on_upload_clicked(self):
        """이미지 업로드 버튼 클릭 시"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Your Story Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )

        if file_path:
            print(f"[StartWidget] Image uploaded: {file_path}")
            self.app_state.start_mode = "image_upload"
            self.app_state.image_path =     file_path
            self.go_to_next_page()

    def go_to_next_page(self):
        """스토리 생성 페이지로 이동"""
        self.stacked_widget.setCurrentIndex(1)
