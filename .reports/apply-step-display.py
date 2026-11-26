from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent / 'step-display'
allowed = [Path('D:/ILMS-FE').resolve(), Path('C:/Users/Admin/OneDrive/Desktop/dang_ky_tin_chi').resolve()]
prepared = []
for item in json.loads((root / 'manifest.json').read_text(encoding='utf-8')):
    target, source = Path(item['target']).resolve(), Path(item['stage']).resolve()
    assert source.is_relative_to(root) and any(target.is_relative_to(p) for p in allowed)
    actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
    if actual != item['sha256']:
        raise RuntimeError(f'Concurrent edit detected: {target}')
    prepared.append((target, source.read_bytes()))
for target, content in prepared:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
print(f'Applied {len(prepared)} reviewed external files; no app/test/database execution.')
