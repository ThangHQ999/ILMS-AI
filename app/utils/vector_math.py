import os
import numpy as np
from openai import OpenAI
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AUTO_MERGE_THRESHOLD = 0.95 
SUSPECT_THRESHOLD = 0.80    


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Hàm tính khoảng cách Cosine giữa 2 vector"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def generate_embeddings(graph_data):
    """
    BƯỚC 4.1: Gọi API nhúng Vector cho tất cả Thực thể
    Mẹo tối ưu: Chúng ta gửi theo Batch (1 mảng các text) chứ không gọi API từng lần một.
    """
    entities = graph_data.entities
    if not entities:
        return graph_data

    texts_to_embed = [f"Tên: {ent.name}. Mô tả: {ent.description}" for ent in entities]
    
    response = client.embeddings.create(
        input=texts_to_embed,
        model="text-embedding-3-small"
    )
    
    for i, data in enumerate(response.data):
        entities[i].embedding = data.embedding
        
    graph_data.entities = entities
    return graph_data


def find_suspected_pairs(entities) -> Tuple[List[Dict], str]:
    """
    BƯỚC 4.2: Toán học chéo (Tất cả vs Tất cả) để tìm cặp nghi ngờ.
    Trả về: 
      - auto_merges: Danh sách tự gộp bằng code
      - suspected_pairs_text: Chuỗi text định dạng sẵn để ném cho Agent 4
    """
    auto_merges = []
    suspected_pairs_text = ""
    suspected_count = 1
    
    processed_names = set()
    n = len(entities)
    
    for i in range(n):
        ent_a = entities[i]
        if ent_a.name in processed_names: 
            continue
            
        for j in range(i + 1, n):
            ent_b = entities[j]
            if ent_b.name in processed_names: 
                continue
                
            if not ent_a.embedding or not ent_b.embedding:
                continue
                
            sim = cosine_similarity(ent_a.embedding, ent_b.embedding)
            
            if sim >= AUTO_MERGE_THRESHOLD:
                if len(ent_a.name) >= len(ent_b.name):
                    target, source = ent_a.name, ent_b.name
                else:
                    target, source = ent_b.name, ent_a.name
                    
                auto_merges.append({
                    "source_name": source,
                    "target_name": target,
                    "reason": f"Tự động gộp bởi Python (Độ giống: {sim:.2f})"
                })
                processed_names.update([source, target])
                
            elif SUSPECT_THRESHOLD <= sim < AUTO_MERGE_THRESHOLD:
                suspected_pairs_text += f"[Cặp {suspected_count} - Độ giống {sim:.2f}]:\n"
                suspected_pairs_text += f"- Entity A: \"{ent_a.name}\" (Mô tả: {ent_a.description})\n"
                suspected_pairs_text += f"- Entity B: \"{ent_b.name}\" (Mô tả: {ent_b.description})\n\n"
                
                suspected_count += 1
                processed_names.update([ent_a.name, ent_b.name])

    return auto_merges, suspected_pairs_text.strip()


def apply_resolutions(graph_data, auto_merges: List[Dict], agent_4_decisions):
    """
    BƯỚC 4.4: Đao phủ thực thi.
    Đọc lệnh gộp từ Python (auto) và Agent 4 để "Cắt - Ghép - Xóa" mảng dữ liệu.
    """
    if isinstance(agent_4_decisions, dict):
        agent_merges = agent_4_decisions.get("merges", [])
    else:
        agent_merges = agent_4_decisions.merges

    processed_agent_merges = [
        m if isinstance(m, dict) else m.model_dump() 
        for m in agent_merges
    ]

    all_merges = auto_merges + processed_agent_merges    
    if isinstance(agent_4_decisions, dict):
        agent_deletes = agent_4_decisions.get("deletes", [])
    else:
        agent_deletes = agent_4_decisions.deletes

    deletes_to_process = set(agent_deletes)
    source_names = {m["source_name"] for m in all_merges}
    entities_to_remove = deletes_to_process.union(source_names)
    
    entity_dict = {e.name: e for e in graph_data.entities}
    
    for merge_action in all_merges:
        src_name = merge_action["source_name"]
        tgt_name = merge_action["target_name"]
        
        if src_name in entity_dict and tgt_name in entity_dict:
            src_ent = entity_dict[src_name]
            tgt_ent = entity_dict[tgt_name]
            
            if hasattr(src_ent, 'exercises') and src_ent.exercises:
                if tgt_ent.exercises is None: tgt_ent.exercises = []
                tgt_ent.exercises.extend(src_ent.exercises)
                
            if hasattr(src_ent, 'processes') and src_ent.processes:
                if tgt_ent.processes is None: tgt_ent.processes = []
                tgt_ent.processes.extend(src_ent.processes)
                
            for rel in graph_data.knowledge_relations:
                if rel.source == src_name:
                    rel.source = tgt_name
                if rel.target == src_name:
                    rel.target = tgt_name

    final_entities = [e for e in graph_data.entities if e.name not in entities_to_remove]
    graph_data.entities = final_entities
    
    seen_rels = set()
    final_rels = []
    for rel in graph_data.knowledge_relations:
        rel_tuple = (rel.source, rel.target, rel.label)
        if rel_tuple not in seen_rels:
            seen_rels.add(rel_tuple)
            final_rels.append(rel)
            
    graph_data.knowledge_relations = final_rels
    
    return graph_data