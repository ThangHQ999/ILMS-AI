import os

def delete_specific_files(root_dir="./data"):
    # Danh sách các tên file cần xóa
    target_files = {
        "graph_chunk_entity_relation.graphml",
        "kv_store_doc_status.json"
    }
    
    if not os.path.exists(root_dir):
        print(f"[!] Thư mục '{root_dir}' không tồn tại.")
        return

    deleted_count = 0
    print(f"[*] Đang quét thư mục '{root_dir}' để xóa các file liên quan đến LightRAG...")

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename in target_files:
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    print(f"  [-] Đã xóa: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  [X] Không thể xóa {file_path}: {e}")

    print(f"\n✅ Hoàn tất! Đã xóa tổng cộng {deleted_count} file.")

if __name__ == "__main__":
    delete_specific_files()