"""Collect provider-reported OpenAI usage in the active benchmark task."""
from collections import Counter
from contextlib import contextmanager
from contextvars import ContextVar

_active = ContextVar('ingestion_benchmark_usage', default=None)


@contextmanager
def collect_usage():
    rows = {}
    token = _active.set(rows)
    try:
        yield rows
    finally:
        _active.reset(token)


def record_openai_usage(model, usage, *, embedding=False):
    rows = _active.get()
    if rows is None:
        return
    row = rows.setdefault(('embedding:' if embedding else 'llm:') + model, Counter())
    row['responses'] += 1
    if usage is None:
        row['missing_usage'] += 1
        return
    row['input_tokens'] += usage.prompt_tokens
    if not embedding:
        row['output_tokens'] += usage.completion_tokens
        row['cached_input_tokens'] += getattr(
            getattr(usage, 'prompt_tokens_details', None), 'cached_tokens', 0,
        ) or 0
