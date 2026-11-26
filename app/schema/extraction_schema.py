from typing import List, Literal, Optional
from pydantic import BaseModel, Field

RelationLabel = Literal[
    "IS_A", "HAS_CATEGORY", "HAS_SUBTYPE", "CLASSIFIED_INTO", "IS_VARIANT_OF",
    "PART_OF", "COMPOSED_OF", "CONTAINS",
    "REQUIRES", "DEPENDS_ON", "APPLIES_TO",
    "ASSOCIATED_WITH", "USES", "CONTRASTS_WITH", "IMPROVES_UPON",
    "CAUSES", "LEADS_TO", "SOLVES", "PRODUCES", "YIELDS",
    "CREATED_BY", "DISCOVERED_BY"
]

# 1. NODE CỘNG ĐỒNG (TOPIC)
class TopicSchema(BaseModel):
    name: str = Field(description="Tên Chủ đề/Chương lớn bao trùm văn bản (VD: Di truyền học phân tử, Cấu trúc dữ liệu). Viết hoa chữ cái đầu.")
    summary: str = Field(description="Bản tóm tắt TỔNG HỢP. Bắt buộc viết thành một đoạn văn dài, mượt mà, tóm lược toàn bộ các khái niệm cốt lõi. Giọng văn mang tính hệ thống hóa để học sinh ôn tập.")
    concepts_included: List[str] = Field(description="Danh sách TÊN của các Entity (Khái niệm cốt lõi) được trích xuất bên dưới thuộc về Chủ đề này.")

# 2. Định nghĩa, ví dụ, bài tập của thực thể tri thức
class DefinitionSchema(BaseModel):
    content: str = Field(description="Nội dung định nghĩa chi tiết. Bắt buộc tổng hợp tất cả các câu mô tả, so sánh thành một đoạn văn duy nhất, hợp lý ngữ nghĩa.")
    conditions: List[str] = Field(default=[], description="Các điều kiện để định nghĩa này đúng (rỗng nếu không có).")
    exceptions: List[str] = Field(default=[], description="Các trường hợp ngoại lệ (rỗng nếu không có).")

class ExerciseSchema(BaseModel):
    title: str = Field(description="Tiêu đề câu hỏi/bài tập")
    content: str = Field(description="Nội dung đề bài chi tiết")
    difficulty: Literal["EASY", "MEDIUM", "HARD"] = Field(description="Chỉ được phép chọn 1 trong 3 mức độ: EASY, MEDIUM, hoặc HARD.")
    solution_steps: List[str] = Field(
        default=[], 
        description="Các bước hướng dẫn giải hoặc phương pháp tính toán chi tiết (nếu tài liệu đề cập)."
    )
    
class ExampleSchema(BaseModel):
    title: str = Field(description="Tiêu đề ví dụ/minh họa")
    code_snippet: str = Field(default="", description="Code mẫu (không có thì trả về chuỗi rỗng '')")
    explanation: str = Field(description="Lời giải thích ví dụ")

# 3. Xử lý Quy trình / Các bước
class ProcessStepSchema(BaseModel):
    step_number: int = Field(description="Thứ tự của bước (1, 2, 3...)")
    action: str = Field(description="Bước mấy: Hành động hoặc sự kiện diễn ra trong bước này")

class ProcessSchema(BaseModel):
    name: str = Field(description="Tên tổng thể của quy trình (VD: Quá trình Nhân đôi DNA).")
    description: str = Field(description="Mô tả tổng quan về mục đích của quy trình.")
    steps: List[ProcessStepSchema] = Field(
        description="BẮT BUỘC PHẢI CÓ TỪ 1 BƯỚC TRỞ LÊN. Bẻ nhỏ cơ chế hoạt động thành các bước tuần tự."
    )

# 4. Thực thể chính (Entity)
class EntitySchema(BaseModel):
    name: str = Field(description="Tên khái niệm chuẩn hóa. CẤM tạo tên thực thể chứa các từ 'Quy trình', 'Cách giải', 'Bài tập'. BẮT BUỘC giữ nguyên các chữ viết tắt khoa học viết hoa (như DNA, RNA, ATP, OOP), không được chuyển thành chữ thường.")
    type: str = Field(description="Loại khái niệm (Algorithm, Concept, Formula, Tool, Person, Event). TUYỆT ĐỐI CẤM dùng chữ 'Process', 'Exercise' hoặc 'Example' ở đây.")
    description: str = Field(description="Mô tả ngắn gọn")
    embedding: Optional[List[float]] = Field(default=None, description="Vector nhúng (bỏ qua bước này, Python sẽ tự thêm)")
    
    definition: Optional[DefinitionSchema] = Field(
        default=None,
        description="Định nghĩa duy nhất của khái niệm. Gộp chung mọi mô tả thành một khối."
    )
    
    processes: List[ProcessSchema] = Field(
        default=[], 
        description="Các quy trình, vòng đời liên quan. Mọi Quy Trình BẮT BUỘC phải nằm ở đây, KHÔNG ĐƯỢC tạo Entity độc lập cho Quy trình."
    )
    
    exercises: List[ExerciseSchema] = Field(
        default=[], 
        description="Danh sách bài tập. BẮT BUỘC nhét bài tập vào Entity Khái niệm/Thuật toán được áp dụng. TUYỆT ĐỐI KHÔNG tạo Entity mới chỉ để chứa bài tập."
    )
    
    examples: List[ExampleSchema] = Field(
        default=[], 
        description="Danh sách ví dụ minh họa. TUYỆT ĐỐI KHÔNG tạo Entity mới cho bối cảnh ví dụ. Bằng chứng khoa học thì đưa vào mảng arguments, không đưa vào đây."
    )

# 5. Mối quan hệ (Relationships)
class KnowledgeRelationSchema(BaseModel):
    source: str = Field(description="TÊN ENTITY NGUỒN. BẮT BUỘC phải khớp chính xác 100% với một 'name' đã có trong mảng entities. CẤM tự bịa ra Entity mới. CẤM lấy tên Quy trình làm nguồn.")
    target: str = Field(description="TÊN ENTITY ĐÍCH. BẮT BUỘC phải khớp chính xác 100% với một 'name' đã có trong mảng entities. CẤM tự bịa ra tên mới (VD: Mạch bổ sung).")
    label: RelationLabel = Field(
        description="Chọn 1 nhãn. CẤM LẠM DỤNG 'IS_A' cho quy trình hoặc tác dụng. Chỉ dùng IS_A để phân loại cha-con."
    )
    description: str = Field(description="Giải thích ngắn gọn tại sao 2 khái niệm này liên kết với nhau.")

# 6. Luận điểm và Bằng chứng
class ArgumentSchema(BaseModel):
    hypothesis: str = Field(description="Giả thuyết, nhận định hoặc luận điểm chính (VD: Môi trường làm thay đổi biểu hiện gen).")
    evidence: List[str] = Field(default=[], description="Các bằng chứng, số liệu hỗ trợ (VD: Nghiên cứu trên sinh đôi cùng trứng...). CẤM vứt bằng chứng này vào phần Examples.")
    conclusion: str = Field(description="Kết luận được rút ra từ luận điểm trên.")

# 7. Siêu dữ liệu
class MetadataSchema(BaseModel):
    domain: str = Field(description="Lĩnh vực chuyên môn (VD: Khoa học máy tính, Sinh học)")
    main_topic: str = Field(description="Chủ đề cốt lõi của văn bản")

# 8. SCHEMA GỐC BAO TRÙM (ROOT)
class KnowledgeGraphExtraction(BaseModel):
    thought_process: str = Field(
        alias="_thought_process", 
        description="SUY LUẬN TRƯỚC KHI TẠO: 1. Đâu là khái niệm lõi? 2. Đâu là bằng chứng (phải nhét vào arguments)? 3. Đâu là quy trình (phải nhét vào processes)? 4. Đâu là bài tập (nhét vào exercises)?"
    )
    metadata: MetadataSchema
    
    topic: TopicSchema = Field(
        description="BẮT BUỘC PHẢI TẠO. Không được để trống. Tổng hợp chủ đề vĩ mô của toàn bộ đoạn văn bản."
    )
    
    entities: List[EntitySchema] = Field(description="Danh sách các thực thể tri thức lõi.")
    knowledge_relations: List[KnowledgeRelationSchema] = Field(default=[], description="Mối quan hệ đồ thị giữa các thực thể.")
    arguments: List[ArgumentSchema] = Field(
        default=[], 
        description="Cực kỳ quan trọng: BẮT BUỘC đưa các cặp [Giả thuyết -> Bằng chứng -> Kết luận] khoa học vào đây."
    )

# 9. Schema dùng cho Agent 4 (Reviewer - Không đổi)
class MergeActionSchema(BaseModel):
    source_name: str = Field(description="Tên thực thể bị trùng, kém chuẩn (VD: ADN)")
    target_name: str = Field(description="Tên thực thể chuẩn mực (VD: Phân tử DNA)")
    reason: str = Field(description="Lý do gộp")

class ResolutionResultSchema(BaseModel):
    merges: List[MergeActionSchema] = Field(default=[])
    deletes: List[str] = Field(default=[])
    
 