-- Migration: Update material_chunks table
CREATE TABLE `material_chunks` (
                                   `id` binary(16) NOT NULL COMMENT 'UUID v4 dạng Binary(16) tương ứng 36-char string bên ChromaDB/Neo4j',
                                   `material_id` binary(16) NOT NULL COMMENT 'ID tài liệu gốc từ Spring Boot',
                                   `material_version_id` binary(16) NOT NULL COMMENT 'Source/parse revision containing this chunk',
                                   `owner_id` binary(16) NOT NULL COMMENT 'ID của Admin hoặc Giáo viên sở hữu tài liệu',
                                   `scope` varchar(20) NOT NULL DEFAULT 'GLOBAL' COMMENT 'GLOBAL hoặc TEACHER',
                                   `subject` varchar(100) NOT NULL COMMENT 'Môn học (VD: MATHEMATICS, PHYSICS)',
                                   `chunk_index` int(11) NOT NULL DEFAULT 0 COMMENT 'Thứ tự của chunk trong tài liệu gốc',
                                   `content` longtext NOT NULL COMMENT 'Nội dung văn bản thô của chunk',
                                   `token_count` int(11) NOT NULL DEFAULT 0 COMMENT 'Số lượng token ước tính',
                                   `char_start` int(11) DEFAULT NULL COMMENT 'Vị trí ký tự bắt đầu trong tài liệu gốc',
                                   `char_end` int(11) DEFAULT NULL COMMENT 'Vị trí ký tự kết thúc trong tài liệu gốc',
                                   `canonical_codes` json DEFAULT NULL COMMENT 'Danh sách canonical_code dạng JSON array',
                                   `extraction_status` varchar(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING, PROCESSING, COMPLETED, FAILED',
                                   `extraction_error` text DEFAULT NULL COMMENT 'Chi tiết lỗi nếu trích xuất KG thất bại',
                                   `extra_metadata` json DEFAULT NULL COMMENT 'Metadata bổ sung (trang, chương...)',
                                   `created_at` datetime(6) DEFAULT CURRENT_TIMESTAMP(6),
                                   `updated_at` datetime(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

                                   CONSTRAINT pk_material_chunks PRIMARY KEY (`id`),
                                   UNIQUE KEY `uq_chunk_version_index` (`material_version_id`, `chunk_index`),
                                   KEY `idx_chunk_material_version` (`material_id`, `material_version_id`),
                                   KEY `idx_chunk_scope_owner_subject` (`scope`, `owner_id`, `subject`),
                                   KEY `idx_extraction_status` (`extraction_status`),
                                   CONSTRAINT `fk_chunk_material_version`
                                       FOREIGN KEY (`material_id`, `material_version_id`)
                                       REFERENCES `material_versions` (`material_id`, `id`)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
                                CONSTRAINT `fk_material_chunks_material` FOREIGN KEY (`material_id`)
                                              REFERENCES `materials` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
                                   CONSTRAINT `fk_material_chunks_owner` FOREIGN KEY (`owner_id`)
                                       REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;