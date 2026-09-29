import os
from dotenv import load_dotenv

# Import LightRAG và các module
from lightrag import LightRAG
import lightrag.lightrag
import lightrag.kg.factory

# --- BẺ KHÓA HỆ THỐNG FACTORY CỦA LIGHTRAG ---
def bypass_storage_validation(*args, **kwargs):
    pass
lightrag.lightrag.verify_storage_implementation = bypass_storage_validation

original_get_storage_class = lightrag.kg.factory.get_storage_class
def custom_get_storage_class(storage_name):
    if isinstance(storage_name, type): return storage_name
    return original_get_storage_class(storage_name)

lightrag.lightrag.get_storage_class = custom_get_storage_class
lightrag.kg.factory.get_storage_class = custom_get_storage_class
# ---------------------------------------------

from lightrag.llm.gemini import gemini_embed
from src.core.mysql_storage import MySQLKVStorage
from src.core.chroma_storage import ChromaVectorStorage
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

async def gemini_standard_text(prompt: str, system_prompt: str = None, **kwargs) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    config_args = {}
    if system_prompt:
        config_args["system_instruction"] = system_prompt
    
    if kwargs:
        config_args.update(kwargs)
        
    config = types.GenerateContentConfig(**config_args) if config_args else None

    res = await client.aio.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config
    )
    
    return res.text

def create_rag_app():
    """Khởi tạo LightRAG chỉ quản lý Vector và KV (Bỏ qua Graph)"""
    working_dir = "./data/storage"
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=gemini_standard_text,
        embedding_func=gemini_embed,
        vector_storage=ChromaVectorStorage,
        kv_storage=MySQLKVStorage,         
        addon_params={"max_async": 1} 
    )
    return rag