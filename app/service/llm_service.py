from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager
import logging
import math
from typing import Any, Literal, TypeVar
from google import genai
from google.genai import types as genai_types
from openai import AsyncOpenAI
from pydantic import BaseModel
from app.core.config import settings
from app.service.ingestion.benchmark_usage import record_openai_usage

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
ProviderType = Literal["gemini", "openai"]


class LLMService:
    """
    Service tích hợp song song cả Google Gemini (`google-genai` SDK) và OpenAI (`AsyncOpenAI` SDK).
    Cung cấp 3 năng lực cốt lõi cho toàn hệ thống:
    1. `embed_texts`: Tạo vector embeddings cho MaterialChunk và câu hỏi của học sinh.
    2. `generate_structured_output`: Ép kiểu JSON theo Pydantic Schema (dùng cho AI trích xuất 7 loại Node Neo4j & đánh giá bước Socratic).
    3. `stream_chat_completion`: Stream từng token thời gian thực qua SSE về cho Spring Boot -> FE.
    Hỗ trợ tự động chuyển đổi dự phòng (Fallback) giữa Gemini và OpenAI nếu một bên gặp sự cố.
    """

    def __init__(self, *, quiet: bool = False) -> None:
        self._quiet = quiet
        self._openai_client: AsyncOpenAI | None = None
        self._gemini_client: genai.Client | None = None

        if settings.OPENAI_API_KEY:
            self._openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                timeout=settings.LLM_REQUEST_TIMEOUT,
                max_retries=settings.LLM_MAX_RETRIES,
            )

        if settings.GEMINI_API_KEY:
            self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    @asynccontextmanager
    async def managed(self):
        """Close owned SDK clients on the event loop that used them."""
        async with AsyncExitStack() as stack:
            if self._openai_client is not None:
                stack.push_async_callback(self._openai_client.close)
            if self._gemini_client is not None:
                stack.callback(self._gemini_client.close)
                stack.push_async_callback(self._gemini_client.aio.aclose)
            yield self

    def _resolve_provider_order(
        self,
        preferred: ProviderType | None = None,
        for_embedding: bool = False,
    ) -> list[ProviderType]:
        """Xác định thứ tự ưu tiên gọi provider (kèm fallback nếu bật LLM_ENABLE_FALLBACK)."""
        if for_embedding and preferred and preferred != settings.EMBEDDING_PROVIDER:
            raise ValueError('Embedding provider is fixed for the configured collection')
        primary: ProviderType = preferred or (
            settings.EMBEDDING_PROVIDER if for_embedding else settings.LLM_DEFAULT_PROVIDER
        )
        secondary: ProviderType = "openai" if primary == "gemini" else "gemini"

        order: list[ProviderType] = [primary]
        if settings.LLM_ENABLE_FALLBACK and not for_embedding:
            order.append(secondary)

        available: list[ProviderType] = []
        for p in order:
            if p == "openai" and self._openai_client is not None:
                available.append("openai")
            elif p == "gemini" and self._gemini_client is not None:
                available.append("gemini")

        if not available:
            raise RuntimeError(
                "Chưa cấu hình GEMINI_API_KEY hoặc OPENAI_API_KEY hợp lệ trong file .env."
            )
        return available

    def model_for(self, provider: ProviderType, task: str) -> str:
        prefix = provider.upper()
        field = {'intent': 'INTENT', 'evaluation': 'EVALUATION',
                 'question': 'QUESTION', 'artifact': 'ARTIFACT'}.get(task)
        configured = getattr(settings, f'{prefix}_{field}_MODEL', None) if field else None
        return configured or getattr(settings, f'{prefix}_CHAT_MODEL')

    @staticmethod
    def _validate_embeddings(vectors: list[list[float]], count: int) -> list[list[float]]:
        if len(vectors) != count or any(len(v) != settings.active_embedding_dimension for v in vectors):
            raise ValueError('Embedding count/dimension differs from configured index identity')
        if any(not math.isfinite(x) for vector in vectors for x in vector):
            raise ValueError('Embedding contains non-finite values')
        return vectors

    # ========================================================================
    # 1. TẠO VECTOR EMBEDDINGS (OPENAI / GEMINI)
    # ========================================================================
    async def embed_texts(
        self,
        texts: list[str],
        provider: ProviderType | None = None,
        *,
        allow_fallback: bool = True,
    ) -> list[list[float]]:
        """
        Sinh vector embeddings cho danh sách văn bản.
        Lưu ý: Nên cố định 1 `EMBEDDING_PROVIDER` trong `.env` cho mỗi Chroma Collection
        để đảm bảo số chiều vector (dimensions) đồng nhất.
        """
        if not texts:
            return []

        providers = (self._resolve_provider_order(preferred=provider, for_embedding=True)
                     if allow_fallback else [provider or settings.EMBEDDING_PROVIDER])
        last_error: Exception | None = None

        for p in providers:
            try:
                if p == "openai" and self._openai_client is not None:
                    response = await self._openai_client.embeddings.create(
                        model=settings.OPENAI_EMBEDDING_MODEL,
                        input=texts,
                        dimensions=settings.OPENAI_EMBEDDING_DIMENSION,
                    )
                    record_openai_usage(settings.OPENAI_EMBEDDING_MODEL, response.usage, embedding=True)
                    return self._validate_embeddings([item.embedding for item in response.data], len(texts))

                if p == "gemini" and self._gemini_client is not None:
                    response = await self._gemini_client.aio.models.embed_content(
                        model=settings.GEMINI_EMBEDDING_MODEL,
                        contents=texts,
                        config=genai_types.EmbedContentConfig(output_dimensionality=settings.GEMINI_EMBEDDING_DIMENSION),
                    )
                    if not response.embeddings:
                        raise RuntimeError("Gemini trả về danh sách embeddings rỗng.")
                    return self._validate_embeddings([list(emb.values or []) for emb in response.embeddings], len(texts))
            except Exception as exc:
                last_error = exc
                if not self._quiet:
                    logger.warning("Lỗi khi tạo embedding với provider '%s': %s", p, exc)

        raise RuntimeError(f"Không thể tạo vector embedding từ cả Gemini và OpenAI: {last_error}")

    # ========================================================================
    # 2. STRUCTURED OUTPUTS (ÉP KIỂU PYDANTIC SCHEMA CHO KG EXTRACTION)
    # ========================================================================
    async def generate_ingestion_output(
        self, *, system_prompt: str, user_prompt: str, response_schema: type[T],
        model: str, temperature: float, reasoning_effort: str, max_output_tokens: int,
    ) -> T:
        if self._openai_client is None:
            raise RuntimeError('OpenAI credentials are required for ingestion')
        options: dict[str, Any] = {}
        if temperature != 1:
            options['temperature'] = temperature
        if model.startswith('gpt-6-'):
            options['reasoning_effort'] = reasoning_effort if temperature == 1 else 'none'
        completion = await self._openai_client.beta.chat.completions.parse(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            response_format=response_schema,
            max_completion_tokens=max_output_tokens,
            **options,
        )
        record_openai_usage(model, completion.usage)
        result = completion.choices[0].message.parsed
        if result is None:
            raise ValueError('Ingestion model did not return the required structured result')
        return result

    async def generate_structured_output(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        provider: ProviderType | None = None,
        use_extraction_model: bool = True,
        temperature: float = 0.1,
        task: str | None = None,
    ) -> T:
        """
        Gọi Gemini hoặc OpenAI và ép đầu ra trả về đúng đối tượng Pydantic `response_schema`
        (VD: `ChunkKnowledgeGraphLLMOutput` gồm 7 loại Node + 22 cạnh `RelationLabel`).
        """
        providers = self._resolve_provider_order(preferred=provider, for_embedding=False)
        last_error: Exception | None = None

        for p in providers:
            try:
                if p == "gemini" and self._gemini_client is not None:
                    model_name = (
                        settings.GEMINI_EXTRACTION_MODEL
                        if use_extraction_model
                        else settings.GEMINI_CHAT_MODEL
                    )
                    if task:
                        model_name = self.model_for('gemini', task)
                    response = await self._gemini_client.aio.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=genai_types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=temperature,
                            response_mime_type="application/json",
                            response_schema=response_schema,
                        ),
                    )
                    if getattr(response, "parsed", None) is not None and isinstance(
                        response.parsed, response_schema
                    ):
                        return response.parsed
                    raw_text = response.text or "{}"
                    return response_schema.model_validate_json(raw_text)

                if p == "openai" and self._openai_client is not None:
                    model_name = (
                        settings.OPENAI_EXTRACTION_MODEL
                        if use_extraction_model
                        else settings.OPENAI_CHAT_MODEL
                    )
                    if task:
                        model_name = self.model_for('openai', task)
                    completion = await self._openai_client.beta.chat.completions.parse(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        response_format=response_schema,
                        **({'temperature': temperature} if settings.OPENAI_SEND_TEMPERATURE else {}),
                    )
                    record_openai_usage(model_name, completion.usage)
                    parsed_obj = completion.choices[0].message.parsed
                    if parsed_obj is not None:
                        return parsed_obj
                    raw_content = completion.choices[0].message.content or "{}"
                    return response_schema.model_validate_json(raw_content)

            except Exception as exc:
                last_error = exc
                if not self._quiet:
                    logger.warning(
                        "Lỗi khi gọi Structured Output (%s) với provider '%s': %s",
                        response_schema.__name__,
                        p,
                        exc,
                    )

        raise RuntimeError(
            f"Cả Gemini và OpenAI đều thất bại khi trích xuất cấu trúc {response_schema.__name__}: {last_error}"
        )

    # ========================================================================
    # 3. STREAMING CHAT COMPLETION (PHỤC VỤ SOCRATIC TUTOR SSE)
    # ========================================================================
    async def stream_chat_completion(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, str]],
        provider: ProviderType | None = None,
        temperature: float = 0.4,
    ) -> AsyncGenerator[str, None]:
        """
        Stream từng cụm văn bản (delta token) từ Gemini hoặc OpenAI.
        Tự động fallback sang provider còn lại nếu lỗi xảy ra khi mở kết nối stream.
        """
        providers = self._resolve_provider_order(preferred=provider, for_embedding=False)
        last_error: Exception | None = None

        for p in providers:
            emitted = False
            try:
                if p == "gemini" and self._gemini_client is not None:
                    gemini_contents: list[genai_types.Content] = []
                    for msg in messages:
                        role_raw = msg.get("role", "user").lower()
                        gemini_role = "model" if role_raw in ("assistant", "model") else "user"
                        gemini_contents.append(
                            genai_types.Content(
                                role=gemini_role,
                                parts=[genai_types.Part.from_text(text=msg.get("content", ""))],
                            )
                        )

                    stream = await self._gemini_client.aio.models.generate_content_stream(
                        model=settings.GEMINI_CHAT_MODEL,
                        contents=gemini_contents,
                        config=genai_types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=temperature,
                        ),
                    )
                    async for chunk in stream:
                        if chunk.text:
                            emitted = True
                            yield chunk.text
                    return

                if p == "openai" and self._openai_client is not None:
                    openai_messages: list[dict[str, Any]] = [
                        {"role": "system", "content": system_prompt}
                    ]
                    for msg in messages:
                        role_raw = msg.get("role", "user").lower()
                        norm_role = (
                            "assistant"
                            if role_raw == "assistant"
                            else ("system" if role_raw == "system" else "user")
                        )
                        openai_messages.append(
                            {"role": norm_role, "content": msg.get("content", "")}
                        )

                    stream = await self._openai_client.chat.completions.create(
                        model=settings.OPENAI_CHAT_MODEL,
                        messages=openai_messages,  # type: ignore[arg-type]
                        stream=True,
                        **({'temperature': temperature} if settings.OPENAI_SEND_TEMPERATURE else {}),
                    )
                    async for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            emitted = True
                            yield chunk.choices[0].delta.content
                    return

            except Exception as exc:
                last_error = exc
                logger.warning("Lỗi khi stream SSE với provider '%s': %s", p, exc)
                if emitted:
                    raise RuntimeError('Stream interrupted after output began; provider fallback is disabled') from exc

        raise RuntimeError(f"Không thể khởi tạo luồng stream từ cả Gemini và OpenAI: {last_error}")


llm_service = LLMService()
