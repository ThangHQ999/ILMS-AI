from app.schema.tutoring_contracts import TeachingAction, Verdict


class PedagogicalPolicy:
    """Deterministic decisions; an LLM never directly updates progress."""
    def decide(self, intent, evaluation, state, bundle, learner):
        action = self._decide(intent, evaluation, state, bundle, learner)
        # A learner attempt still needs scaffolding when no gradable pending exists.
        # Never turn an ungraded attempt into a full worked solution.
        restricted = (
            bool(evaluation and evaluation.verdict in {Verdict.PARTIAL, Verdict.INCORRECT})
            or action.kind in {'SCAFFOLD', 'REMEDIATE'}
            or intent.is_practice_attempt or intent.asks_for_solution
        )
        if restricted and not intent.explicit_switch and action.kind not in {
                'CLOSE', 'RECHECK', 'REQUEST_EXERCISE', 'REQUEST_DIAGRAM', 'ADVANCE'}:
            action.support_scope = 'SINGLE_STEP'
            if action.kind == 'EXPLAIN':
                action.kind = 'SCAFFOLD'
                action.ask_question = True
                action.hint_level = min(4, state.hint_level + 1)
            action.directive += (
                ' Chỉ gỡ một điểm vướng và để học sinh thực hiện bước tiếp theo. '
                'Không tính hộ kết quả, không trình bày chuỗi suy ra còn lại hoặc đáp án cuối; '
                'hint cao dùng ví dụ khác. Không tự bảo vệ lời giải thích trước của AI.')
        return action

    def _decide(self, intent, evaluation, state, bundle, learner):
        objective = state.objective or 'MEANING'
        if intent.intent == 'CLOSE_DISCUSSION':
            return TeachingAction(kind='CLOSE', directive='Kết thúc nhẹ nhàng, không ép làm bài kiểm tra.')
        if intent.intent == 'CHALLENGE_TUTOR':
            return TeachingAction(kind='RECHECK', objective=objective, preserve_pending=True,
                directive='Kiểm tra lại phát biểu trước bằng nguồn. Nếu sai thì sửa rõ ràng, không đổ lỗi người học.')
        if not bundle.sources or 'AMBIGUOUS_CONCEPT' in bundle.warnings:
            return TeachingAction(kind='CLARIFY', directive='Nêu giới hạn nguồn/ngữ cảnh; hỏi một câu phân biệt nếu cần, không đoán.',
                objective=objective, preserve_pending=True)
        if intent.intent in {'REQUEST_EXERCISE', 'REQUEST_DIAGRAM'}:
            return TeachingAction(kind=intent.intent, directive='Chuẩn bị artifact theo mục tiêu; không lộ đáp án bài đang làm.',
                objective=objective, hint_level=state.hint_level, preserve_pending=True)
        if intent.intent in {'REQUEST_HINT', 'EXPRESS_CONFUSION', 'REQUEST_EXAMPLE'}:
            return TeachingAction(kind='SCAFFOLD', objective=objective,
                hint_level=min(4, state.hint_level + 1), ask_question=True,
                directive='Giải thích ngắn và đổi ví dụ/biểu diễn; không hỏi lại nguyên câu cũ. Không tính là trả lời sai.')
        if evaluation:
            if evaluation.verdict == Verdict.CORRECT:
                return TeachingAction(kind='ADVANCE', objective=objective, advance=True,
                    ask_question=intent.practice_requested or state.mode != 'CONCEPT' or state.pending is not None,
                    hint_level=max(0, state.hint_level - 1),
                    directive='Xác nhận điểm đúng cụ thể. Kiểm tra một khía cạnh/tình huống mới nếu cần, không tuyên bố thành thạo toàn khái niệm.')
            if evaluation.verdict == Verdict.PARTIAL:
                return TeachingAction(kind='FOCUS_GAP', objective=objective, ask_question=True,
                    hint_level=state.hint_level,
                    directive='Công nhận phần đúng rồi hỏi đúng phần thiếu; không yêu cầu lại điều đã thể hiện được.')
            if evaluation.verdict == Verdict.INCORRECT:
                return TeachingAction(kind='COUNTEREXAMPLE', objective=objective, ask_question=True,
                    hint_level=min(4, state.hint_level + 1),
                    directive='Dựa vào bằng chứng để chỉ ra điểm vướng, dùng phản ví dụ/giải thích ngắn và câu hỏi nhỏ hơn.')
            return TeachingAction(kind='CLARIFY', objective=objective, preserve_pending=True,
                directive='Chưa đủ căn cứ để chấm. Hỏi làm rõ hoặc giải thích lại, không nhận xét là sai.')
        return TeachingAction(kind='EXPLAIN', objective='DISTINCTION' if intent.intent == 'COMPARE' else 'MEANING',
            ask_question=intent.practice_requested,
            directive='Trả lời nhu cầu trước bằng giải thích dễ tiếp cận và ví dụ; không ép kiểm tra khi chỉ hỏi định nghĩa.')
