# twitter_client.py - 使用 Twitter/X API v2 搜尋含創作者 ID 或 OnlyFans 連結的貼文
import logging
import re
from typing import Any, Dict, Generator, List, Optional

import tweepy
from tweepy import Client

from config import TWITTER_BEARER_TOKEN
from rate_limiter import SlidingWindowRateLimiter
from config import (
    TWITTER_RATE_LIMIT_REQUESTS,
    TWITTER_RATE_LIMIT_WINDOW_SEC,
)

logger = logging.getLogger(__name__)

# 僅作範例：可改為從設定或 DB 讀取
ONLYFANS_LINK_PATTERN = re.compile(
    r"https?://(?:www\.)?onlyfans\.com/[a-zA-Z0-9_-]+",
    re.IGNORECASE,
)
CREATOR_ID_PATTERN = re.compile(r"@([a-zA-Z0-9_]{1,15})\b")  # 簡易創作者 handle


def _contains_target(content: str) -> bool:
    """貼文是否包含 OnlyFans 連結或目標創作者 ID（可擴充）。"""
    if ONLYFANS_LINK_PATTERN.search(content):
        return True
    # 可改為白名單創作者 ID 列表
    return bool(CREATOR_ID_PATTERN.search(content))


def _extract_creator_refs(text: str) -> List[str]:
    refs = []
    for m in ONLYFANS_LINK_PATTERN.finditer(text):
        refs.append(m.group(0))
    for m in CREATOR_ID_PATTERN.finditer(text):
        refs.append(f"@{m.group(1)}")
    return list(dict.fromkeys(refs))  # 去重保留順序


class TwitterStreamClient:
    """在遵守 Rate Limit 下查詢推文並 yield 符合條件的結果。"""

    def __init__(
        self,
        bearer_token: str = TWITTER_BEARER_TOKEN,
        rate_limiter: Optional[SlidingWindowRateLimiter] = None,
    ):
        self._client: Optional[Client] = None
        self._bearer_token = bearer_token
        self._limiter = rate_limiter or SlidingWindowRateLimiter(
            TWITTER_RATE_LIMIT_REQUESTS,
            TWITTER_RATE_LIMIT_WINDOW_SEC,
            name="twitter",
        )

    def _ensure_client(self) -> Client:
        if self._client is None:
            if not self._bearer_token:
                raise ValueError("TWITTER_BEARER_TOKEN is required")
            self._client = Client(bearer_token=self._bearer_token)
        return self._client

    def search_recent(
        self,
        query: str,
        max_results: int = 10,
        tweet_fields: Optional[List[str]] = None,
        user_fields: Optional[List[str]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """搜尋近期推文，只 yield 含 OnlyFans 連結或創作者 ID 的貼文。"""
        client = self._ensure_client()
        tweet_fields = tweet_fields or ["created_at", "public_metrics", "author_id"]
        user_fields = user_fields or ["username"]

        self._limiter.wait_if_needed()
        resp = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            expansions=["author_id"],
        )

        if resp.data is None:
            return

        users_list = getattr(resp.includes, "users", None) or (resp.includes.get("users") if resp.includes else None) or []
        users = {}
        for u in users_list:
            uid = getattr(u, "id", None) or u.get("id")
            if uid:
                users[uid] = u
        for tweet in resp.data:
            data = getattr(tweet, "data", None) or tweet
            text = data.get("text", "")
            if not _contains_target(text):
                continue
            author_id = data.get("author_id")
            author = users.get(author_id) or {}
            uname = getattr(author, "username", None) or getattr(getattr(author, "data", None), "username", None) or author.get("username")
            payload = {
                "source": "twitter",
                "id": data.get("id"),
                "text": text,
                "created_at": data.get("created_at"),
                "author_id": author_id,
                "author_username": uname,
                "creator_refs": _extract_creator_refs(text),
            }
            yield payload
