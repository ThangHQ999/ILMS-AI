from collections import defaultdict
from app.core.config import settings


class TopicContextService:
    def choose(self, rows, ranked_chunk_ids, code, previous, explicit_switch=False):
        scores, topics = defaultdict(float), {}
        rank = {cid: 1 / (i + 1) for i, cid in enumerate(ranked_chunk_ids)}
        for row in rows:
            tid = row['id']
            topics[tid] = row
            # Max evidence avoids a large topic winning only through chunk count.
            scores[tid] = max(scores[tid], rank.get(row['chunk_id'], 0))
        for tid, row in topics.items():
            if code and code in row['concepts']:
                scores[tid] += 0.2
            if tid == previous and not explicit_switch:
                scores[tid] += 0.15
        ordered = sorted(scores, key=lambda tid: (-scores[tid], tid))
        if not ordered:
            return None, None
        if len(ordered) > 1 and scores[ordered[0]] - scores[ordered[1]] < settings.SOCRATIC_TOPIC_MARGIN:
            chosen = previous if previous in topics and not explicit_switch else None
        else:
            chosen = ordered[0]
        return chosen, topics[chosen]['name'] if chosen else None
