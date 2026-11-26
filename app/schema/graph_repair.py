"""Schema for AI Knowledge Graph Validation and Auto-Repair."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class GraphValidationIssue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str = Field(..., description="Unique issue code, e.g. ERR_CYCLE_01")
    code: str = Field(..., description="Issue type code, e.g. CYCLE_DETECTED, ORPHAN_NODE")
    severity: Literal["BLOCKER", "WARNING", "INFO"] = "BLOCKER"
    targetId: str | None = Field(default=None, description="Affected node or edge ID")
    targetType: Literal["NODE", "EDGE", "GRAPH"] = "GRAPH"
    message: str = Field(..., description="Human-readable description in Vietnamese")
    suggestion: str | None = Field(default=None, description="Suggested action to resolve issue")


class AiRepairAction(BaseModel):
    model_config = ConfigDict(extra='ignore')

    action: Literal["REMOVE_EDGE", "REVERSE_EDGE", "ADD_DESCRIPTION", "LINK_ORPHAN", "NORMALIZE_LEVEL", "OTHER"]
    targetId: str = Field(..., description="Target node ID or edge source->target")
    description: str = Field(..., description="Explanation of what was repaired and why in Vietnamese")


class GraphRepairNodeItem(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    label: str
    description: str | None = None
    level: str | None = "BEGINNER"
    category: str | None = "General"
    prerequisites: list[str] = Field(default_factory=list)
    linkedLessonIds: list[str] = Field(default_factory=list)


class GraphRepairEdgeItem(BaseModel):
    model_config = ConfigDict(extra='ignore')

    source: str
    target: str
    relation: str = "PREREQUISITE"


class AiGraphRepairRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')

    courseTitle: str = Field(default="Course", description="Title of the course")
    nodes: list[GraphRepairNodeItem] = Field(default_factory=list)
    edges: list[GraphRepairEdgeItem] = Field(default_factory=list)
    issues: list[GraphValidationIssue] = Field(default_factory=list)
    instruction: str | None = Field(default=None, description="Optional extra instructions from teacher")


class AiGraphRepairResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    repairedNodes: list[GraphRepairNodeItem]
    repairedEdges: list[GraphRepairEdgeItem]
    summary: str = Field(..., description="Overview of the repair strategy in Vietnamese")
    changes: list[AiRepairAction] = Field(default_factory=list)
