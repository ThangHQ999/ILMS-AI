"""One-time source cleanup authorized by the user; no app/DB/LLM execution."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]


def path(name):
    p = (root / name).resolve()
    assert p.is_relative_to(root), name
    return p


def read(name):
    return path(name).read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def write(name, text):
    path(name).write_text(text, encoding='utf-8')


def move(source, target):
    if not path(source).exists() and path(target).exists():
        return
    assert not path(target).exists(), target
    path(source).rename(path(target))


move('app/service/tutoring/v2_service.py', 'app/service/tutoring/chat_service.py')
move('app/seed_tutoring_v2.py', 'app/seed_tutoring.py')
for name in ('intent', 'evaluation', 'question', 'response'):
    move(f'app/prompts/tutoring/v2/{name}.md', f'app/prompts/tutoring/{name}.md')
if path('app/prompts/tutoring/v2').exists():
    path('app/prompts/tutoring/v2').rmdir()  # Empty directory only, never recursive.

remove = ['app/service/socratic_chat_service.py', 'app/prompts/tutoring/base_tutor_rules.md',
          'app/prompts/tutoring/router_evaluator_system.md']
remove += [f'app/prompts/tutoring/strategies/{name}.md' for name in
           ('cognitive_metaphor', 'feynman_protege', 'misconception_autopsy', 'socratic_dialectic')]
for name in remove:
    if path(name).exists():
        try:
            path(name).unlink()
        except PermissionError:
            print('Windows denied removal of unused prompt:', name)
if path('app/prompts/tutoring/strategies').exists() and not any(path('app/prompts/tutoring/strategies').iterdir()):
    path('app/prompts/tutoring/strategies').rmdir()

for p in path('app').rglob('*.py'):
    s = p.read_text(encoding='utf-8-sig')
    s = s.replace('SOCRATIC_V2_', 'SOCRATIC_')
    s = s.replace('app.service.socratic_chat_service', 'app.service.tutoring.chat_service')
    s = s.replace('app.service.tutoring.v2_service', 'app.service.tutoring.chat_service')
    s = s.replace('SocraticChatV2Service', 'SocraticChatService')
    s = s.replace('app.seed_tutoring_v2', 'app.seed_tutoring')
    s = s.replace(" / 'v2'", '')
    s = re.sub(r'\bV2\b', 'Socratic', s)
    s = s.replace("print(\"v2\")", '')
    s = s.replace("evaluator_version='socratic-v2.1'", "evaluator_version='socratic-evaluator-1'")
    if s != p.read_text(encoding='utf-8-sig'):
        p.write_text(s, encoding='utf-8')

s = read('app/api/deps.py')
s = s.replace('from app.core.config import settings\n', '')
# Both former imports now point at the same service.
line = 'from app.service.tutoring.chat_service import SocraticChatService\n'
first = s.index(line)
s = s[:first + len(line)] + s[first + len(line):].replace(line, '')
start = s.index('def get_socratic_chat_service(')
end = s.index('\n\n# ===', start)
s = s[:start] + '''def get_socratic_chat_service(
    vector_repo: ChromaVectorRepository = Depends(get_vector_repo),
) -> SocraticChatService:
    return SocraticChatService(llm_service, vector_repo)
''' + s[end:]
write('app/api/deps.py', s)

s = read('app/controller/chat_controller.py')
start = s.index('        from app.core.config import settings\n')
end = s.index('        updated = await', start)
s = s[:start] + '''        protected = {'active_canonical_code', 'active_process_id', 'active_exercise_id',
                     'current_step_number', 'is_completed', 'teacher_id', 'subject'}
        if update_in.model_fields_set & protected:
            raise HTTPException(409, 'Trạng thái học được quản lý qua lượt chat; PATCH này chỉ đổi tiêu đề.')
''' + s[end:]
write('app/controller/chat_controller.py', s)

s = read('app/api/v1/endpoints/chat_api.py')
s = s.replace('from app.core.config import settings\n', '')
s = s.replace("    if not settings.SOCRATIC_ENABLED:\n        raise HTTPException(409, 'Socratic Socratic chưa được bật.')\n", '')
# Exact string after the V2 label replacement.
s = s.replace("    if not settings.SOCRATIC_ENABLED:\n        raise HTTPException(409, 'Socratic Socratic chưa được bật.')\n", '')
s = s.replace('    print(req)\n', '')
assert 'SOCRATIC_ENABLED' not in s, 'Unremoved service gate'
write('app/api/v1/endpoints/chat_api.py', s)

s = read('app/core/config.py')
s = s.replace('    # Socratic is opt-in until the supplied migrations and vector backfill are applied.\n',
              '    # Socratic tutoring: single service, task budgets and retrieval configuration.\n')
s = s.replace('    SOCRATIC_ENABLED: bool = False\n', '')
s = s.replace("SOCRATIC_ENTITY_COLLECTION: str = 'socratic_knowledge_entities_v2'",
              "SOCRATIC_ENTITY_COLLECTION: str = 'socratic_knowledge_entities'")
write('app/core/config.py', s)

s = read('app/repository/chroma/entity_vector_repo.py')
s = s.replace('# Initialized lazily: V1 startup does not create or mutate a Socratic collection.',
              '# Create the entity index lazily; startup does not mutate it.')
write('app/repository/chroma/entity_vector_repo.py', s)
s = read('app/service/tutoring/chat_service.py').replace('        print(req)\n', '').replace('        \n', '\n')
write('app/service/tutoring/chat_service.py', s)

# Rename only chat setting keys; preserve credentials, endpoint values and physical index names.
env = path('.env')
if env.exists():
    original = env.read_text(encoding='utf-8-sig')
    keys = set(re.findall(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=', original, re.M))
    lines = []
    for line in original.splitlines(keepends=True):
        match = re.match(r'^(\s*)(SOCRATIC_V2_[A-Z0-9_]+)(\s*=.*)$', line.rstrip('\r\n'))
        if not match:
            lines.append(line)
            continue
        key = match[2]
        if key == 'SOCRATIC_V2_ENABLED':
            continue
        new_key = key.replace('SOCRATIC_V2_', 'SOCRATIC_')
        if new_key in keys:
            continue  # Explicit neutral setting wins; never duplicate it.
        ending = '\r\n' if line.endswith('\r\n') else '\n'
        lines.append(match[1] + new_key + match[3] + ending)
    result = ''.join(lines)
    if 'SOCRATIC_ENTITY_COLLECTION' not in keys and 'SOCRATIC_V2_ENTITY_COLLECTION' not in keys:
        # Keep the previous physical collection selected even though the default is now neutral.
        result = result.rstrip('\r\n') + '\nSOCRATIC_ENTITY_COLLECTION=socratic_knowledge_entities_v2\n'
    env.write_text(result, encoding='utf-8')

move('.docs/socratic-v2.env.example', '.docs/socratic.env.example')
s = read('.docs/socratic.env.example')
s = s.replace('SOCRATIC_V2_ENABLED=true\n', '').replace('SOCRATIC_V2_', 'SOCRATIC_')
s = s.replace('V2 requests', 'chat requests').replace('socratic_chunks_v2', 'socratic_chunks')
s = s.replace('socratic_knowledge_entities_v2', 'socratic_knowledge_entities')
write('.docs/socratic.env.example', s)
move('.docs/socratic-v2-operator-guide.md', '.docs/socratic-operator-guide.md')
move('.docs/socratic-chat-v2-implementation-blueprint.md', '.docs/socratic-chat-implementation-blueprint.md')

# Update links everywhere but preserve the wording/history of dated reports.
renames = {'socratic-v2.env.example': 'socratic.env.example',
           'socratic-v2-operator-guide.md': 'socratic-operator-guide.md',
           'socratic-chat-v2-implementation-blueprint.md': 'socratic-chat-implementation-blueprint.md'}
for folder in (root, path('.docs'), path('.agents'), path('.reports')):
    for p in folder.glob('*.md'):
        s = p.read_text(encoding='utf-8-sig')
        updated = s
        for old, new in renames.items():
            updated = updated.replace(old, new)
        if updated != s:
            p.write_text(updated, encoding='utf-8')

print('Unified chat service, prompts, settings, seed command and environment keys. No secrets printed.')
