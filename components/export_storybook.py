from PySide6.QtGui import QPdfWriter, QPainter, QPageSize, QFont, QPixmap, QBrush, QColor
from PySide6.QtCore import QRectF, Qt, QSizeF
from pathlib import Path

def export_to_pdf(storybook, filename: str) -> None:
    """Export all storybook pages as a simple PDF with title, image, and text."""

    writer = QPdfWriter(filename)
    # 스토리북에 맞는 사용자 정의 페이지 크기 (세로로 긴 비율)
    custom_size = QSizeF(600, 800)  # 3:4 비율 (스토리북 형태)
    writer.setPageSize(QPageSize(custom_size, QPageSize.Point))
    writer.setResolution(300)  # 고해상도로 변경
    painter = QPainter(writer)

    # 실제 페이지 크기 가져오기
    page_width = writer.width()
    page_height = writer.height()
    
    # 스토리북 비율에 맞는 마진 - 페이지 크기에 비례
    margin_x = page_width * 0.05  # 페이지 너비의 5%
    margin_y = page_height * 0.04  # 페이지 높이의 4%
    images_dir = Path("images")  # 프로젝트 내 images 폴더 기준

    for page_idx in range(storybook.total_pages):
        # 배경 이미지 적용 (paper texture) - 전체 페이지 크기로
        paper_path = Path("assets/paper.jpg")
        if paper_path.exists():
            paper_pixmap = QPixmap(str(paper_path))
            if not paper_pixmap.isNull():
                # 페이지 전체에 배경 이미지 적용 - 실제 페이지 크기 사용
                scaled_paper = paper_pixmap.scaled(
                    page_width, page_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                painter.drawPixmap(0, 0, scaled_paper)
        else:
            # 배경 이미지가 없으면 흰색 배경 - 전체 페이지 채우기
            painter.fillRect(0, 0, page_width, page_height, QBrush(QColor(255, 255, 255)))
        
        y = margin_y

        # Title - 중앙 정렬, 고정 크기
        title_text = f"CHAPTER {page_idx+1}"
        title_font_size = 24  # 고정 크기
        font = QFont("Georgia", title_font_size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(42, 41, 53))
        
        title_height = page_height * 0.06  # 제목 영역 높이
        title_rect = QRectF(margin_x, y, page_width - 2*margin_x, title_height)
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
            title_text
        )
        y += title_height + margin_y * 0.5

        # 이미지 - 중앙 정렬, 페이지 크기에 비례
        image_path = images_dir / f"page_{page_idx+1}.png"
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                # 이미지를 페이지 너비의 85% 사용, 높이는 페이지의 35%
                img_width = page_width * 0.85
                img_height = page_height * 0.35
                
                # 이미지 비율 유지하며 그리기
                scaled_pixmap = pixmap.scaled(
                    int(img_width), int(img_height),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # 실제 이미지 크기 계산 후 중앙 정렬
                actual_width = scaled_pixmap.width()
                actual_height = scaled_pixmap.height()
                actual_x = (page_width - actual_width) / 2
                actual_y = y
                
                painter.drawPixmap(int(actual_x), int(actual_y), scaled_pixmap)
                y += actual_height + margin_y

        # 본문 텍스트 - 남은 공간 모두 사용, 고정 폰트 크기
        text = storybook._page_texts.get(page_idx, "")
        if text.strip():
            text_font_size = 16  # 고정 크기
            font = QFont("Georgia", text_font_size)
            painter.setFont(font)
            painter.setPen(QColor(42, 41, 53))
            
            # 남은 공간 계산
            available_height = page_height - y - margin_y
            print(f"Page {page_idx+1}: Page size: {page_width}x{page_height}, Available height for text: {available_height}")
            
            text_rect = QRectF(
                margin_x, 
                y, 
                page_width - 2*margin_x, 
                available_height
            )
            
            painter.drawText(
                text_rect,
                Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignJustify,
                text
            )

        if page_idx < storybook.total_pages - 1:
            writer.newPage()

    painter.end()
    print(f"[export_simple_pdf] Exported {storybook.total_pages} pages to {filename}")
    print(f"Final page size used: {page_width}x{page_height}")