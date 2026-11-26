import os
from openai import AsyncOpenAI

from src.schemas.schemas import KnowledgeGraphExtraction
from src.core.prompts import CUSTOM_SYSTEM_PROMPT

async def openai_extract_kg(prompt: str, file_name: str) -> str:
    """
    Hàm gọi OpenAI (bất đồng bộ) chuyên dùng để trích xuất JSON.
    Đã gỡ bỏ cơ chế khóa luồng, cho phép chạy song song thoải mái.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Chưa cấu hình OPENAI_API_KEY trong .env")

    client = AsyncOpenAI(api_key=api_key)
    
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

    user_prompt = f"""
    [NGỮ CẢNH TOÀN CỤC]: Đoạn văn dưới đây được trích từ tài liệu: "{file_name}".
    (LƯU Ý: Tên tài liệu này chỉ để cung cấp ngữ cảnh định hướng. Hãy dựa vào NỘI DUNG THỰC TẾ của trích đoạn để quyết định tên Thực thể).

    YÊU CẦU:
    1. Tự tìm Khái niệm/Thực thể cốt lõi xuất hiện TRONG NỘI DUNG đoạn văn.
    2. Nếu đoạn văn bị cắt lẻ và CHỈ CHỨA Bài tập/Ví dụ (không nhắc đến tên Khái niệm chính), hãy kết hợp nội dung đó với "[Ngữ cảnh toàn cục]" ở trên để suy luận xem Bài tập/Ví dụ này thuộc về Khái niệm nào, từ đó gán tên Thực thể cho đúng.

    [NỘI DUNG TRÍCH ĐOẠN CẦN PHÂN TÍCH]:
    {prompt}
    """
    
    response = await client.beta.chat.completions.parse(
        model=model_name,
        messages=[
            {"role": "system", "content": CUSTOM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format=KnowledgeGraphExtraction,
        temperature=0.0,
    )
   
    return response.choices[0].message.content