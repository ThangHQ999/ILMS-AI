import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

from lightrag import LightRAG
import lightrag.lightrag
import lightrag.kg.factory

def bypass_storage_validation(*args, **kwargs):
    pass
lightrag.lightrag.verify_storage_implementation = bypass_storage_validation

original_get_storage_class = lightrag.kg.factory.get_storage_class
def custom_get_storage_class(storage_name):
    if isinstance(storage_name, type): return storage_name
    return original_get_storage_class(storage_name)

lightrag.lightrag.get_storage_class = custom_get_storage_class
lightrag.kg.factory.get_storage_class = custom_get_storage_class

from lightrag.llm.openai import openai_embed 
from src.core.mysql_storage import MySQLKVStorage
from src.core.chroma_storage import ChromaVectorStorage

load_dotenv()

async def openai_standard_text(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """
    Hàm gọi OpenAI chuẩn hóa cho LightRAG
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    messages.append({"role": "user", "content": prompt})

    valid_openai_args = ["temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty", "response_format", "seed", "stop"]
    clean_kwargs = {k: v for k, v in kwargs.items() if k in valid_openai_args}
    
    # Gọi OpenAI bất đồng bộ
    res = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        **clean_kwargs
    )
    
    return res.choices[0].message.content

def create_rag_app():
    """Khởi tạo LightRAG chỉ quản lý Vector và KV (Bỏ qua Graph)"""
    working_dir = "./data/storage"
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=openai_standard_text,
        embedding_func=openai_embed,        
        vector_storage=ChromaVectorStorage,
        kv_storage=MySQLKVStorage,         
        addon_params={
            "max_async": 10, 
            "chunk_token_size": 8000
        } 
    )
    return rag

# import os
# from dotenv import load_dotenv

# # Import LightRAG và các module
# from lightrag import LightRAG
# import lightrag.lightrag
# import lightrag.kg.factory

# # --- BẺ KHÓA HỆ THỐNG FACTORY CỦA LIGHTRAG ---
# def bypass_storage_validation(*args, **kwargs):
#     pass
# lightrag.lightrag.verify_storage_implementation = bypass_storage_validation

# original_get_storage_class = lightrag.kg.factory.get_storage_class
# def custom_get_storage_class(storage_name):
#     if isinstance(storage_name, type): return storage_name
#     return original_get_storage_class(storage_name)

# lightrag.lightrag.get_storage_class = custom_get_storage_class
# lightrag.kg.factory.get_storage_class = custom_get_storage_class
# # ---------------------------------------------

# from lightrag.llm.gemini import gemini_embed
# from src.core.mysql_storage import MySQLKVStorage
# from src.core.chroma_storage import ChromaVectorStorage
# import os
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# load_dotenv()

# async def gemini_standard_text(prompt: str, system_prompt: str = None, **kwargs) -> str:
#     client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
#     model_name = os.getenv("LLM_MODEL")
    
#     config_args = {}
#     if system_prompt:
#         config_args["system_instruction"] = system_prompt
    
#     if kwargs:
#         config_args.update(kwargs)
        
#     config = types.GenerateContentConfig(**config_args) if config_args else None

#     res = await client.aio.models.generate_content(
#         model=model_name,
#         contents=prompt,
#         config=config
#     )
    
#     return res.text

# def create_rag_app():
#     """Khởi tạo LightRAG chỉ quản lý Vector và KV (Bỏ qua Graph)"""
#     working_dir = "./data/storage"
#     if not os.path.exists(working_dir):
#         os.makedirs(working_dir)

#     rag = LightRAG(
#         working_dir=working_dir,
#         llm_model_func=gemini_standard_text,
#         embedding_func=gemini_embed,
#         vector_storage=ChromaVectorStorage,
#         kv_storage=MySQLKVStorage,         
#         addon_params={"max_async": 1} 
#     )
#     return rag