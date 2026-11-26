"""Structured ingestion expert agent."""
from app.agents.ingestion_prompt import run_ingestion_agent


async def run_expert(llm, instruction, payload, schema, *, config=None):
    return await run_ingestion_agent('expert', llm, instruction, payload, schema, config)
