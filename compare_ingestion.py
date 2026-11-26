"""Compare the existing agents, native LightRAG and the combined pipeline."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from app.schema.ingestion_contracts import SourceSnapshot
from app.service.ingestion.benchmark_usage import collect_usage
from app.service.ingestion.config import IngestionSettings
from app.service.ingestion.document_parser import local_file_path, parse_document, read_source
from app.service.ingestion.lightrag_eval import candidate_hints, extract_native
from app.service.ingestion.multi_agent import run_pipeline
from app.service.ingestion.preprocessing import (
    TokenCounter, build_chunks, semantic_boundaries, semantic_units, verify_chunks,
)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def graph_counts(graph, evidence):
    processes = [process for entity in graph['entities'] for process in entity['processes']]
    exercises = [exercise for entity in graph['entities'] for exercise in entity['exercises']]
    return {
        'entities': len(graph['entities']),
        'processes': len(processes),
        'process_steps': sum(len(process['steps']) for process in processes),
        'exercises': len(exercises),
        'solution_steps': sum(len(exercise['solution_steps']) for exercise in exercises),
        'issues': len(graph.get('issues', [])),
        'rejected_claims': evidence.get('rejected_claim_count', 0),
        'rejected_evidence': len(evidence.get('evidence_rejections', [])),
        'review_notes': len(graph.get('review_notes', [])),
        'requires_evidence_review': graph.get('requires_evidence_review'),
    }


async def compare(path, output, mode):
    config = IngestionSettings()
    start = perf_counter()
    content = read_source(path, config)
    digest = hashlib.sha256(content).hexdigest()
    snapshot = SourceSnapshot(
        material_id=uuid4(), material_version_id=uuid4(), source_name=path.name,
        source_hash=digest, size_bytes=len(content), extension=path.suffix.lower(),
    )
    document = parse_document(snapshot, config, content=content)
    counter = TokenCounter(config.tokenizer_encoding)
    preprocess_usage = {}
    if config.chunk_strategy == 'semantic':
        units = list(semantic_units(document, config, counter))
        with collect_usage() as preprocess_usage:
            scores = await semantic_boundaries(units, quiet=True)
        manifest = build_chunks(document, config, counter, units=units, similarities=scores)
    else:
        manifest = build_chunks(document, config, counter)
    integrity = verify_chunks(document, manifest, counter)
    if not integrity.passed:
        raise ValueError('Shared chunk integrity failed')
    preprocess_seconds = round(perf_counter() - start, 2)
    write_json(output / 'chunks.json', manifest.model_dump(mode='json'))
    results = {}
    measured_usage = {'preprocess': preprocess_usage}

    async def measure(name, operation):
        with collect_usage() as rows:
            measured_usage[name] = rows
            return await operation

    async def agents(name, hints=None):
        artifacts = {}

        def keep_result(filename, value):
            if filename in {'08-draft.json', '09-graph-draft.json'}:
                artifacts[filename] = value

        start = perf_counter()
        try:
            await measure(name, run_pipeline(document, manifest, 'review', lambda *_: None, keep_result,
                               repair_quotes=False, parallel_chunks=config.api_parallel_chunks,
                               quiet=True, graph_hints=hints))
            graph = artifacts['09-graph-draft.json']
            evidence = artifacts['08-draft.json']
            write_json(output / f'{name}-graph.json', graph)
            write_json(output / f'{name}-evidence.json', evidence)
            results[name] = {'status': 'DRAFT_READY', 'seconds': round(perf_counter() - start, 2),
                             **graph_counts(graph, evidence)}
        except Exception as exc:
            results[name] = {'status': 'FAILED', 'seconds': round(perf_counter() - start, 2),
                             'error_type': type(exc).__name__}

    if mode in {'all', 'agents'}:
        await agents('agents')
    if mode in {'all', 'lightrag', 'hybrid'}:
        start = perf_counter()
        try:
            graph = await measure('lightrag', extract_native(manifest, output / 'lightrag-storage'))
            write_json(output / 'lightrag-graph.json', graph)
            results['lightrag'] = {
                'status': 'GRAPH_READY', 'seconds': round(perf_counter() - start, 2),
                'nodes': len(graph['nodes']), 'edges': len(graph['edges']),
                'truncated': graph.get('is_truncated', False), **graph['usage'],
            }
        except Exception as exc:
            results['lightrag'] = {'status': 'FAILED', 'seconds': round(perf_counter() - start, 2),
                                   'error_type': type(exc).__name__, 'error': str(exc)[:500]
                                   if isinstance(exc, RuntimeError) and str(exc).startswith(
                                       ('Install requirements-', 'Expected lightrag-hku', 'LightRAG document status',
                                        'The LightRAG experiment requires')
                                   ) else 'LightRAG extraction failed'}
        if mode in {'all', 'hybrid'}:
            if results['lightrag']['status'] != 'GRAPH_READY':
                results['hybrid'] = {'status': 'SKIPPED', 'error': 'LightRAG graph unavailable'}
            else:
                hints = candidate_hints(graph, counter)
                if not hints:
                    results['hybrid'] = {'status': 'SKIPPED', 'error': 'No source-mapped graph hints'}
                else:
                    await agents('hybrid', hints)
                    hybrid = results['hybrid']
                    hybrid['hints'] = len(hints)
                    hybrid['standalone_seconds'] = round(hybrid['seconds'] + results['lightrag']['seconds'], 2)
    from app.core.config import settings

    summary = {
        'source_name': path.name, 'source_hash': digest, 'chunk_count': len(manifest.chunks),
        'chunk_strategy': config.chunk_strategy, 'preprocess_seconds': preprocess_seconds,
        'agent_provider': settings.LLM_DEFAULT_PROVIDER, 'agent_fallback_enabled': settings.LLM_ENABLE_FALLBACK,
        'embedding_provider': settings.EMBEDDING_PROVIDER, 'openai_extraction_model': settings.OPENAI_EXTRACTION_MODEL,
        'gemini_extraction_model': settings.GEMINI_EXTRACTION_MODEL, 'results': results,
        'openai_usage_by_stage': measured_usage,
    }
    write_json(output / 'comparison.json', summary)
    lines = [
        '# So sánh ingestion', '', f'File: {path.name}', '',
        f'Dùng chung {len(manifest.chunks)} chunk. Tiền xử lý {preprocess_seconds:.2f} giây.', '',
        '| Nhánh | Trạng thái | Giây | Thực thể / node | Bước quy trình | Bài tập | Bước giải | Issues |',
        '|---|---|---:|---:|---:|---:|---:|---:|',
    ]
    for name, row in results.items():
        lines.append(
            f"| {name} | {row['status']} | {row.get('standalone_seconds', row.get('seconds', '–'))} "
            f"| {row.get('entities', row.get('nodes', '–'))} | {row.get('process_steps', '–')} "
            f"| {row.get('exercises', '–')} | {row.get('solution_steps', '–')} | {row.get('issues', '–')} |"
        )
    lines.extend(['', 'Thời gian hybrid gồm thời gian LightRAG và thời gian bốn agent.',
                  'Đếm mục chỉ giúp rà soát. Chấm đúng sai bằng cách đối chiếu tài liệu nguồn.',
                  'Xem comparison.json để biết lỗi từng nhánh và số lượt gọi của LightRAG.'])
    (output / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return any(row['status'] in {'FAILED', 'SKIPPED'} for row in results.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='Local document path')
    parser.add_argument('--mode', choices=('all', 'agents', 'lightrag', 'hybrid'), default='all')
    parser.add_argument('--output', type=Path, default=Path('data/ingestion-comparison'))
    args = parser.parse_args()
    output = args.output.resolve() / uuid4().hex
    output.mkdir(parents=True, exist_ok=False)
    try:
        failed = asyncio.run(compare(local_file_path(args.file), output, args.mode))
    except Exception as exc:
        # Keep the common preprocessing failure separate from pipeline results.
        write_json(output / 'comparison.json', {'status': 'FAILED', 'error_type': type(exc).__name__,
                                                'error_code': getattr(exc, 'code', 'PREPROCESSING_FAILED')})
        print(f'Comparison could not start. Details: {output / "comparison.json"}')
        return 1
    print(f'Report: {output / "REPORT.md"}')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
