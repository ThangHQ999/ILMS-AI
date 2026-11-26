from pathlib import Path
import hashlib
import json

staging = Path(__file__).resolve().parent / 'be-ingestion-create-tables'
root = Path('C:/Users/Admin/OneDrive/Desktop/dang_ky_tin_chi').resolve()
prepared = []
for item in json.loads((staging / 'manifest.json').read_text(encoding='utf-8')):
    target, source = Path(item['target']).resolve(), Path(item['stage']).resolve()
    assert target.is_relative_to(root) and source.is_relative_to(staging)
    digest = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
    if digest != item['sha256']:
        raise RuntimeError(f'Concurrent edit detected: {target}')
    prepared.append((target, source.read_bytes()))
for target, content in prepared:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
print(f'Applied {len(prepared)} reviewed BE files. No app, Flyway, tests or DB execution.')
