"""Structured ingestion validator agent."""
from app.agents.ingestion_prompt import run_ingestion_agent


async def run_validator(llm, instruction, payload, schema, *, config=None):
    return await run_ingestion_agent('validator', llm, instruction, payload, schema, config)
