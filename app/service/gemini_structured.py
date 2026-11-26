import asyncio
import os
from google import genai
from google.genai import types

from schemas.graph import KnowledgeGraphExtraction
from src.core.prompts import CUSTOM_SYSTEM_PROMPT

_gemini_api_lock = asyncio.Lock()

async def gemini_extract_kg(prompt: str) -> str:
    """
    Hàm gọi Gemini độc lập chuyên dùng để trích xuất JSON.
    Đã nâng cấp lên SDK google-genai. Áp dụng cơ chế chặn luồng và Pydantic Schema.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Chưa cấu hình GEMINI_API_KEY trong .env")

    # 1. Khởi tạo Client theo chuẩn SDK mới
    client = genai.Client(api_key=api_key)
    
    model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")

    # 2. Gom toàn bộ System Prompt, Schema và Temperature vào GenerateContentConfig
    config = types.GenerateContentConfig(
        system_instruction=CUSTOM_SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=KnowledgeGraphExtraction,
        temperature=0.0,
    )
    
    # 3. Sử dụng block `async with` để chặn luồng
    # Bất kỳ task nào gọi đến đây đều phải xếp hàng đợi task trước đó chạy xong
    async with _gemini_api_lock:
        
        # Gọi API bất đồng bộ qua thuộc tính .aio
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        
        # Nghỉ một nhịp trước khi nhả Lock cho task tiếp theo (Rate Limiting)
        # Giữ nguyên 30.0 giây để tuân thủ 15 request/phút của Free tier
        await asyncio.sleep(30.0) 
        
        return response.text