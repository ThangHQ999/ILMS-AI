"""Apply prepared changes after filesystem approval; reject concurrent edits."""
import hashlib
import json
from pathlib import Path

staging = Path(__file__).resolve().parent / 'sse-integration'
manifest = json.loads((staging / 'manifest.json').read_text(encoding='utf-8'))
roots = (Path('D:/ILMS-FE').resolve(), Path('C:/Users/Admin/OneDrive/Desktop/dang_ky_tin_chi').resolve())
prepared = []
for item in manifest:
    target = Path(item['source']).resolve()
    source = Path(item['stage']).resolve()
    if not any(target.is_relative_to(root) for root in roots) or not source.is_relative_to(staging):
        raise RuntimeError('Path outside reviewed roots')
    current = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
    if current != item['original_sha256']:
        raise RuntimeError(f'Concurrent edit detected: {target}')
    prepared.append((target, source.read_bytes()))
for target, content in prepared:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
print(f'Applied {len(prepared)} reviewed files. No applications, tests or databases started.')
