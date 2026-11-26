from collections import OrderedDict
from copy import deepcopy
from time import monotonic
from app.core.config import settings


class ContextCache:
    """Bounded, per-worker knowledge cache; never caches learner decisions."""
    def __init__(self):
        self.entries = OrderedDict()

    def get(self, key):
        item = self.entries.get(key)
        if not item:
            return None
        expires, value = item
        if monotonic() >= expires:
            self.entries.pop(key, None)
            return None
        self.entries.move_to_end(key)
        result = deepcopy(value)
        result.cache_hit = True
        return result

    def put(self, key, value):
        if not settings.SOCRATIC_CACHE_SECONDS:
            return
        self.entries[key] = (monotonic() + settings.SOCRATIC_CACHE_SECONDS, deepcopy(value))
        self.entries.move_to_end(key)
        while len(self.entries) > settings.SOCRATIC_CACHE_SIZE:
            self.entries.popitem(last=False)

    def clear(self):
        self.entries.clear()


knowledge_cache = ContextCache()
