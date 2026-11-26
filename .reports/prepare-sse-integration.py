"""Prepare reviewable copies only; external repositories are not written here."""
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent / 'sse-integration'
FE = Path('D:/ILMS-FE')
BE = Path('C:/Users/Admin/OneDrive/Desktop/dang_ky_tin_chi')
manifest = []


def stage(root, relative, transform):
    source = root / relative
    original = source.read_bytes() if source.exists() else None
    current = original.decode('utf-8-sig') if original is not None else ''
    current = current.replace('\r\n', '\n')
    result = transform(current)
    dest = BASE / ('fe' if root == FE else 'be') / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result, encoding='utf-8')
    manifest.append({'source': str(source), 'stage': str(dest),
                     'original_sha256': hashlib.sha256(original).hexdigest() if original is not None else None})


def replace(s, old, new):
    assert old in s, old[:100]
    return s.replace(old, new)


def dto(s):
    s = s.replace('import jakarta.validation.constraints.NotBlank;',
        'import jakarta.validation.constraints.NotBlank;\nimport jakarta.validation.constraints.Min;\nimport jakarta.validation.constraints.Max;\nimport jakarta.validation.constraints.PositiveOrZero;')
    return replace(s, '    private String activeExercise_id;','''    private String activeExercise_id;
    private String forced_action;
    private UUID client_request_id;
    @PositiveOrZero
    private Long expected_state_version;
    @Builder.Default
    @Min(1)
    @Max(2)
    private Integer protocol_version = 1;''')


stage(BE, 'src/main/java/com/example/ilms/dto/socratic/SocraticChatStreamRequestDto.java', dto)
stage(BE, 'src/main/java/com/example/ilms/exception/ErrorCode.java', lambda s: replace(s,
    '    // Auth', '''    SOCRATIC_STREAM_FAILED(HttpStatus.BAD_GATEWAY, "Kết nối gia sư AI bị gián đoạn. Vui lòng thử lại."),
    // Auth'''))


def bridge(s):
    s = s.replace('import reactor.core.Disposable;', 'import reactor.core.Disposable;\nimport reactor.core.Disposables;\nimport com.fasterxml.jackson.databind.ObjectMapper;\nimport com.example.ilms.exception.ErrorCode;')
    s = replace(s, '    private final FastApiProperties properties;',
        '    private final FastApiProperties properties;\n    private final ObjectMapper objectMapper;')
    start = s.index('        Disposable subscription = socraticChatClient')
    end = s.index('\n    }', start)
    s = s[:start] + '''        // Register cancellation before subscribe; callbacks can run synchronously.
        Disposable.Swap upstream = Disposables.swap();
        emitter.onCompletion(upstream::dispose);
        emitter.onTimeout(() -> {
            upstream.dispose();
            emitter.complete();
        });
        emitter.onError(error -> upstream.dispose());
        upstream.update(socraticChatClient
                .streamSocraticChat(request, provider, "STUDENT")
                .subscribe(event -> {
                    try {
                        SseEmitter.SseEventBuilder outgoing = SseEmitter.event();
                        if (StringUtils.hasText(event.event())) outgoing.name(event.event());
                        if (event.id() != null) outgoing.id(event.id());
                        if (event.retry() != null) outgoing.reconnectTime(event.retry().toMillis());
                        if (event.comment() != null) outgoing.comment(event.comment());
                        if (event.data() != null) outgoing.data(event.data());
                        if (event.data() != null || event.comment() != null) emitter.send(outgoing);
                    } catch (Exception sendError) {
                        upstream.dispose();
                        emitter.completeWithError(sendError);
                    }
                }, error -> {
                    log.warn("Socratic upstream stream failed: {}", error.getClass().getSimpleName());
                    try {
                        emitter.send(SseEmitter.event().name("error").data(objectMapper.writeValueAsString(Map.of(
                                "code", "SPRING_PROXY_ERROR",
                                "message", ErrorCode.SOCRATIC_STREAM_FAILED.getMessage(),
                                "recoverable", true,
                                "content_status", "INCOMPLETE"))));
                        emitter.complete();
                    } catch (Exception sendError) {
                        emitter.completeWithError(sendError);
                    }
                }, emitter::complete));''' + s[end:]
    # No raw exception interpolation is needed after JSON serialization above.
    start = s.index('    private String escapeJson(')
    s = s[:start] + '}\n'
    return s.replace('import java.io.IOException;\n', '')


stage(BE, 'src/main/java/com/example/ilms/service/SocraticTutorBridgeService.java', bridge)


def schemas(s):
    s = replace(s, 'export const socraticStreamPayloadSchema = z.object({', '''export const socraticStreamPayloadSchema = z.object({
  protocol_version: z.union([z.literal(1), z.literal(2)]).optional(),
  client_request_id: z.string().uuid().optional(),
  expected_state_version: z.number().int().nonnegative().optional(),''')
    s = replace(s, 'export const sseDoneDataSchema = z.object({', '''export const sseStatusDataSchema = z.object({
  stage: z.string(),
  state: z.enum(['running', 'completed', 'failed']),
  message: z.string(),
});

export const sseContentReplaceDataSchema = z.object({
  full_content: z.string(),
});

export const sseDoneDataSchema = z.object({
  state_version: z.number().int().nonnegative().optional(),''')
    return replace(s, 'export const sseErrorDataSchema = z.object({', '''export const sseErrorDataSchema = z.object({
  partial_response: z.boolean().optional(),
  content_status: z.string().nullable().optional(),
  assistant_message_id: z.string().nullable().optional(),''')


stage(FE, 'src/features/ai-tutor/schemas/socratic-chat.schema.ts', schemas)


def types(s):
    s = replace(s, '  sseErrorDataSchema,', '  sseErrorDataSchema,\n  sseStatusDataSchema,\n  sseContentReplaceDataSchema,')
    s = replace(s, 'export type SSEErrorData =', '''export type SSEStatusData = z.infer<typeof sseStatusDataSchema>;
export type SSEContentReplaceData = z.infer<typeof sseContentReplaceDataSchema>;
export type SSEErrorData =''')
    return replace(s, '  isStreaming?: boolean;', '''  isStreaming?: boolean;
  streamStatus?: SSEStatusData | null;
  isIncomplete?: boolean;''')


stage(FE, 'src/features/ai-tutor/types.ts', types)


def service(s):
    s = replace(s, '  SSEErrorData,', '  SSEErrorData,\n  SSEStatusData,\n  SSEContentReplaceData,')
    s = replace(s, '  sseErrorDataSchema,', '  sseErrorDataSchema,\n  sseStatusDataSchema,\n  sseContentReplaceDataSchema,')
    s = replace(s, '  onToken: (delta: string) => void;', '''  onStatus?: (data: SSEStatusData) => void;
  onContentReplace?: (data: SSEContentReplaceData) => void;
  onToken: (delta: string) => void;''')
    s = replace(s, '    throw new Error(errorMsg);', '    return;')
    start = s.index('  const decoder = new TextDecoder')
    end = s.index('\n}\n', start)
    s = s[:start] + '''  const decoder = new TextDecoder('utf-8');
  let buffer = '';
  let terminal = false;

  const fail = (code: string): void => {
    if (terminal) return;
    terminal = true;
    callbacks.onError?.({ code, message: '', recoverable: true, content_status: 'INCOMPLETE' });
  };

  const processBlock = (block: string): void => {
    if (terminal) return;
    let eventType = 'message';
    const dataLines: string[] = [];
    for (const line of block.split('\\n')) {
      if (line.startsWith('event:')) eventType = line.slice(6).trim();
      else if (line.startsWith('data:')) dataLines.push(line.slice(5).replace(/^ /, ''));
    }
    if (!dataLines.length) return; // Heartbeat comments have no data.
    let parsed: unknown;
    try {
      parsed = JSON.parse(dataLines.join('\\n'));
    } catch {
      fail('INVALID_SSE_EVENT');
      return;
    }
    try {
      switch (eventType) {
        case 'session_init': callbacks.onSessionInit?.(sseSessionInitDataSchema.parse(parsed)); break;
        case 'step_update': callbacks.onStepUpdate?.(sseStepUpdateDataSchema.parse(parsed)); break;
        case 'context_ref': callbacks.onContextRef?.(sseContextRefDataSchema.parse(parsed)); break;
        case 'status': callbacks.onStatus?.(sseStatusDataSchema.parse(parsed)); break;
        case 'content_replace': callbacks.onContentReplace?.(sseContentReplaceDataSchema.parse(parsed)); break;
        case 'token': callbacks.onToken(sseTokenDataSchema.parse(parsed).delta); break;
        case 'done': {
          const data = sseDoneDataSchema.parse(parsed);
          terminal = true;
          callbacks.onDone?.(data);
          break;
        }
        case 'error': {
          const data = sseErrorDataSchema.parse(parsed);
          terminal = true;
          callbacks.onError?.(data);
          break;
        }
        default: break; // Unknown event types must never become chat text.
      }
    } catch {
      fail('INVALID_SSE_EVENT');
    }
  };

  const consume = (): void => {
    buffer = buffer.replace(/\\r\\n/g, '\\n');
    let boundary = buffer.indexOf('\\n\\n');
    while (boundary >= 0 && !terminal) {
      const block = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      processBlock(block);
      boundary = buffer.indexOf('\\n\\n');
    }
  };

  try {
    while (!terminal) {
      const { done, value } = await reader.read();
      if (done) {
        buffer += decoder.decode();
        consume();
        if (buffer.trim()) processBlock(buffer);
        if (!terminal) fail('STREAM_INTERRUPTED');
        break;
      }
      buffer += decoder.decode(value, { stream: true });
      consume();
    }
  } catch (error: unknown) {
    if (options?.signal?.aborted) throw error;
    fail('STREAM_INTERRUPTED');
  } finally {
    try { await reader.cancel(); } catch { /* The connection may already be closed. */ }
    reader.releaseLock();
  }''' + s[end:]
    return s


stage(FE, 'src/features/ai-tutor/services/socratic-chat.service.ts', service)


def hook(s):
    s = replace(s, '      if (!isCurrentActive) {', '''      if (!isCurrentActive) {
        abortControllerRef.current?.abort();
        abortControllerRef.current = null;
        setIsStreaming(false);''')
    s = replace(s, '      setIsStreaming(false);\n    }\n  }, []);', '''      setIsStreaming(false);
      setMessages((prev) => prev.map((m) => m.isStreaming
        ? { ...m, isStreaming: false, streamStatus: null, isIncomplete: true } : m));
    }
  }, []);''')
    s = replace(s, '      const now = new Date();', '      let assistantId = aiTempId;\n      const now = new Date();')
    s = replace(s, '            session_id: activeSessionId || null,', '''            protocol_version: 2,
            client_request_id: crypto.randomUUID(),
            session_id: activeSessionId || null,''')
    s = replace(s, '            onSessionInit: (data) => {', '''            onSessionInit: (data) => {
              assistantId = data.assistant_message_id;''')
    s = replace(s, '            onToken: (delta) => {', '''            onStatus: (data) => {
              setMessages((prev) => prev.map((m) => m.id === assistantId && m.isStreaming
                ? { ...m, streamStatus: data.state === 'running' ? data : null } : m));
            },
            onContentReplace: (data) => {
              setMessages((prev) => prev.map((m) => m.id === assistantId
                ? { ...m, content: data.full_content } : m));
            },
            onToken: (delta) => {''')
    s = s.replace('if (m.isStreaming) {', 'if (m.id === assistantId && m.isStreaming) {')
    s = replace(s, 'return { ...m, content: m.content + delta };',
        'return { ...m, content: m.content + delta, streamStatus: null };')
    s = replace(s, 'if (m.isStreaming || m.id === data.assistant_message_id)',
        'if (m.id === assistantId || m.id === data.assistant_message_id)')
    s = replace(s, 'content: data.full_content || m.content,', 'content: data.full_content,')
    s = replace(s, '                      isStreaming: false,', '''                      isStreaming: false,
                      streamStatus: null,
                      isIncomplete: false,''')
    s = s.replace('m.isStreaming ? { ...m, isStreaming: false } : m',
        'm.id === assistantId ? { ...m, isStreaming: false, streamStatus: null, isIncomplete: true } : m')
    for callback in ('onSessionInit', 'onStepUpdate', 'onContextRef', 'onStatus', 'onContentReplace', 'onToken', 'onDone', 'onError'):
        import re
        s, count = re.subn(r'(' + callback + r': \([^)]*\) => \{)',
            r'\1\n              if (controller.signal.aborted) return;', s, count=1)
        assert count == 1, callback
    s = replace(s, '      } finally {\n        abortControllerRef.current = null;',
        '      } finally {\n        if (abortControllerRef.current === controller) abortControllerRef.current = null;')
    return s


stage(FE, 'src/features/ai-tutor/hooks/useSocraticStream.ts', hook)


def message(s):
    marker = '        {/* Nội dung Markdown chính có KaTeX, Mermaid và Vis-3D */}'
    return replace(s, marker, '''        {message.isStreaming && (!message.content || message.streamStatus) && (
          <div role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
            <span aria-hidden="true" className="size-2 rounded-full bg-primary motion-safe:animate-pulse" />
            {message.streamStatus && t.has(`streamStages.${message.streamStatus.stage}`)
              ? t(`streamStages.${message.streamStatus.stage}`) : t('streamWorking')}
          </div>
        )}
        {message.isIncomplete && (
          <p role="status" className="text-sm text-muted-foreground">{t('streamIncomplete')}</p>
        )}

''' + marker).replace('{!message.isStreaming && (', '{!message.isStreaming && !message.isIncomplete && (')


stage(FE, 'src/features/ai-tutor/components/AiTutorMessageItem.tsx', message)
stage(FE, 'src/features/ai-tutor/components/AiTutorChatCanvas.tsx', lambda s: replace(s,
    '{isTyping && (', "{isTyping && !messages.some((message) => message.isStreaming) && ("))

vi = {'understanding_request': 'Đang xác định nội dung bạn muốn tìm hiểu…',
      'retrieving_materials': 'Đang tìm học liệu liên quan…', 'connecting_concepts': 'Đang đối chiếu các khái niệm…',
      'evaluating_answer': 'Đang đối chiếu câu trả lời…', 'preparing_explanation': 'Đang chuẩn bị phản hồi…',
      'generating_exercise': 'Đang chuẩn bị bài tập…', 'validating_exercise': 'Đang kiểm tra bài tập…',
      'generating_diagram': 'Đang dựng sơ đồ…', 'saving_response': 'Đang lưu cuộc trò chuyện…'}
en = {'understanding_request': 'Understanding your request…', 'retrieving_materials': 'Finding relevant materials…',
      'connecting_concepts': 'Connecting related concepts…', 'evaluating_answer': 'Checking your answer…',
      'preparing_explanation': 'Preparing a response…', 'generating_exercise': 'Preparing an exercise…',
      'validating_exercise': 'Checking the exercise…', 'generating_diagram': 'Building a diagram…',
      'saving_response': 'Saving the conversation…'}


def translations(s, locale):
    data = json.loads(s)
    values = {'streamStages': vi if locale == 'vi' else en,
              'streamWorking': 'Đang xử lý…' if locale == 'vi' else 'Working…',
              'streamIncomplete': 'Phản hồi chưa hoàn tất. Bạn có thể gửi lại yêu cầu.' if locale == 'vi'
                  else 'The response is incomplete. You can send your request again.'}
    # Insert only the new keys; preserve unrelated formatting and translations.
    assert 'streamStages' not in data['aiTutor']
    marker = '"aiTutor": {'
    assert marker in s
    addition = json.dumps(values, ensure_ascii=False, indent=2)[2:-2]
    return s.replace(marker, marker + '\n' + '\n'.join('  ' + line for line in addition.splitlines()) + ',', 1)


for locale in ('vi', 'en'):
    stage(FE, f'src/messages/{locale}.json', lambda s, locale=locale: translations(s, locale))

report = '''# Socratic live SSE integration

Date: 2026-11-02
Plan: extend existing request DTO and SSE transport, handle status/live draft/replacement/final/error in the current chat UI. Authorized by the user's request to read and fix both projects.

STATUS: PARTIAL (runtime not verified)
SUMMARY: Protocol 2 fields pass through the Spring DTO. The existing authenticated student identity is preserved. The emitter relays event names/data/comments immediately and cancels upstream on disconnect. Frontend requests protocol 2, renders task status in the assistant bubble, appends tokens, replaces drafts, treats done.full_content as authoritative and marks interrupted/aborted streams incomplete.
CHECKS: static review only; compile/lint/typecheck/tests/build not run per the user's standing instruction. No app/DB/LLM calls.
ASSUMPTIONS: Python V2 is enabled and its current SSE contract is deployed. Frontend and Spring are separate projects. No new dependency or schema/config change.
LIMITATIONS: No automatic retry/resume or artifact renderer added. Each explicit send gets a new request ID; any future network retry must reuse the original payload. UI and Gateway behavior require manual verification.
DEPLOYMENT: not deployed.
NEXT: restart services and inspect protocol_version=2, status, token before done, content_replace and incomplete-stream behavior.

## Review
Removed fake successful completion on truncated streams; unknown/malformed events never become response text. Protocol 1 DTO default remains 1 for existing callers. No changes to login, UUID encoding, database selection, migrations or environment files.
'''
for root in (FE, BE):
    stage(root, 'reports/2026-11-02-socratic-live-sse-integration.md', lambda s: report if not s else (_ for _ in ()).throw(ValueError('Report already exists')))
    stage(root, 'TASKS.md', lambda s: replace(s, '## Done',
        '## Done\n- [x] 2026-11-02 — Socratic protocol 2 live SSE/status integration (runtime not verified): `reports/2026-11-02-socratic-live-sse-integration.md`'))
    stage(root, 'docs/api-spec.md', lambda s: s + '''

## Socratic SSE protocol 2 (2026-11-02)

POST chat/socratic/stream accepts protocol_version (1 or 2), client_request_id (UUID) and optional expected_state_version. Spring derives student_id from the authenticated user. Protocol 1 remains the default for existing callers; the tutor UI sends 2. Each new explicit send gets a new request ID. Retry transport with the same payload/ID; automatic retry is not implemented by this change.

Forward event names and JSON unchanged, without buffering: session_init, status, token, content_replace, context_ref, step_update, diagram_ready, exercise_ready, done, error. Comments are heartbeats. Status contains stage/state/message and describes real tasks, never private chain-of-thought. The UI localizes stage labels. Tokens append provisional text; content_replace replaces the whole draft; done.full_content replaces text and confirms persistence. Error or EOF before done marks the draft incomplete, never successful. Unknown events are ignored; artifact rendering remains outside this change.
''')

BASE.mkdir(parents=True, exist_ok=True)
(BASE / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f'Prepared {len(manifest)} files; external repositories unchanged.')
