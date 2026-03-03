# rate_limiter.py - 滑動窗口 Rate Limiter，避免 API 帳號被封鎖
import time
import threading
from collections import deque
from typing import Deque, Optional


class SlidingWindowRateLimiter:
    """滑動窗口：在 window_sec 秒內最多允許 max_requests 次請求。"""

    def __init__(self, max_requests: int, window_sec: float, name: str = "default"):
        self.max_requests = max_requests
        self.window_sec = window_sec
        self.name = name
        self._timestamps: Deque[float] = deque()
        self._lock = threading.Lock()

    def _evict_expired(self, now: float) -> None:
        cutoff = now - self.window_sec
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def acquire(self) -> None:
        """阻塞直到可以安全發送一次請求。"""
        with self._lock:
            now = time.monotonic()
            self._evict_expired(now)
            if len(self._timestamps) >= self.max_requests:
                sleep_until = self._timestamps[0] + self.window_sec
                sleep_time = max(0.0, sleep_until - now)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                now = time.monotonic()
                self._evict_expired(now)
            self._timestamps.append(now)

    def record_request(self) -> None:
        """僅記錄一次請求（不阻塞），用於與外部 API 呼叫搭配。"""
        with self._lock:
            now = time.monotonic()
            self._evict_expired(now)
            self._timestamps.append(now)

    def wait_if_needed(self) -> None:
        """若已達上限則等待，否則直接通過。等同 acquire()。"""
        self.acquire()
