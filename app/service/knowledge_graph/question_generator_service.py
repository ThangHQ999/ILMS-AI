"""AI RAG Question Generator Service for ILMS Question Bank."""
from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_questions_with_ai(payload: dict[str, Any]) -> dict[str, Any]:
    course_title = payload.get("courseTitle") or "Học phần"
    topic = payload.get("topic") or course_title
    difficulty = (payload.get("difficultyLevel") or "MEDIUM").upper()
    q_type = (payload.get("questionType") or "SINGLE_CHOICE").upper()
    bloom = (payload.get("bloomLevel") or "UNDERSTAND").upper()
    count = max(1, min(int(payload.get("count") or 5), 20))
    custom_prompt = payload.get("customPrompt") or ""
    concepts = payload.get("concepts") or []
    chunks = payload.get("chunks") or []

    prompt = (
        f"Bạn là chuyên gia biên soạn đề thi đại học cho môn '{course_title}'.\n"
        f"Hãy tạo đúng {count} câu hỏi trắc nghiệm bằng tiếng Việt.\n"
        f"- Chủ đề: {topic}\n"
        f"- Độ khó: {difficulty} (EASY/MEDIUM/HARD)\n"
        f"- Loại câu hỏi: {q_type} (SINGLE_CHOICE/MULTIPLE_CHOICE/TRUE_FALSE)\n"
        f"- Mức độ nhận thức Bloom: {bloom} (REMEMBER/UNDERSTAND/APPLY/ANALYZE/EVALUATE/CREATE)\n"
        f"- Yêu cầu bổ sung: {custom_prompt}\n"
        f"- Các khái niệm trọng tâm: {json.dumps(concepts, ensure_ascii=False)}\n"
        f"- Trích đoạn học liệu gốc (RAG): {json.dumps(chunks[:5], ensure_ascii=False)}\n\n"
        "Trả về JSON object với đúng định dạng:\n"
        '{"questions": [{"content": "...", "questionType": "...", "difficultyLevel": "...", '
        '"bloomLevel": "...", "optionA": "...", "optionB": "...", "optionC": "...", "optionD": "...", '
        '"correctAnswer": "A", "explanation": "...", "tags": ["..."], '
        '"concepts": [{"conceptId": "...", "name": "..."}]}]}'
    )

    api_key = getattr(settings, "GEMINI_API_KEY", None) or getattr(settings, "GOOGLE_API_KEY", None)
    if api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                ),
            )
            if resp and resp.text:
                parsed = json.loads(resp.text)
                if isinstance(parsed, dict) and isinstance(parsed.get("questions"), list):
                    return parsed
        except Exception as exc:
            logger.warning("Gemini question generation failed, falling back to structured template: %s", exc)

    # Fallback synthesis from RAG chunks and KG concepts
    questions = []
    for idx in range(count):
        concept = concepts[idx % len(concepts)] if concepts else {"id": f"CONCEPT_{idx + 1}", "name": topic, "description": ""}
        c_name = concept.get("name") or topic
        c_id = concept.get("id") or c_name
        c_desc = concept.get("description") or (chunks[idx % len(chunks)][:180] if chunks else f"Nguyên lý trọng tâm của {c_name} trong {course_title}.")

        questions.append({
            "content": f"[{bloom}] Trong học phần {course_title}, phát biểu nào sau đây phản ánh chính xác nhất về '{c_name}'?",
            "questionType": q_type,
            "difficultyLevel": difficulty,
            "bloomLevel": bloom,
            "optionA": c_desc,
            "optionB": "Chỉ áp dụng cho tập dữ liệu tĩnh mà không xét đến điều kiện biên.",
            "optionC": "Bỏ qua hoàn toàn các ràng buộc toàn vẹn để giảm chi phí tính toán.",
            "optionD": "Hoạt động tách biệt, không có mối liên hệ với các khái niệm tiên quyết.",
            "correctAnswer": "A",
            "explanation": f"Theo học liệu của môn {course_title}: {c_desc}",
            "tags": [course_title, c_name, bloom],
            "concepts": [{"conceptId": c_id, "name": c_name}],
        })

    return {"questions": questions}
