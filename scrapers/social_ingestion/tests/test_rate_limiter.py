# tests/test_rate_limiter.py - 滑動窗口 Rate Limiter 單元測試
# 請在 scrapers/social_ingestion 目錄下執行：python -m pytest tests/ -v
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import pytest
from rate_limiter import SlidingWindowRateLimiter


def test_under_limit_no_wait() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=5, window_sec=1.0, name="test")
    t0 = time.monotonic()
    for _ in range(3):
        limiter.acquire()
    elapsed = time.monotonic() - t0
    assert elapsed < 0.5  # 未達上限不應明顯等待


def test_over_limit_waits() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_sec=0.3, name="test")
    t0 = time.monotonic()
    for _ in range(3):
        limiter.acquire()
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.25  # 第三次應等窗口滑過


def test_record_request() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_sec=1.0, name="test")
    limiter.record_request()
    limiter.record_request()
    t0 = time.monotonic()
    limiter.wait_if_needed()  # 第三次應等待
    assert time.monotonic() - t0 >= 0.5
