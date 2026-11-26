from pathlib import Path
import hashlib
import json

root = Path('D:/ILMS-FE')
staging = Path(__file__).resolve().parent / 'fe-stream-motion'
relative = Path('src/features/ai-tutor/components/AiTutorMessageItem.tsx')
source = root / relative
original = source.read_bytes()
text = original.decode('utf-8-sig').replace('\r\n', '\n')
text = text.replace("import { SocraticContextAccordion } from './SocraticContextAccordion';",
    "import { SocraticContextAccordion } from './SocraticContextAccordion';\nimport styles from './AiTutorMessageItem.module.css';")
old = '''          <div role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
            <span aria-hidden="true" className="size-2 rounded-full bg-primary motion-safe:animate-pulse" />
            {message.streamStatus && t.has(`streamStages.${message.streamStatus.stage}`)
              ? t(`streamStages.${message.streamStatus.stage}`) : t('streamWorking')}
          </div>'''
new = '''          <div role="status" aria-atomic="true" className="flex items-center gap-2.5 text-sm text-muted-foreground">
            <span aria-hidden="true" className={styles.dots}>
              <span className={styles.dot} />
              <span className={styles.dot} />
              <span className={styles.dot} />
            </span>
            <span className={styles.label}>
              {message.streamStatus && t.has(`streamStages.${message.streamStatus.stage}`)
                ? t(`streamStages.${message.streamStatus.stage}`) : t('streamWorking')}
            </span>
          </div>'''
assert text.count(old) == 1
text = text.replace(old, new)
css = '''.dots {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  flex-shrink: 0;
}

.dot {
  width: 0.3rem;
  height: 0.3rem;
  border-radius: 50%;
  background: currentColor;
  animation: dot-breathe 1.5s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.16s; }
.dot:nth-child(3) { animation-delay: 0.32s; }

.label {
  color: transparent;
  background-image: linear-gradient(110deg,
    var(--muted-foreground) 35%, var(--foreground) 50%, var(--muted-foreground) 65%);
  background-size: 240% 100%;
  background-clip: text;
  -webkit-background-clip: text;
  animation: text-shimmer 2.6s linear infinite;
}

@keyframes dot-breathe {
  0%, 70%, 100% { opacity: 0.4; transform: scale(0.8); }
  35% { opacity: 1; transform: scale(1); }
}

@keyframes text-shimmer {
  from { background-position: 150% 0; }
  to { background-position: -150% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .dot, .label { animation: none; }
  .label { color: var(--muted-foreground); background-image: none; }
}

@media (forced-colors: active) {
  .label { color: CanvasText; background-image: none; }
}
'''
files = [(relative, text), (relative.with_suffix('.module.css'), css)]
manifest = []
for rel, content in files:
    target = root / rel
    dest = staging / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding='utf-8')
    manifest.append({'target': str(target), 'stage': str(dest),
        'sha256': hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None})
(staging / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Prepared 2 UI files; external FE unchanged.')
