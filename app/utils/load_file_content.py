import os
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    raise ImportError("Vui lòng cài đặt thư viện: pip install markitdown")

class DocumentLoadError(Exception):
    pass

def _read_txt_like(file_path: str) -> str:
    """
    Đọc các file văn bản thuần và Code (.txt, .md, .py, .js...).
    Giữ nguyên định dạng gốc để LLM không bị mất lề (indentation).
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1258", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise DocumentLoadError(f"Không thể giải mã file text/code: {file_path}")

def _read_with_markitdown(file_path: str) -> str:
    """
    Vũ khí tối thượng: Dùng MarkItDown xử lý mọi định dạng tài liệu phức tạp.
    Tự động chuyển Word, PDF, Excel, PPTX, HTML thành Markdown chuẩn 100%.
    Bảo toàn hoàn hảo Bảng biểu (Tables) và Tiêu đề (Headers).
    """
    try:
        md = MarkItDown()
        result = md.convert(file_path)
        
        text_content = result.text_content
        if not text_content or not text_content.strip():
            raise DocumentLoadError(f"MarkItDown không trích xuất được nội dung (File rỗng hoặc PDF dạng ảnh): {file_path}")
            
        return text_content
    except Exception as e:
        raise DocumentLoadError(f"Lỗi MarkItDown khi xử lý file {file_path}: {str(e)}")

PARSER_REGISTRY = {
    ".pdf": _read_with_markitdown,
    ".docx": _read_with_markitdown,
    ".pptx": _read_with_markitdown,
    ".xlsx": _read_with_markitdown,
    ".csv": _read_with_markitdown,
    ".tsv": _read_with_markitdown,
    ".html": _read_with_markitdown,
    ".htm": _read_with_markitdown,
    
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
    Kết quả trả về luôn là Markdown hoặc Text thuần đã được chuẩn hóa.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    ext = Path(file_path).suffix.lower()
    
    if ext not in PARSER_REGISTRY:
        valid_exts = ", ".join(PARSER_REGISTRY.keys())
        raise ValueError(f"Định dạng '{ext}' chưa được hỗ trợ. Các định dạng hợp lệ: {valid_exts}")

    parser = PARSER_REGISTRY[ext]
    return parser(file_path)
