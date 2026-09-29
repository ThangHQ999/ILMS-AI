import os
import csv
from pathlib import Path
from typing import Optional


class DocumentLoadError(Exception):
    pass


def _read_txt_like(file_path: str) -> str:
    """Đọc các file văn bản thuần (txt, md, code, json)."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1258", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise DocumentLoadError(f"Không thể giải mã file text: {file_path}")


def _read_pdf(file_path: str) -> str:
    """Đọc file PDF theo từng trang kèm đánh dấu số trang."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages_text = []
        for idx, page in enumerate(reader.pages):
            content = page.extract_text() or ""
            if content.strip():
                pages_text.append(f"--- [Trang {idx + 1}] ---\n{content.strip()}")
        return "\n\n".join(pages_text)
    except ImportError:
        raise ImportError("Vui lòng cài đặt: pip install pypdf")


def _read_docx(file_path: str) -> str:
    """Đọc file Word docx bao gồm cả đoạn văn và bảng dữ liệu."""
    try:
        import docx
        doc = docx.Document(file_path)
        parts = []

        for p in doc.paragraphs:
            txt = p.text.strip()
            if txt:
                parts.append(txt)

        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if cells:
                    parts.append(" | ".join(cells))

        return "\n\n".join(parts)
    except ImportError:
        raise ImportError("Vui lòng cài đặt: pip install python-docx")


def _read_pptx(file_path: str) -> str:
    """Đọc file PowerPoint (Slide bài giảng)."""
    try:
        from pptx import Presentation
        prs = Presentation(file_path)
        slides_text = []
        for idx, slide in enumerate(prs.slides):
            slide_content = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text = paragraph.text.strip()
                        if text:
                            slide_content.append(text)
            if slide_content:
                slides_text.append(f"--- [Slide {idx + 1}] ---\n" + "\n".join(slide_content))
        return "\n\n".join(slides_text)
    except ImportError:
        raise ImportError("Vui lòng cài đặt: pip install python-pptx")


def _read_excel(file_path: str) -> str:
    """Đọc file Excel (.xlsx) biến đổi các sheet thành bảng văn bản."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheets_content = []
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            rows = []
            for row in sheet.iter_rows(values_only=True):
                row_vals = [str(val).strip() for val in row if val is not None and str(val).strip()]
                if row_vals:
                    rows.append(" | ".join(row_vals))
            if rows:
                sheets_content.append(f"--- [Sheet: {sheet_name}] ---\n" + "\n".join(rows))
        return "\n\n".join(sheets_content)
    except ImportError:
        raise ImportError("Vui lòng cài đặt: pip install openpyxl")


def _read_csv(file_path: str) -> str:
    """Đọc file CSV/TSV."""
    delimiter = "\t" if file_path.lower().endswith(".tsv") else ","
    rows = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            items = [col.strip() for col in row if col.strip()]
            if items:
                rows.append(" | ".join(items))
    return "\n".join(rows)


def _read_html(file_path: str) -> str:
    """Bóc tách text sạch từ file HTML, loại bỏ script/style."""
    try:
        from bs4 import BeautifulSoup
        raw_html = _read_txt_like(file_path)
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except ImportError:
        raise ImportError("Vui lòng cài đặt: pip install beautifulsoup4")


# Bản đồ định tuyến bộ parser theo định dạng file
PARSER_REGISTRY = {
    # Văn phòng
    ".pdf": _read_pdf,
    ".docx": _read_docx,
    ".pptx": _read_pptx,
    
    # Bảng tính
    ".xlsx": _read_excel,
    ".csv": _read_csv,
    ".tsv": _read_csv,
    
    # Web
    ".html": _read_html,
    ".htm": _read_html,
    
    # Văn bản & Code
    ".txt": _read_txt_like,
    ".md": _read_txt_like,
    ".markdown": _read_txt_like,
    ".json": _read_txt_like,
    ".py": _read_txt_like,
    ".js": _read_txt_like,
    ".ts": _read_txt_like,
    ".java": _read_txt_like,
    ".cpp": _read_txt_like,
    ".c": _read_txt_like,
    ".sql": _read_txt_like,
}


def load_file_content(file_path: str) -> str:
    """
    Hàm entry point duy nhất để đọc bất kỳ loại file nào được hỗ trợ.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    ext = Path(file_path).suffix.lower()
    
    if ext not in PARSER_REGISTRY:
        raise ValueError(f"Định dạng '{ext}' chưa được hỗ trợ. Các định dạng hợp lệ: {list(PARSER_REGISTRY.keys())}")

    parser = PARSER_REGISTRY[ext]
    return parser(file_path)