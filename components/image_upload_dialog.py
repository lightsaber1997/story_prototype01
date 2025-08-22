from PySide6 import QtCore, QtGui, QtWidgets

class ImageUploadDialog(QtWidgets.QDialog):
    fileSelected = QtCore.Signal(str)  # File Path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이미지 업로드")
        self.setModal(True)
        self.setMinimumSize(420, 300)
        self.setAcceptDrops(True)  # Accept Drag&Drop

        # ----- 전체 레이아웃 -----
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        # 중앙 카드
        card = QtWidgets.QFrame(self)
        card.setObjectName("Card")
        card.setMinimumSize(360, 200)
        card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        card.setFrameShadow(QtWidgets.QFrame.Raised)

        shadow = QtWidgets.QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        # 설명 라벨
        title = QtWidgets.QLabel("Upload Your Image", card)
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:600; color:#111827;")
        card_layout.addWidget(title)

        # 드롭 영역
        self.dropArea = QtWidgets.QLabel("📥 Drag & Drop \n or \nClick Here", card)
        self.dropArea.setAlignment(QtCore.Qt.AlignCenter)
        self.dropArea.setObjectName("DropArea")
        card_layout.addWidget(self.dropArea, alignment=QtCore.Qt.AlignCenter)

        root.addWidget(card, alignment=QtCore.Qt.AlignCenter)

        # 드롭 영역 클릭 → 파일 선택
        self.dropArea.mousePressEvent = self._openFileDialog

        # 스타일 적용
        self._apply_styles()

    # ----- Handle Drag&Drop -----
    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.fileSelected.emit(file_path)
            self.accept()  # 다이얼로그 닫기

    # ----- Handle Button Click -----
    def _openFileDialog(self, event):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Upload Your Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.fileSelected.emit(file_path)
            self.accept()

    # ----- Style -----
    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: #0c192e;
            }
            #Card {
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid rgba(17, 24, 39, 0.08);
                font-size: 16px;
            }
            #DropArea {
                border: 2px dashed #3B82F6;
                border-radius: 12px;
                font-size: 14px;
                color: #374151;
                padding: 40px;
                background: #F9FAFB;
            }
            #DropArea:hover {
                background: #EFF6FF;
            }
        """)