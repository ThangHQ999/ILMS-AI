"""Standalone preprocessing settings: no dependency on chat credentials or DBs."""
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parents[3]


class IngestionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / '.env'), env_file_encoding='utf-8',
        env_prefix='INGESTION_', case_sensitive=False, extra='ignore',
    )

    allowed_extensions: str = 'pdf,docx,pptx,txt,md,py,js,ts,java,go,sql'
    max_file_mb: int = Field(default=30, ge=1, le=1024)
    max_pages: int = Field(default=300, ge=1)
    max_slides: int = Field(default=300, ge=1)
    max_parsed_characters: int = Field(default=2_000_000, ge=1)
    max_chunks: int = Field(default=1500, ge=1)
    text_encoding: str = 'utf-8-sig'
    ocr_enabled: bool = False
    max_archive_uncompressed_mb: int = Field(default=200, ge=1)
    chunk_target_tokens: int = Field(default=800, ge=16)
    chunk_strategy: Literal['semantic', 'structural'] = 'semantic'
    semantic_min_similarity: float = Field(default=0.60, ge=-1, le=1)
    semantic_min_chunk_tokens: int = Field(default=160, ge=1)
    extraction_window_tokens: int = Field(default=32000, ge=1024)
    extraction_max_output_tokens: int = Field(default=8000, ge=256)
    extractor_temperature: float = Field(default=1, ge=0, le=2)
    expert_temperature: float = Field(default=1, ge=0, le=2)
    validator_temperature: float = Field(default=0, ge=0, le=2)
    reviewer_temperature: float = Field(default=1, ge=0, le=2)
    expert_batch_claims: int = Field(default=32, ge=8, le=96)
    publication_collection: str = 'ilms-publications-1'
    publication_embedding_batch: int = Field(default=32, ge=1, le=128)
    default_temperature_model: str = 'gpt-4o-mini'
    custom_temperature_model: str = 'gpt-4o-mini'
    luna_reasoning_effort: Literal['none', 'low', 'medium', 'high'] = 'low'
    api_parallel_chunks: int = Field(default=3, ge=1, le=8)
    chunk_max_tokens: int = Field(default=1200, ge=16)
    chunk_overlap_tokens: int = Field(default=100, ge=0)
    tokenizer_encoding: str = 'cl100k_base'
    parser_version: str = 'parser-1'
    chunker_version: str = 'chunker-1'

    @model_validator(mode='after')
    def chunk_limits(self):
        if not self.chunk_overlap_tokens < self.chunk_target_tokens <= self.chunk_max_tokens:
            raise ValueError('Require overlap < target tokens <= maximum tokens')
        if not self.extensions:
            raise ValueError('INGESTION_ALLOWED_EXTENSIONS must not be empty')
        if self.ocr_enabled:
            raise ValueError('OCR adapter is not implemented in this package; keep INGESTION_OCR_ENABLED=false')
        return self

    @property
    def extensions(self) -> set[str]:
        return {x.strip().lower().lstrip('.') for x in self.allowed_extensions.split(',') if x.strip()}
