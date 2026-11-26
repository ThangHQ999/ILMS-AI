"""Stage only; write outside the AI workspace requires a separate approval."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent / 'step-display'
FE = Path('D:/ILMS-FE')
BE = Path('C:/Users/Admin/OneDrive/Desktop/dang_ky_tin_chi')
manifest = []


def replace(s, old, new):
    assert old in s, old[:100]
    return s.replace(old, new)


def stage(root, relative, transform):
    target = root / relative
    original = target.read_bytes() if target.exists() else None
    text = original.decode('utf-8-sig').replace('\r\n', '\n') if original else ''
    result = transform(text)
    dest = ROOT / ('fe' if root == FE else 'be') / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result, encoding='utf-8')
    manifest.append({'target': str(target), 'stage': str(dest),
        'sha256': hashlib.sha256(original).hexdigest() if original is not None else None})


def schema(s):
    s = replace(s, "import { z } from 'zod';", '''import { z } from 'zod';

/** An explicit backend-confirmed step; a numeric counter alone is not progress. */
export const stepProgressSchema = z.object({
  step_id: z.string().min(1),
  exercise_id: z.string().min(1),
  number: z.number().int().positive(),
  total: z.number().int().positive(),
  instruction: z.string().default(''),
  completed: z.boolean(),
}).refine((step) => step.number <= step.total);
''')
    for name in ('socraticChatMessageItemSchema', 'sseSessionInitDataSchema', 'sseStepUpdateDataSchema', 'sseDoneDataSchema'):
        s = replace(s, f'export const {name} = z.object({{',
            f'export const {name} = z.object({{\n  step_progress: stepProgressSchema.nullable().optional(),')
    return replace(s, '  step_number_at_turn: z.number(),', '  step_number_at_turn: z.number().nullable().optional(),')


stage(FE, 'src/features/ai-tutor/schemas/socratic-chat.schema.ts', schema)


def types(s):
    s = replace(s, '  sseStatusDataSchema,', '  sseStatusDataSchema,\n  stepProgressSchema,')
    s = replace(s, 'export type SSEStatusData =', '''export type SocraticStepProgress = z.infer<typeof stepProgressSchema>;
export type SSEStatusData =''')
    s = replace(s, 'export interface SocraticProgressState {', '''export interface SocraticProgressState {
  stepId: string;
  exerciseId: string;''')
    s = replace(s, '  step_number_at_turn?: number | null;',
        '  step_number_at_turn?: number | null;\n  step_progress?: SocraticStepProgress | null;')
    return s


stage(FE, 'src/features/ai-tutor/types.ts', types)


def hook(s):
    s = replace(s, '  SocraticProgressState,', '  SocraticProgressState,\n  SocraticStepProgress,')
    s = replace(s, 'interface UseSocraticStreamOptions {', '''function toProgressState(step?: SocraticStepProgress | null): SocraticProgressState | null {
  if (!step) return null;
  return {
    stepId: step.step_id,
    exerciseId: step.exercise_id,
    currentStepNumber: step.number,
    totalSteps: step.total,
    currentStepAction: step.instruction,
    isCompleted: step.completed,
  };
}

interface UseSocraticStreamOptions {''')
    for name in ('onSessionInit', 'onStepUpdate'):
        begin = s.index(f'            {name}:')
        start = s.index('              setProgressState(', begin)
        end = s.index('              }));', start) + len('              }));')
        s = s[:start] + '              setProgressState(toProgressState(data.step_progress));' + s[end:]
    # session_init describes the previous state, not the message being generated.
    s = replace(s, '                      step_number_at_turn: data.current_step_number,',
        '                      step_number_at_turn: null,\n                      step_progress: null,')
    s = replace(s, '            onDone: (data) => {\n              if (controller.signal.aborted) return;',
        '''            onDone: (data) => {
              if (controller.signal.aborted) return;
              setProgressState(toProgressState(data.step_progress));''')
    s = replace(s, '                      step_number_at_turn: data.step_number_at_turn,',
        '                      step_number_at_turn: data.step_number_at_turn,\n                      step_progress: data.step_progress ?? null,')
    return s


stage(FE, 'src/features/ai-tutor/hooks/useSocraticStream.ts', hook)
stage(FE, 'src/features/ai-tutor/components/AiTutorMessageItem.tsx', lambda s:
    replace(replace(s, '{message.step_number_at_turn && (', '{message.step_progress && ('),
        "t('stepBadge', { step: message.step_number_at_turn })", "t('stepBadge', { step: message.step_progress.number })"))
stage(FE, 'src/features/ai-tutor/components/AiTutorPageView.tsx', lambda s:
    replace(s, '        step_number_at_turn: m.step_number_at_turn,',
        '        step_number_at_turn: m.step_number_at_turn,\n        step_progress: m.step_progress,'))


def stepper(s):
    s = replace(s, '  const total = progress.totalSteps || 3;\n  const current = progress.currentStepNumber;',
        '''  const current = progress.currentStepNumber;
  const total = progress.totalSteps;
  if (!progress.stepId || !progress.exerciseId || !total || current < 1 || current > total) return null;''')
    s = replace(s, 'className="grid grid-cols-3 gap-1.5 my-2.5"', 'className="flex gap-1.5 my-2.5"')
    s = replace(s, 'className={`h-1.5 rounded-full', 'className={`h-1.5 flex-1 rounded-full')
    return s


stage(FE, 'src/features/ai-tutor/components/SocraticStepperCard.tsx', stepper)


def backend(s):
    s = replace(s, '        private Integer step_number_at_turn;',
        '        private Integer step_number_at_turn;\n        private StepProgressDto step_progress;')
    pos = s.rfind('\n}')
    s = s[:pos] + '''

    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class StepProgressDto {
        private String step_id;
        private String exercise_id;
        private Integer number;
        private Integer total;
        private String instruction;
        private Boolean completed;
    }
''' + s[pos:]
    return s


stage(BE, 'src/main/java/com/example/ilms/dto/socratic/SocraticSessionDetailDto.java', backend)
report = '''# Backend-confirmed exercise step display

Date: 2026-11-02
STATUS: PARTIAL (runtime not verified)
SUMMARY: Only explicit step_progress metadata can enable message badges and the progress card. Concept discussion, review and exercises without real ordered steps do not display numbered steps. Removed the frontend fallback of three steps. The session_init counter is no longer stamped onto the assistant message before that turn completes.
CONTRACT: Python emits step_progress (nullable) with step_id, exercise_id, number, total, instruction and completed. Metadata is stored in existing turn_metadata.public; no DB migration. step_number_at_turn is null when no confirmed exercise step exists. Spring preserves metadata on historical messages, SSE remains pass-through. Frontend validates and uses metadata for live completion and loaded history; missing metadata hides labels, including old ambiguous history.
CHECKS: static syntax/review only; no app, tests, Java compile, typecheck or build run per the user's standing instruction.
LIMITATIONS: No backfill of ambiguous old steps. Exercises without explicit stored steps intentionally have no numbered progress. No unrelated authentication, database, streaming animation or dependencies changed.
DOCS: TASKS and docs/api-spec updated.
DEPLOYMENT: not deployed.
NEXT: restart services and check concept chat has no badge/card, real exercise uses the exact backend total, switching back to concepts clears progress, and reload retains only confirmed historical steps.

## Review
No inferred progress from current_step_number=1, Process presence or a guessed three-step total. Historical labels use per-message metadata, not the session's current exercise state. No applied migrations changed.
'''
for root in (FE, BE):
    stage(root, 'reports/2026-11-02-confirmed-step-display.md', lambda s:
        report if not s else (_ for _ in ()).throw(ValueError('Report already exists')))
    stage(root, 'TASKS.md', lambda s: replace(s, '## Done',
        '## Done\n- [x] 2026-11-02 — Backend-confirmed exercise step display; no inferred concept-chat steps (runtime not verified): `reports/2026-11-02-confirmed-step-display.md`'))
    stage(root, 'docs/api-spec.md', lambda s: s + '''

## Confirmed exercise step metadata (2026-11-02)

session_init/step_update/done and history messages can contain nullable step_progress: {step_id, exercise_id, number, total, instruction, completed}. Only this explicit metadata permits numbered step UI. Internal current_step_number is not display evidence. step_number_at_turn can be null. Missing metadata hides badges and the stepper, including old history; no frontend fallback total. Spring forwards metadata in historical DTOs and SSE pass-through.
''')

ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f'Prepared {len(manifest)} external files; external projects unchanged.')
