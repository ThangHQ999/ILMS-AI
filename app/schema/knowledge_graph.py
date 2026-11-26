"""Internal graph management contracts. Public authorization belongs to Spring Boot."""
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GraphOperation(BaseModel):
    model_config = ConfigDict(extra='forbid')

    op: Literal['CREATE_NODE', 'UPDATE_NODE', 'DELETE_NODE', 'MOVE_NODE',
                'CREATE_EDGE', 'UPDATE_EDGE', 'DELETE_EDGE',
                'LINK_TOPIC_CHUNK', 'UNLINK_TOPIC_CHUNK']
    nodeId: str | None = None
    edgeId: str | None = None
    kind: str | None = None
    parentId: str | None = None
    newParentId: str | None = None
    fromNodeId: str | None = None
    toNodeId: str | None = None
    chunkId: UUID | None = None
    cascade: bool = False
    fields: dict[str, Any] = Field(default_factory=dict)

    @field_validator('fields', mode='before')
    @classmethod
    def empty_fields(cls, value):
        return {} if value is None else value


class GraphEditRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    jobId: UUID
    revisionId: UUID
    graph: dict[str, Any] | None = None
    operations: list[GraphOperation] = Field(default_factory=list, max_length=200)


class GraphViewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    jobId: UUID
    revisionId: UUID
    includeSolutions: bool = False
    nodeId: str | None = None
    canonicalCode: str | None = Field(default=None, max_length=128)
    depth: int = Field(default=2, ge=0, le=4)
    limit: int = Field(default=200, ge=1, le=500)
    after: str | None = None


class ConceptCatalogRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    courseId: UUID
    publicationIds: list[UUID] = Field(max_length=100)


class PublishedConcept(BaseModel):
    canonicalCode: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1)


class ConceptCatalogResponse(BaseModel):
    courseId: UUID
    concepts: list[PublishedConcept]
