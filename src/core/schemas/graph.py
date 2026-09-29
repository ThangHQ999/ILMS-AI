from typing import List
from pydantic import BaseModel, Field

class DefinitionSchema(BaseModel):
    content: str = Field(description="Nội dung định nghĩa chi tiết của khái niệm")
    conditions: List[str] = Field(description="Các điều kiện để định nghĩa/khái niệm này đúng (nếu có, rỗng nếu không)")
    exceptions: List[str] = Field(description="Các trường hợp ngoại lệ, bối cảnh không áp dụng (nếu có, rỗng nếu không)")

class ExerciseSchema(BaseModel):
    title: str = Field(description="Tiêu đề câu hỏi/bài tập")
    content: str = Field(description="Nội dung đề bài chi tiết")
    difficulty: str = Field(description="EASY, MEDIUM, hoặc HARD")

class ExampleSchema(BaseModel):
    title: str = Field(description="Tiêu đề ví dụ/minh họa")
    code_snippet: str = Field(description="Code mẫu (nếu có, không có thì trả về chuỗi rỗng '')")
    explanation: str = Field(description="Lời giải thích ví dụ")

# 2. Schema mới: Xử lý Quy trình / Các bước (Processes & Workflows)
class ProcessStepSchema(BaseModel):
    step_number: int = Field(description="Thứ tự của bước (1, 2, 3...)")
    action: str = Field(description="Hành động hoặc sự kiện diễn ra trong bước này")

class ProcessSchema(BaseModel):
    name: str = Field(description="Tên quy trình hoặc vòng đời (VD: Quy trình quang hợp, Vòng đời phát triển phần mềm)")
    description: str = Field(description="Mô tả tổng quan về mục đích của quy trình này")
    steps: List[ProcessStepSchema] = Field(description="Danh sách các bước thực hiện theo trình tự")

class EntitySchema(BaseModel):
    name: str = Field(description="Tên khái niệm chuẩn hóa (viết hoa chữ cái đầu)")
    type: str = Field(description="Loại khái niệm (Algorithm, Concept, Formula, Tool, Person, Process, Event)")
    description: str = Field(description="Mô tả ngắn gọn")
    definitions: List[DefinitionSchema] = Field(description="Danh sách định nghĩa (có thể rỗng nếu không có dữ liệu)")
    
    # Nhúng danh sách quy trình vào bên trong thực thể
    processes: List[ProcessSchema] = Field(description="Các quy trình, vòng đời liên quan đến thực thể này (có thể rỗng)")
    
    exercises: List[ExerciseSchema] = Field(description="Danh sách bài tập (có thể rỗng nếu không có dữ liệu)")
    examples: List[ExampleSchema] = Field(description="Danh sách ví dụ (có thể rỗng nếu không có dữ liệu)")

# 3. Mở rộng hướng dẫn cho Mối quan hệ (Relationships)
class KnowledgeRelationSchema(BaseModel):
    source: str = Field(description="Tên thực thể nguồn")
    target: str = Field(description="Tên thực thể đích")
    label: str = Field(description="Nhãn quan hệ (VD: IS_A (phân cấp), CAUSES (nhân quả), PART_OF (thành phần), APPLIES_TO)")
    description: str = Field(description="Ngữ cảnh chi tiết giải thích tại sao 2 khái niệm này liên kết với nhau")

# 4. Schema mới: Luận điểm và Bằng chứng (Arguments & Evidence)
class ArgumentSchema(BaseModel):
    hypothesis: str = Field(description="Giả thuyết, nhận định hoặc luận điểm chính")
    evidence: List[str] = Field(description="Danh sách các bằng chứng, số liệu hỗ trợ cho luận điểm")
    conclusion: str = Field(description="Kết luận được rút ra")

# 5. Schema mới: Siêu dữ liệu (Metadata)
class MetadataSchema(BaseModel):
    domain: str = Field(description="Lĩnh vực chuyên môn của đoạn tài liệu (VD: Khoa học máy tính, Sinh học, Kinh tế)")
    main_topic: str = Field(description="Chủ đề cốt lõi mà đoạn văn bản này đang đề cập")

# 6. Schema gốc bao trùm tất cả
class KnowledgeGraphExtraction(BaseModel):
    metadata: MetadataSchema = Field(description="Siêu dữ liệu tổng quan của đoạn tài liệu đang xét")
    entities: List[EntitySchema] = Field(description="Danh sách các thực thể tri thức được trích xuất")
    knowledge_relations: List[KnowledgeRelationSchema] = Field(description="Danh sách các mối quan hệ đồ thị giữa các thực thể")
    arguments: List[ArgumentSchema] = Field(description="Các luận điểm và bằng chứng học thuật (nếu có trong tài liệu)")