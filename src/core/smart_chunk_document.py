import os
import re
from typing import List
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    PythonCodeTextSplitter,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.utils.text_cleaner import sanitize_text

MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n---+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

_semantic_embeddings = None

def get_semantic_embeddings():
    global _semantic_embeddings
    if _semantic_embeddings is None:
        _semantic_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
    return _semantic_embeddings

def _chunk_hierarchical(
    content: str,
    parent_chunk_size: int = 1200,
    parent_overlap: int = 200,
    child_chunk_size: int = 800,
    child_overlap: int = 150,
) -> List[str]:
    """
    Kỹ thuật Phân tầng:
    1. Chia văn bản thành các Parent chunks lớn (chứa đầy đủ ngữ cảnh).
    2. Trong từng Parent chunk, cắt thành các Child chunks nhỏ.
    3. Đính kèm bản tóm tắt hoặc header định danh ngữ cảnh cha vào từng Child chunk.
    """
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_overlap,
        separators=MARKDOWN_SEPARATORS,
        is_separator_regex=True
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_overlap,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        is_separator_regex=False
    )

    parent_docs = parent_splitter.split_text(content)
    enriched_chunks = []

    for p_idx, parent_text in enumerate(parent_docs):
        first_line = parent_text.strip().split("\n")[0][:100]
        context_anchor = f"[Context: Section {p_idx + 1} - '{first_line}...']"

        children = child_splitter.split_text(parent_text)
        for child in children:
            chunk_with_parent_context = f"{context_anchor}\n{child}"
            enriched_chunks.append(chunk_with_parent_context)

    return enriched_chunks

def _chunk_markdown(content: str, max_chunk_size: int = 5000, overlap: int = 300) -> List[str]:
    headers_to_split_on = [("#", "H1"), ("##", "H2"), ("###", "H3"), ("####", "H4")]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=True)
    section_docs = md_splitter.split_text(content)

    final_chunks = []
    
    for doc in section_docs:
        header_path = " > ".join([str(v) for k, v in doc.metadata.items() if k in ["H1", "H2", "H3", "H4"]])
        prefix = f"[{header_path}]\n" if header_path else ""
        
        effective_chunk_size = max(200, max_chunk_size - len(prefix))
        
        text_content = doc.page_content.strip()
        if not text_content:
            continue
            
        if len(text_content) <= effective_chunk_size:
            final_chunks.append(f"{prefix}{text_content}")
        else:
            sub_splitter = RecursiveCharacterTextSplitter(
                chunk_size=effective_chunk_size,
                chunk_overlap=overlap,
                separators=["\n\n", "\n", ". ", " "]
            )
            for sub in sub_splitter.split_text(text_content):
                final_chunks.append(f"{prefix}{sub.strip()}")

    return final_chunks


def _chunk_semantic(content: str, percentile_threshold: int = 90) -> List[str]:
    embeddings = get_semantic_embeddings()
    semantic_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=percentile_threshold
    )
    docs = semantic_splitter.create_documents([content])
    return [doc.page_content for doc in docs]

def smart_chunk_document(
    file_path: str,
    content: str,
    strategy: str = "auto",  # 'auto', 'hierarchical', 'semantic', 'structure'
    chunk_size: int = 5000,  
    chunk_overlap: int = 300,
    min_chunk_length: int = 100
) -> List[str]:
    """
    Router phân luồng chiến lược:
    - Code: AST / Code Splitter
    - Markdown: Structure-Aware (Two-stage)
    - CSV/TSV: Row-by-Row
    - Sách/Luật/Báo cáo dài: Hierarchical (Parent-Child)
    - Văn bản tự do/Transcript: Semantic
    """
    clean_text = sanitize_text(content)
    if not clean_text:
        return []

    ext = os.path.splitext(file_path)[-1].lower()

    if strategy == "hierarchical":
        raw_chunks = _chunk_hierarchical(clean_text)
    elif strategy == "semantic":
        raw_chunks = _chunk_semantic(clean_text)
    elif strategy == "structure":
        raw_chunks = _chunk_markdown(clean_text, max_chunk_size=chunk_size, overlap=chunk_overlap)
    else:
        if ext in [".py", ".js", ".ts", ".go", ".java", ".sql", ]:
            splitter = PythonCodeTextSplitter(chunk_size=max(chunk_size, 800), chunk_overlap=chunk_overlap)
            raw_chunks = splitter.split_text(clean_text)

        elif ext in [".md", ".markdown"] or re.search(r"^#{1,3}\s+\S+", clean_text, re.MULTILINE):
            raw_chunks = _chunk_markdown(clean_text, max_chunk_size=chunk_size, overlap=chunk_overlap)

        elif ext in [".csv", ".tsv"]:
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0, separators=["\n"])
            raw_chunks = splitter.split_text(clean_text)

        elif ext in [".pdf", ".docx", ".doc"] or len(clean_text) > 10000:
            raw_chunks = _chunk_hierarchical(clean_text)
            
        elif ext in [".txt", ".transcript"]:
            raw_chunks = _chunk_semantic(clean_text)

        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=MARKDOWN_SEPARATORS
            )
            raw_chunks = splitter.split_text(clean_text)

    return [c.strip() for c in raw_chunks if len(c.strip()) >= min_chunk_length]