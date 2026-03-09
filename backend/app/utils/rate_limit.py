import time
from collections import defaultdict, deque
from threading import Lock


class SlidingWindowRateLimiter:
    def __init__(self, max_attempts=5, window_seconds=60):
        self.max_attempts = int(max(1, max_attempts))
        self.window_seconds = int(max(1, window_seconds))
        self._events = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key):
        current_time = time.time()
        with self._lock:
            queue = self._events[str(key or "unknown")]
            while queue and (current_time - queue[0]) > self.window_seconds:
                queue.popleft()
            if len(queue) >= self.max_attempts:
                return False
            queue.append(current_time)
            return True

    def reset(self, key):
        with self._lock:
            self._events.pop(str(key or "unknown"), None)
