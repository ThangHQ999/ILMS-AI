import os
import json
import asyncio
from dotenv import load_dotenv

from src.core.neo4j_storage import CustomNeo4jStorage
from src.services.gemini_structured import gemini_extract_kg
from src.core.lightrag_instance import create_rag_app
from src.core.smart_chunk_document import smart_chunk_document
from src.utils.load_file_content import load_file_content
from src.utils.cosine_similarity import cosine_similarity

load_dotenv()


async def ingest_file(file_path: str):
    """Hàm đọc file và tiến hành nạp tri thức theo luồng kép (Dual-Track)"""
    if not os.path.exists(file_path):
        print(f"[X] Lỗi: Không tìm thấy file tại đường dẫn {file_path}")
        return

    print(f"\n[*] Đang đọc và bóc tách file: {file_path}")
    try:
        document_content = load_file_content(file_path)
    except Exception as e:
        print(f"[X] Thất bại khi đọc file {file_path}: {e}")
        return

    if not document_content.strip():
        print("[!] Nội dung file rỗng.")
        return
    
    print("[*] Đang cắt chunk văn bản...")
    chunks = smart_chunk_document(file_path, document_content)
    print(f"[*] Tổng số chunk tạo ra: {len(chunks)}\n")

    # ==========================================
    # LUỒNG 1: LIGHTRAG (LƯU VÀO CHROMA VÀ MYSQL)
    # ==========================================
    print("==========================================")
    print("⏳ NẠP LUỒNG 1: Vector Storage & KV Storage")
    print("==========================================")
    
    rag = create_rag_app()
    await rag.initialize_storages()
    
    for i, chunk in enumerate(chunks):
        print(f"Đang xử lý chunk {i+1}/{len(chunks)}...")
        
        # Truyền 1 chunk dưới dạng mảng 1 phần tử
        await rag.ainsert([chunk]) 
        
        # Nghỉ 15 giây trước khi chạy chunk tiếp theo để tránh Rate Limit
        if i < len(chunks) - 1:
            print("-> Nghỉ 30s để né Rate Limit của Gemini...")
            await asyncio.sleep(30)
            
    print("✅ Luồng 1 (LightRAG) hoàn tất!\n")


    # ==========================================
    # LUỒNG 2: CUSTOM NEO4J (LƯU KNOWLEDGE GRAPH)
    # ==========================================
    print("==========================================")
    print("⏳ NẠP LUỒNG 2: Graph Storage (Giáo dục)")
    print("==========================================")
    
    storage = CustomNeo4jStorage(
        namespace="education_kg",
        global_config=rag, 
        embedding_func=rag.embedding_func
    )

    # Khởi tạo bộ nhớ lưu vector các thực thể đã quét để so sánh
    global_entity_vectors = {}

    for i, chunk in enumerate(chunks):
        print(f"[*] Đang xử lý chunk {i+1}/{len(chunks)} cho đồ thị...")
        try:
            # 1. Gọi Gemini bóc tách JSON
            json_result = await gemini_extract_kg(chunk)
            
            # 2. Giải mã JSON
            data = json.loads(json_result)
            entities = data.get("entities", [])
            relations = data.get("knowledge_relations", [])
            
            print(f"    -> AI bóc tách được: {len(entities)} Thực thể, {len(relations)} Quan hệ.")
            
            if not entities:
                continue
            
            raw_entity_names = []
            for ent in entities:
                clean_name = " ".join(ent["name"].split())
                ent["name"] = clean_name # Cập nhật luôn vào entity
                raw_entity_names.append(clean_name)
            
            # 2. SỬA LỖI: Bypass WorkerPool của LightRAG, gọi thẳng API lõi (.func)
            # Truyền lại toàn bộ danh sách 1 lần để tối ưu tốc độ
            core_embedding_api = rag.embedding_func.func
            chunk_entity_vectors = await core_embedding_api(raw_entity_names)

            # Khởi tạo dictionary để lưu ánh xạ: Tên cũ -> Tên mới (sau khi gom)
            name_mapping = {}

            for idx, entity in enumerate(entities):
                raw_name = entity["name"].strip()
                current_vector = chunk_entity_vectors[idx]
                
                matched_name = raw_name
                max_sim = 0.0
                best_match = None
                
                # Quét so sánh Cosine với các Entity đã có trong hệ thống
                for existing_name, existing_vector in global_entity_vectors.items():
                    sim = cosine_similarity(current_vector, existing_vector)
                    if sim > max_sim:
                        max_sim = sim
                        best_match = existing_name
                
                # NGƯỠNG AN TOÀN (TỰ ĐỘNG GOM): > 0.94
                # Vùng xám (0.85 - 0.94) sẽ được giữ nguyên thành node độc lập 
                # để UI sau này quét và gợi ý người dùng tự gom bằng tay.
                if max_sim > 0.97 and best_match:
                    matched_name = best_match
                    print(f"      [Deduplicated] Tự động gom '{raw_name}' -> '{matched_name}' (Cosine: {max_sim:.2f})")
                else:
                    # Nếu là khái niệm mới (hoặc nằm trong vùng xám) -> Lưu vector vào bộ nhớ chung
                    global_entity_vectors[matched_name] = current_vector
   
                # Lưu vào mapping và cập nhật lại tên cho entity
                name_mapping[raw_name] = matched_name
                entity["name"] = matched_name
                entity["embedding"] = current_vector
            
            # Cập nhật lại Source và Target cho Relationships dựa trên name_mapping
            for rel in relations:
                source_name = rel.get("source", "").strip()
                target_name = rel.get("target", "").strip()
                
                if source_name in name_mapping:
                    rel["source"] = name_mapping[source_name]
                if target_name in name_mapping:
                    rel["target"] = name_mapping[target_name]

            # 3. Đẩy dữ liệu đã chuẩn hóa lên Neo4j
            await storage.upsert_nodes(entities)
            await storage.upsert_edges(relations)
                
            # Nghỉ 20 giây giữa các chunk để tránh lỗi 429
            if i < len(chunks) - 1:
                await asyncio.sleep(20) 
            
        except json.JSONDecodeError:
            print(f"    [X] Lỗi: Gemini trả về định dạng JSON không hợp lệ ở chunk {i+1}.")
        except Exception as e:
            print(f"    [X] Có lỗi xảy ra ở chunk {i+1}: {e}")

    print("\n🎉 HOÀN TẤT TOÀN BỘ! Dữ liệu đã nằm trên Chroma, MySQL và Neo4j.")


if __name__ == "__main__":
    target_file = "./data/raw/Thuật toán Sắp xếp nổi bọt.docx"
    asyncio.run(ingest_file(target_file))