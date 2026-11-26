from app.model.enums import NodeLabelEnum, RelationLabel
from app.model.neo4j.relationships import (
    PedagogyRelationTypeEnum,
    VALID_ENTITY_RELATION_LABELS,
)

# ============================================================================
# 1. CYPHER CHO NODE TÂM :KnowledgeEntity
# ============================================================================
MERGE_KNOWLEDGE_ENTITY_CYPHER = """
MERGE (ke:KnowledgeEntity {canonical_code: $canonical_code})
ON CREATE SET
    ke.name = $name,
    ke.subject = $subject,
    ke.source_chunk_id = $source_chunk_id,
    ke.created_at = $created_at,
    ke.updated_at = $updated_at
ON MATCH SET
    ke.name = COALESCE($name, ke.name),
    ke.subject = COALESCE($subject, ke.subject),
    ke.updated_at = $updated_at
RETURN properties(ke) AS entity
"""

GET_KNOWLEDGE_ENTITY_BY_CODE_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})
RETURN properties(ke) AS entity
"""

SEARCH_KNOWLEDGE_ENTITIES_CYPHER = """
MATCH (ke:KnowledgeEntity)
WHERE ($subject IS NULL OR ke.subject = $subject)
  AND (
    toLower(ke.canonical_code) CONTAINS toLower($keyword)
    OR toLower(ke.name) CONTAINS toLower($keyword)
  )
RETURN properties(ke) AS entity
ORDER BY ke.canonical_code ASC
LIMIT $limit
"""


# ============================================================================
# 2. CYPHER NỐI CẠNH NGỮ NGHĨA GIỮA 2 :KnowledgeEntity (22 NHÃN RelationLabel)
# ============================================================================
def build_merge_entity_relation_cypher(relation_label: RelationLabel) -> str:
    """
    Sinh câu lệnh Cypher MERGE cạnh nối giữa 2 :KnowledgeEntity.
    Kiểm tra nghiêm ngặt `relation_label` nằm trong `VALID_ENTITY_RELATION_LABELS` (22 nhãn)
    để ngăn chặn tuyệt đối Cypher Injection.
    """
    if relation_label not in VALID_ENTITY_RELATION_LABELS:
        raise ValueError(f"RelationLabel không hợp lệ: {relation_label}")

    return f"""
    MATCH (source:KnowledgeEntity {{canonical_code: $source_canonical_code}})
    MATCH (target:KnowledgeEntity {{canonical_code: $target_canonical_code}})
    MERGE (source)-[r:{relation_label}]->(target)
    ON CREATE SET
        r.description = $description,
        r.confidence = $confidence,
        r.source_chunk_id = $source_chunk_id,
        r.owner_id = $owner_id,
        r.scope = $scope,
        r.created_at = $created_at
    ON MATCH SET
        r.description = COALESCE($description, r.description),
        r.confidence = $confidence,
        r.source_chunk_id = COALESCE($source_chunk_id, r.source_chunk_id)
    RETURN
        source.canonical_code AS source_canonical_code,
        type(r) AS relation_label,
        target.canonical_code AS target_canonical_code,
        target.name AS target_name,
        properties(r) AS rel_props
    """


GET_ENTITY_OUTGOING_RELATIONS_CYPHER = """
MATCH (source:KnowledgeEntity {canonical_code: $canonical_code})-[r]->(target:KnowledgeEntity)
WHERE r.scope = 'GLOBAL' OR ($teacher_id IS NOT NULL AND r.scope = 'TEACHER' AND r.owner_id = $teacher_id)
RETURN
    source.canonical_code AS source_canonical_code,
    type(r) AS relation_label,
    target.canonical_code AS target_canonical_code,
    target.name AS target_name,
    properties(r) AS rel_props
ORDER BY CASE WHEN r.scope = 'TEACHER' THEN 0 ELSE 1 END, type(r) ASC
"""

GET_ENTITY_INCOMING_RELATIONS_CYPHER = """
MATCH (source:KnowledgeEntity)-[r]->(target:KnowledgeEntity {canonical_code: $canonical_code})
WHERE r.scope = 'GLOBAL' OR ($teacher_id IS NOT NULL AND r.scope = 'TEACHER' AND r.owner_id = $teacher_id)
RETURN
    source.canonical_code AS source_canonical_code,
    type(r) AS relation_label,
    target.canonical_code AS target_canonical_code,
    source.name AS target_name,
    properties(r) AS rel_props
ORDER BY CASE WHEN r.scope = 'TEACHER' THEN 0 ELSE 1 END, type(r) ASC
"""


# ============================================================================
# 3. CYPHER CHO 4 NODE SƯ PHẠM VỆ TINH (:Definition, :Example, :Exercise, :Argument)
# Ưu tiên lấy bản riêng của Giáo viên (scope='TEACHER') trước bản chuẩn Admin (scope='GLOBAL')
# ============================================================================
MERGE_DEFINITION_NODE_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})
MERGE (d:Definition {id: $id})
ON CREATE SET
    d.content = $content,
    d.conditions = $conditions,
    d.exceptions = $exceptions,
    d.owner_id = $owner_id,
    d.scope = $scope,
    d.source_chunk_id = $source_chunk_id,
    d.created_at = $created_at,
    d.updated_at = $updated_at
ON MATCH SET
    d.content = $content,
    d.conditions = $conditions,
    d.exceptions = $exceptions,
    d.scope = $scope,
    d.updated_at = $updated_at
MERGE (ke)-[:HAS_DEFINITION]->(d)
RETURN properties(d) AS node
"""

MERGE_EXAMPLE_NODE_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})
MERGE (ex:Example {id: $id})
ON CREATE SET
    ex.title = $title,
    ex.code_snippet = $code_snippet,
    ex.explanation = $explanation,
    ex.owner_id = $owner_id,
    ex.scope = $scope,
    ex.source_chunk_id = $source_chunk_id,
    ex.created_at = $created_at,
    ex.updated_at = $updated_at
ON MATCH SET
    ex.title = $title,
    ex.code_snippet = $code_snippet,
    ex.explanation = $explanation,
    ex.scope = $scope,
    ex.updated_at = $updated_at
MERGE (ke)-[:HAS_EXAMPLE]->(ex)
RETURN properties(ex) AS node
"""

MERGE_EXERCISE_NODE_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})
MERGE (exer:Exercise {id: $id})
ON CREATE SET
    exer.title = $title,
    exer.content = $content,
    exer.difficulty = $difficulty,
    exer.owner_id = $owner_id,
    exer.scope = $scope,
    exer.source_chunk_id = $source_chunk_id,
    exer.created_at = $created_at,
    exer.updated_at = $updated_at
ON MATCH SET
    exer.title = $title,
    exer.content = $content,
    exer.difficulty = $difficulty,
    exer.scope = $scope,
    exer.updated_at = $updated_at
MERGE (ke)-[:HAS_EXERCISE]->(exer)
WITH exer
OPTIONAL MATCH (p:Process {id: $process_id})
FOREACH (_ IN CASE WHEN p IS NOT NULL THEN [1] ELSE [] END |
    MERGE (exer)-[:USES_PROCESS]->(p)
)
RETURN properties(exer) AS node
"""

MERGE_ARGUMENT_NODE_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})
MERGE (arg:Argument {id: $id})
ON CREATE SET
    arg.hypothesis = $hypothesis,
    arg.evidence = $evidence,
    arg.conclusion = $conclusion,
    arg.owner_id = $owner_id,
    arg.scope = $scope,
    arg.source_chunk_id = $source_chunk_id,
    arg.created_at = $created_at,
    arg.updated_at = $updated_at
ON MATCH SET
    arg.hypothesis = $hypothesis,
    arg.evidence = $evidence,
    arg.conclusion = $conclusion,
    arg.scope = $scope,
    arg.updated_at = $updated_at
MERGE (ke)-[:HAS_ARGUMENT]->(arg)
RETURN properties(arg) AS node
"""


def build_get_satellite_nodes_cypher(
    node_label: NodeLabelEnum,
    rel_type: PedagogyRelationTypeEnum,
) -> str:
    """
    Sinh câu lệnh Cypher lấy danh sách Node vệ tinh (:Definition, :Example, :Exercise, :Argument)
    của 1 :KnowledgeEntity, ưu tiên xếp các Node `scope = 'TEACHER'` của `teacher_id` lên đầu.
    """
    return f"""
    MATCH (ke:KnowledgeEntity {{canonical_code: $canonical_code}})-[:{rel_type.value}]->(n:{node_label.value})
    WHERE n.scope = 'GLOBAL'
       OR ($teacher_id IS NOT NULL AND n.scope = 'TEACHER' AND n.owner_id = $teacher_id)
    RETURN properties(n) AS node
    ORDER BY CASE WHEN n.scope = 'TEACHER' THEN 0 ELSE 1 END, n.created_at DESC
    """


DELETE_PEDAGOGY_NODE_BY_ID_CYPHER = """
MATCH (n {id: $node_id})
WHERE ($is_admin = true OR n.owner_id = $owner_id)
DETACH DELETE n
RETURN count(n) AS deleted_count
"""


# ============================================================================
# 4. CYPHER CHO :Process VÀ CHUỖI BƯỚC GIẢI SOCRATIC (:ProcessStep)
# ============================================================================
UPSERT_PROCESS_WITH_STEPS_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})
MERGE (p:Process {id: $process_id})
ON CREATE SET
    p.name = $name,
    p.owner_id = $owner_id,
    p.scope = $scope,
    p.source_chunk_id = $source_chunk_id,
    p.created_at = $created_at,
    p.updated_at = $updated_at
ON MATCH SET
    p.name = $name,
    p.scope = $scope,
    p.updated_at = $updated_at
MERGE (ke)-[:HAS_PROCESS]->(p)

WITH p
OPTIONAL MATCH (p)-[old_rel:HAS_STEP]->(old_step:ProcessStep)
DETACH DELETE old_step

WITH p
UNWIND $steps AS step_data
CREATE (ps:ProcessStep {
    id: step_data.id,
    process_id: $process_id,
    step_number: step_data.step_number,
    action: step_data.action,
    hint_prompt: step_data.hint_prompt,
    created_at: step_data.created_at
})
MERGE (p)-[:HAS_STEP {step_number: step_data.step_number}]->(ps)

WITH p, collect(ps) AS created_steps
FOREACH (i IN range(0, size(created_steps) - 2) |
    FOREACH (s1 IN [created_steps[i]] |
        FOREACH (s2 IN [created_steps[i + 1]] |
            MERGE (s1)-[:NEXT_STEP]->(s2)
        )
    )
)
RETURN properties(p) AS process, [s IN created_steps | properties(s)] AS steps
"""

GET_PROCESSES_FOR_ENTITY_CYPHER = """
MATCH (ke:KnowledgeEntity {canonical_code: $canonical_code})-[:HAS_PROCESS]->(p:Process)
WHERE p.scope = 'GLOBAL'
   OR ($teacher_id IS NOT NULL AND p.scope = 'TEACHER' AND p.owner_id = $teacher_id)
OPTIONAL MATCH (p)-[:HAS_STEP]->(ps:ProcessStep)
WITH p, ps
ORDER BY ps.step_number ASC
WITH p, collect(CASE WHEN ps IS NOT NULL THEN properties(ps) END) AS steps
RETURN properties(p) AS process, steps
ORDER BY CASE WHEN p.scope = 'TEACHER' THEN 0 ELSE 1 END, p.created_at DESC
"""

GET_PROCESS_BY_ID_CYPHER = """
MATCH (p:Process {id: $process_id})
OPTIONAL MATCH (p)-[:HAS_STEP]->(ps:ProcessStep)
WITH p, ps
ORDER BY ps.step_number ASC
RETURN properties(p) AS process, collect(CASE WHEN ps IS NOT NULL THEN properties(ps) END) AS steps
"""

GET_PROCESS_STEP_HINT_CYPHER = """
MATCH (p:Process {id: $process_id})-[:HAS_STEP]->(ps:ProcessStep {step_number: $step_number})
OPTIONAL MATCH (p)-[:HAS_STEP]->(all_ps:ProcessStep)
RETURN properties(ps) AS step, count(all_ps) AS total_steps
"""