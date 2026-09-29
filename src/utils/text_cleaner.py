import re

def sanitize_text(text: str) -> str:
    """
    Tiền xử lý dữ liệu: làm sạch các ký tự lạ, regex
    """
    if not text:
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()