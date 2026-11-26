"""Versioned ingestion contracts shared by local inspection and future workers."""
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid')


class SourcePolicy(str, Enum):
    DOCUMENT_ONLY = 'DOCUMENT_ONLY'
    EXTERNAL_ALLOWED = 'EXTERNAL_ALLOWED'


class ContentOrigin(str, Enum):
    DOCUMENT_EXTRACTED = 'DOCUMENT_EXTRACTED'
    SOURCE_DERIVED = 'SOURCE_DERIVED'
    EXTERNAL_RETRIEVED = 'EXTERNAL_RETRIEVED'
    AI_GENERATED = 'AI_GENERATED'


class JobStatus(str, Enum):
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    AWAITING_REVIEW = 'AWAITING_REVIEW'
    PUBLISHING = 'PUBLISHING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class SourceSnapshot(Contract):
    material_id: UUID
    material_version_id: UUID
    source_name: str
    source_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    size_bytes: int = Field(ge=0)
    extension: str


class DocumentBlock(Contract):
    block_id: str
    kind: Literal['TEXT', 'TABLE', 'CODE', 'FORMULA', 'IMAGE']
    text: str
    locator: str
    page_or_slide: int | None = Field(default=None, ge=1)
    heading_path: list[str] = Field(default_factory=list)


class ParsedDocument(Contract):
    schema_version: Literal['parsed-document-1'] = 'parsed-document-1'
    material_version_id: UUID
    source_hash: str
    parser_version: str
    adapter: str
    blocks: list[DocumentBlock]
    warnings: list[str] = Field(default_factory=list)


class BlockSpan(Contract):
    """Offsets are Unicode code points in an immutable DocumentBlock, end-exclusive."""
    block_id: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode='after')
    def ordered(self):
        if self.end <= self.start:
            raise ValueError('Source span must be non-empty and end > start')
        return self


class ChunkProposal(Contract):
    chunk_id: UUID
    material_version_id: UUID
    chunk_index: int = Field(ge=0)
    content: str = Field(min_length=1)
    content_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    token_count: int = Field(ge=1)
    block_refs: list[BlockSpan] = Field(min_length=1)
    heading_path: list[str] = Field(default_factory=list)


class ChunkManifest(Contract):
    schema_version: Literal['chunk-manifest-1'] = 'chunk-manifest-1'
    material_version_id: UUID
    source_hash: str
    chunker_version: str
    tokenizer: str
    target_tokens: int
    max_tokens: int
    overlap_tokens: int
    chunks: list[ChunkProposal]


class SourceRef(Contract):
    source_ref_id: str
    origin: ContentOrigin
    source_id: str
    chunk_id: UUID | None = None
    span: BlockSpan | None = None
    quote: str | None = None
    url: str | None = None
    snapshot_hash: str | None = None

    @model_validator(mode='after')
    def evidence_required(self):
        if self.origin == ContentOrigin.DOCUMENT_EXTRACTED:
            if not self.chunk_id or not self.span or not self.quote:
                raise ValueError('Document evidence requires chunk_id, span and quote')
        if self.origin == ContentOrigin.EXTERNAL_RETRIEVED:
            if not self.url or not self.quote or not self.snapshot_hash:
                raise ValueError('External evidence requires URL, quote and snapshot hash')
        return self


class ExtractedFact(Contract):
    fact_id: str
    kind: Literal['DEFINITION', 'CONDITION', 'EXCEPTION', 'PROCESS', 'PROCESS_STEP',
                  'EXERCISE', 'EXERCISE_STEP', 'EXAMPLE', 'ARGUMENT', 'RELATION']
    text: str = Field(min_length=1)
    origin: ContentOrigin
    entity_local_ids: list[str] = Field(default_factory=list)
    source_ref_ids: list[str] = Field(min_length=1)
    missing_fields: list[str] = Field(default_factory=list)


class ValidationIssue(Contract):
    code: str
    severity: Literal['BLOCKER', 'ERROR', 'WARNING']
    message: str
    object_ref: str | None = None


class IntegrityReport(Contract):
    passed: bool
    block_count: int
    chunk_count: int
    covered_nonempty_blocks: int
    issues: list[ValidationIssue]
