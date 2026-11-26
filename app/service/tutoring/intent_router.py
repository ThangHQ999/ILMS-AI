from collections.abc import AsyncGenerator
# Ví dụ tích hợp với openai-python (hoặc google-genai)
from openai import AsyncOpenAI

client = AsyncOpenAI()

SYSTEM_PROMPT = """
Bạn là một AI Tutor kiên nhẫn và tận tâm.
Nguyên tắc sư phạm:
1. Phương pháp Socratic: Đặt câu hỏi gợi mở từng bước thay vì đưa ngay đáp án cuối cùng.
2. Động viên và sửa lỗi sai nhẹ nhàng, giải thích cặn kẽ bản chất vấn đề.
3. Sử dụng định dạng Markdown rõ ràng, dùng công thức toán hoặc khối code khi cần.
"""

async def stream_tutor_response(history: list[dict], user_message: str) -> AsyncGenerator[str, None]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model="gpt-6-luna",
        messages=messages,
        stream=True,
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content