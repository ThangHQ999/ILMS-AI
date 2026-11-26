"""Structured ingestion reviewer agent."""
from app.agents.ingestion_prompt import run_ingestion_agent


async def run_reviewer(llm, instruction, payload, schema, *, config=None):
    return await run_ingestion_agent('reviewer', llm, instruction, payload, schema, config)
