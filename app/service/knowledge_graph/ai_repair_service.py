"""AI Knowledge Graph Auto-Repair Service using LLM (Gemini/OpenAI) with deterministic fallback."""
import json
import logging
from typing import Any

from app.schema.graph_repair import (
    AiGraphRepairRequest,
    AiGraphRepairResponse,
    AiRepairAction,
    GraphRepairEdgeItem,
    GraphRepairNodeItem,
)
from app.service.llm_service import LLMService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là Chuyên gia Kiến trúc Đồ thị Tri thức Giáo dục (Senior Curriculum Knowledge Graph Architect & Pedagogical AI).
Nhiệm vụ của bạn là phân tích đồ thị tri thức môn học đang có lỗi cấu trúc (chu trình phụ thuộc vòng lặp vô hạn, node mồ côi, thiếu mô tả) và TRỰC TIẾP SỬA MÃ JSON để trả về một đồ thị DAG chuẩn mực, hợp lệ và giàu giá trị sư phạm.

NGUYÊN TẮC SỬA ĐỒ THỊ (MINIMAL INVASIVE REPAIR):
1. Đảm bảo đồ thị kết quả TUYỆT ĐỐI KHÔNG CÓ CHU TRÌNH VÒNG LẶP (No Circular Dependencies in PREREQUISITE relations - Directed Acyclic Graph).
   - Khi phát hiện chu trình (A -> B -> C -> A), hãy ngắt cạnh phụ thuộc ngược (back-edge) hoặc đảo chiều cạnh sao cho phản ánh đúng trình tự học từ cơ bản đến nâng cao.
2. Xóa bỏ các cạnh trỏ tới node không tồn tại (Dangling edges).
3. Bổ sung mô tả ngắn gọn, chính xác (1-2 câu tiếng Việt) cho các node đang bị thiếu thuộc tính 'description'.
4. Với các node mồ côi (không có liên kết), nếu tìm thấy chủ đề liên quan trong cùng category, hãy đề xuất nối cạnh quan hệ nhẹ nhàng.
5. Giữ nguyên 100% ID, label, linkedLessonIds và các cạnh đang hợp lệ của người dùng.
6. Cung cấp 'summary' tóm tắt cách xử lý và 'changes' liệt kê cụ thể từng hành động đã can thiệp (bằng tiếng Việt).
"""


def _deterministic_fallback_repair(request: AiGraphRepairRequest) -> AiGraphRepairResponse:
    """Fallback algorithm when LLM is unavailable: breaks DFS cycles and cleans dangling edges."""
    logger.info("Executing deterministic fallback repair for knowledge graph")
    node_ids = {n.id for n in request.nodes}
    repaired_nodes: list[GraphRepairNodeItem] = []
    changes: list[AiRepairAction] = []

    # 1. Clean nodes and fill missing descriptions
    for n in request.nodes:
        n_copy = n.model_copy()
        if not n_copy.description or not n_copy.description.strip():
            n_copy.description = f"Khái niệm cốt lõi: {n_copy.label}. Định nghĩa và kiến thức nền tảng trong môn học."
            changes.append(AiRepairAction(
                action="ADD_DESCRIPTION",
                targetId=n_copy.id,
                description=f"Tự động bổ sung mô tả học thuật cho khái niệm '{n_copy.label}'"
            ))
        repaired_nodes.append(n_copy)

    # 2. Filter dangling edges & self loops
    valid_edges: list[GraphRepairEdgeItem] = []
    for e in request.edges:
        if e.source == e.target:
            changes.append(AiRepairAction(
                action="REMOVE_EDGE",
                targetId=f"{e.source}->{e.target}",
                description=f"Xóa vòng lặp tự thân trên node '{e.source}'"
            ))
            continue
        if e.source not in node_ids or e.target not in node_ids:
            changes.append(AiRepairAction(
                action="REMOVE_EDGE",
                targetId=f"{e.source}->{e.target}",
                description=f"Xóa cạnh mồ côi nối tới node không tồn tại ({e.source} -> {e.target})"
            ))
            continue
        valid_edges.append(e)

    # 3. Detect and break cycles using DFS
    adj: dict[str, list[str]] = {nid: [] for nid in node_ids}
    edge_map: dict[tuple[str, str], GraphRepairEdgeItem] = {}
    for e in valid_edges:
        rel = (e.relation or "PREREQUISITE").upper()
        if rel in ("PREREQUISITE", "REQUIRES", "DEPENDS_ON"):
            adj[e.source].append(e.target)
            edge_map[(e.source, e.target)] = e

    state: dict[str, int] = {nid: 0 for nid in node_ids}  # 0=white, 1=gray, 2=black
    edges_to_remove: set[tuple[str, str]] = set()

    def dfs(curr: str) -> None:
        state[curr] = 1
        for nxt in adj.get(curr, []):
            if (curr, nxt) in edges_to_remove:
                continue
            if state.get(nxt) == 1:
                # Cycle back-edge found! Break this edge
                edges_to_remove.add((curr, nxt))
                changes.append(AiRepairAction(
                    action="REMOVE_EDGE",
                    targetId=f"{curr}->{nxt}",
                    description=f"Ngắt cạnh phụ thuộc ngược '{curr}' -> '{nxt}' để loại bỏ chu trình lặp vô hạn"
                ))
            elif state.get(nxt) == 0:
                dfs(nxt)
        state[curr] = 2

    for nid in list(node_ids):
        if state[nid] == 0:
            dfs(nid)

    repaired_edges = [
        e for e in valid_edges
        if (e.source, e.target) not in edges_to_remove
    ]

    # 4. Synchronize node prerequisites
    prereq_map: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for e in repaired_edges:
        if (e.relation or "PREREQUISITE").upper() == "PREREQUISITE":
            if e.source not in prereq_map[e.target]:
                prereq_map[e.target].append(e.source)

    for n in repaired_nodes:
        n.prerequisites = prereq_map.get(n.id, [])

    summary = (
        f"AI đã phân tích và tự động can thiệp sửa {len(changes)} vấn đề trong đồ thị: "
        "loại bỏ toàn bộ chu trình phụ thuộc vòng, dọn sạch cạnh không hợp lệ và hoàn thiện thuộc tính mô tả."
    )

    return AiGraphRepairResponse(
        repairedNodes=repaired_nodes,
        repairedEdges=repaired_edges,
        summary=summary,
        changes=changes,
    )


async def repair_knowledge_graph_with_ai(request: AiGraphRepairRequest) -> AiGraphRepairResponse:
    """Analyzes the graph with LLM to repair cycles, orphans, and descriptions, falling back to rule engine."""
    user_prompt = f"""Dưới đây là thông tin đồ thị tri thức môn học cần sửa:
Khóa học: {request.courseTitle}
Danh sách lỗi đã phát hiện:
{json.dumps([issue.model_dump() for issue in request.issues], ensure_ascii=False, indent=2)}

Lời dặn bổ sung từ giảng viên: {request.instruction or 'Không có'}

Cấu trúc đồ thị hiện tại:
NODES:
{json.dumps([n.model_dump() for n in request.nodes], ensure_ascii=False, indent=2)}

EDGES:
{json.dumps([e.model_dump() for e in request.edges], ensure_ascii=False, indent=2)}

Hãy sửa chữa đồ thị này để trở thành một DAG hoàn toàn hợp lệ, giải quyết triệt để các lỗi trên và trả về đúng JSON Schema."""

    try:
        llm = LLMService()
        result: AiGraphRepairResponse = await llm.generate_structured_output(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=AiGraphRepairResponse,
            use_extraction_model=False,
            temperature=0.2,
        )
        if result and result.repairedNodes:
            return result
    except Exception as exc:
        logger.warning("LLM graph repair invocation encountered error or credentials missing: %s. Using deterministic fallback.", exc)

    return _deterministic_fallback_repair(request)
