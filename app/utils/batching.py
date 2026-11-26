from typing import List, Dict, Tuple, Any

from src.schemas.schemas import (
    KnowledgeGraphExtraction, 
    TopicSchema, 
    KnowledgeRelationSchema, 
    EntitySchema
)

def merge_graphs_python(partial_graphs: List[Any]) -> KnowledgeGraphExtraction:
    """
    Gộp danh sách các Đồ thị nhỏ (Partial Graphs) thành một Đồ thị Tổng (Global Graph).
    """
    print(f"🔄 [Batching] Đang gộp {len(partial_graphs)} đồ thị cục bộ thành đồ thị tổng...")

    merged_entities: Dict[str, EntitySchema] = {}
    merged_relations: Dict[Tuple[str, str, str], KnowledgeRelationSchema] = {}
    all_arguments = []
    
    topic_names = []
    topic_summaries = []
    all_concepts_included = set()
    base_metadata = None

    for graph in partial_graphs:
        # Chuyển đổi linh hoạt nếu graph là dict hay pydantic model
        is_dict = isinstance(graph, dict)
        
        # Lấy metadata từ chunk đầu tiên tìm thấy
        if not base_metadata:
            base_metadata = graph.get("metadata") if is_dict else getattr(graph, "metadata", None)

        # 0. LẤY ARGUMENTS (Luận điểm học thuật)
        args = graph.get("arguments", []) if is_dict else getattr(graph, "arguments", [])
        if args:
            for arg in args:
                # Chuẩn hóa an toàn cho arg (dict hoặc object)
                hyp = arg.get("hypothesis") if isinstance(arg, dict) else getattr(arg, "hypothesis", str(arg))
                if hyp and not any((a.hypothesis if not isinstance(a, dict) else a.get("hypothesis")) == hyp for a in all_arguments):
                    all_arguments.append(arg)

        # 1. GỘP ENTITIES
        entities = graph.get("entities", []) if is_dict else getattr(graph, "entities", [])
        if entities:
            for ent in entities:
                # Xử lý an toàn tên và thuộc tính dù là dict hay object
                ent_name = (ent.get("name") if isinstance(ent, dict) else getattr(ent, "name", "")).strip()
                if not ent_name:
                    continue
                lookup_key = ent_name.lower()
                
                if lookup_key in merged_entities:
                    existing_ent = merged_entities[lookup_key]
                    
                    # Gộp exercises
                    ent_exs = ent.get("exercises", []) if isinstance(ent, dict) else getattr(ent, "exercises", [])
                    if ent_exs:
                        if isinstance(existing_ent, dict):
                            if "exercises" not in existing_ent or existing_ent["exercises"] is None: existing_ent["exercises"] = []
                            existing_ent["exercises"].extend(ent_exs)
                        else:
                            if existing_ent.exercises is None: existing_ent.exercises = []
                            existing_ent.exercises.extend(ent_exs)
                            
                    # Gộp processes
                    ent_procs = ent.get("processes", []) if isinstance(ent, dict) else getattr(ent, "processes", [])
                    if ent_procs:
                        if isinstance(existing_ent, dict):
                            if "processes" not in existing_ent or existing_ent["processes"] is None: existing_ent["processes"] = []
                            existing_ent["processes"].extend(ent_procs)
                        else:
                            if existing_ent.processes is None: existing_ent.processes = []
                            existing_ent.processes.extend(ent_procs)
                            
                    # Gộp examples
                    ent_amps = ent.get("examples", []) if isinstance(ent, dict) else getattr(ent, "examples", [])
                    if ent_amps:
                        if isinstance(existing_ent, dict):
                            if "examples" not in existing_ent or existing_ent["examples"] is None: existing_ent["examples"] = []
                            existing_ent["examples"].extend(ent_amps)
                        else:
                            if existing_ent.examples is None: existing_ent.examples = []
                            existing_ent.examples.extend(ent_amps)
                else:
                    # Nếu là dict, ép về EntitySchema hoặc giữ nguyên
                    if is_dict and not isinstance(ent, EntitySchema):
                        try:
                            ent_obj = EntitySchema(**ent)
                            ent_obj.name = ent_name
                            merged_entities[lookup_key] = ent_obj
                        except:
                            merged_entities[lookup_key] = ent
                    else:
                        ent.name = ent_name
                        merged_entities[lookup_key] = ent

        # 2. GỘP MỐI QUAN HỆ (KNOWLEDGE RELATIONS) - ⚠️ ĐẢM BẢO KHÔNG BỊ MẤT
        relations = graph.get("knowledge_relations", []) if is_dict else getattr(graph, "knowledge_relations", [])
        if relations:
            for rel in relations:
                src = (rel.get("source") if isinstance(rel, dict) else getattr(rel, "source", "")).strip()
                tgt = (rel.get("target") if isinstance(rel, dict) else getattr(rel, "target", "")).strip()
                lbl = (rel.get("label") if isinstance(rel, dict) else getattr(rel, "label", "")).strip()
                
                if not src or not tgt:
                    continue
                
                rel_key = (src.lower(), tgt.lower(), lbl)
                
                if rel_key not in merged_relations:
                    merged_relations[rel_key] = rel
                else:
                    existing_rel = merged_relations[rel_key]
                    desc = (rel.get("description") if isinstance(rel, dict) else getattr(rel, "description", ""))
                    ex_desc = (existing_rel.get("description") if isinstance(existing_rel, dict) else getattr(existing_rel, "description", ""))
                    
                    if desc and desc not in ex_desc:
                        new_desc = f"{ex_desc} | {desc}" if ex_desc else desc
                        if isinstance(existing_rel, dict):
                            existing_rel["description"] = new_desc
                        else:
                            existing_rel.description = new_desc

        # 3. GỘP TOPIC
        top = graph.get("topic") if is_dict else getattr(graph, "topic", None)
        if top:
            t_name = top.get("name") if isinstance(top, dict) else getattr(top, "name", "")
            t_sum = top.get("summary") if isinstance(top, dict) else getattr(top, "summary", "")
            t_concepts = top.get("concepts_included", []) if isinstance(top, dict) else getattr(top, "concepts_included", [])
            
            if t_name and t_name not in topic_names:
                topic_names.append(t_name)
            if t_sum:
                topic_summaries.append(t_sum)
            if t_concepts:
                for c in t_concepts:
                    all_concepts_included.add(c.strip())

    # ==========================================
    # ĐÓNG GÓI THÀNH ĐỒ THỊ TỔNG (GLOBAL GRAPH)
    # ==========================================
    global_topic = None
    if topic_summaries:
        final_topic_name = " - ".join(topic_names) if len(topic_names) <= 3 else "Kiến thức Tổng hợp"
        global_topic = TopicSchema(
            name=final_topic_name,
            summary="\n\n".join(topic_summaries),
            concepts_included=list(all_concepts_included)
        )

    # Đảm bảo chuyển đổi knowledge_relations sang đúng schema nếu chúng đang ở dạng dict
    final_relations = []
    for rel in merged_relations.values():
        if isinstance(rel, dict):
            try:
                final_relations.append(KnowledgeRelationSchema(**rel))
            except:
                pass
        else:
            final_relations.append(rel)

    global_graph = KnowledgeGraphExtraction(
        _thought_process="Global Graph Merged Robustly by Python Batching",
        metadata=base_metadata or {},
        topic=global_topic,
        entities=list(merged_entities.values()),
        knowledge_relations=final_relations,
        arguments=all_arguments
    )

    print(f"✅ [Batching] Kết quả chuẩn: {len(global_graph.entities)} Entities, {len(global_graph.knowledge_relations)} Relations, {len(global_graph.arguments)} Arguments.")
    return global_graph