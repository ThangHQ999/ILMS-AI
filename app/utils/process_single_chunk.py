import asyncio
import json

from src.services.openai_extract_kg import openai_extract_kg
from src.utils.cosine_similarity import cosine_similarity

semaphore = asyncio.Semaphore(4) 

async def process_single_chunk(i, chunk, core_embedding_api, global_entity_vectors, global_entities_dict, lock, file_name):
    """
    Xử lý độc lập từng chunk
    - global_entity_vectors: dict lưu { "name": vector } để tìm độ tương đồng
    - global_entities_dict: dict lưu { ("name", "type"): entity_object } để gộp dữ liệu
    """
    try:
        async with semaphore:
            json_result = await openai_extract_kg(chunk, file_name)
            
        data = json.loads(json_result)
        entities = data.get("entities", [])
        relations = data.get("knowledge_relations", [])
        
        if not entities:
            return [], []
            
        raw_entity_names = [" ".join(ent["name"].split()) for ent in entities]
        for idx, ent in enumerate(entities):
            ent["name"] = raw_entity_names[idx]

        chunk_entity_vectors = await core_embedding_api(raw_entity_names)

        name_mapping = {}
        unique_chunk_entities = []
        
        async with lock:
            for idx, entity in enumerate(entities):
                raw_name = entity["name"].strip()
                entity_type = entity.get("type", "Unknown").strip()
                current_vector = chunk_entity_vectors[idx]
                
                matched_name = raw_name
                max_sim = 0.0
                best_match = None
                
                for existing_name, existing_vector in global_entity_vectors.items():
                    sim = cosine_similarity(current_vector, existing_vector)
                    if sim > max_sim:
                        max_sim = sim
                        best_match = existing_name
                
                if max_sim > 0.96 and best_match:
                    matched_name = best_match
                    print(f"    [Deduplicated] Tự động gom '{raw_name}' -> '{matched_name}' (Cosine: {max_sim:.2f})")
                else:
                    global_entity_vectors[matched_name] = current_vector
                
                name_mapping[raw_name] = matched_name
                entity["name"] = matched_name
                entity["embedding"] = current_vector

                entity_key = (matched_name, entity_type)
                
                if entity_key in global_entities_dict:
                    existing_entity = global_entities_dict[entity_key]
                    
                    existing_def = existing_entity.get("definition")
                    new_def = entity.get("definition")
                    
                    if new_def:
                        if existing_def:
                            if new_def.get('content') and new_def.get('content') not in existing_def.get('content', ''):
                                existing_def["content"] = f"{existing_def.get('content', '')}\n{new_def.get('content')}".strip()
                            
                            existing_conds = set(existing_def.get("conditions", []))
                            existing_conds.update(new_def.get("conditions", []))
                            existing_def["conditions"] = list(existing_conds)
                            
                            existing_excs = set(existing_def.get("exceptions", []))
                            existing_excs.update(new_def.get("exceptions", []))
                            existing_def["exceptions"] = list(existing_excs)
                        else:
                            existing_entity["definition"] = new_def
                            
                    for field in ["exercises", "examples", "processes"]:
                        if entity.get(field):
                            if field not in existing_entity:
                                existing_entity[field] = []
                            existing_entity[field].extend(entity[field])
                else:
                    global_entities_dict[entity_key] = entity
                    unique_chunk_entities.append(entity)

        for rel in relations:
            source_name = rel.get("source", "").strip()
            target_name = rel.get("target", "").strip()
            if source_name in name_mapping:
                rel["source"] = name_mapping[source_name]
            if target_name in name_mapping:
                rel["target"] = name_mapping[target_name]
                
        return unique_chunk_entities, relations
        
    except Exception as e:
        print(f"    [X] Lỗi ở chunk {i+1}: {e}")
        return [], []