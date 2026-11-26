"""Structured ingestion extractor agent."""
from app.agents.ingestion_prompt import run_ingestion_agent


async def run_extractor(llm, instruction, payload, schema, *, config=None):
    return await run_ingestion_agent('extractor', llm, instruction, payload, schema, config)
