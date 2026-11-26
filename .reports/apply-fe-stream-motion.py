from pathlib import Path
import hashlib
import json

root = Path('D:/ILMS-FE').resolve()
staging = Path(__file__).resolve().parent / 'fe-stream-motion'
manifest = json.loads((staging / 'manifest.json').read_text(encoding='utf-8'))
prepared = []
for item in manifest:
    target, source = Path(item['target']).resolve(), Path(item['stage']).resolve()
    assert target.is_relative_to(root) and source.is_relative_to(staging)
    actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
    if actual != item['sha256']:
        raise RuntimeError(f'Concurrent edit detected: {target}')
    prepared.append((target, source.read_bytes()))
for target, data in prepared:
    target.write_bytes(data)
print('Applied 2 reviewed UI files. No app or tests started.')
