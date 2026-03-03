# reddit_client.py - 使用 Reddit API 搜尋含創作者 ID 或 OnlyFans 連結的貼文
import logging
import re
from typing import Any, Dict, Generator, List, Optional

import praw
from praw.models import Submission

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_RATE_LIMIT_REQUESTS,
    REDDIT_RATE_LIMIT_WINDOW_SEC,
)
from rate_limiter import SlidingWindowRateLimiter

logger = logging.getLogger(__name__)

ONLYFANS_LINK_PATTERN = re.compile(
    r"https?://(?:www\.)?onlyfans\.com/[a-zA-Z0-9_-]+",
    re.IGNORECASE,
)
CREATOR_ID_PATTERN = re.compile(r"@([a-zA-Z0-9_]{1,15})\b")


def _contains_target(content: str) -> bool:
    if ONLYFANS_LINK_PATTERN.search(content):
        return True
    return bool(CREATOR_ID_PATTERN.search(content))


def _extract_creator_refs(text: str) -> List[str]:
    refs = []
    for m in ONLYFANS_LINK_PATTERN.finditer(text):
        refs.append(m.group(0))
    for m in CREATOR_ID_PATTERN.finditer(text):
        refs.append(f"@{m.group(1)}")
    return list(dict.fromkeys(refs))


class RedditStreamClient:
    """在遵守 Rate Limit 下查詢 Reddit 貼文並 yield 符合條件的結果。"""

    def __init__(
        self,
        client_id: str = REDDIT_CLIENT_ID,
        client_secret: str = REDDIT_CLIENT_SECRET,
        user_agent: str = REDDIT_USER_AGENT,
        rate_limiter: Optional[SlidingWindowRateLimiter] = None,
    ):
        self._reddit: Optional[praw.Reddit] = None
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent
        self._limiter = rate_limiter or SlidingWindowRateLimiter(
            REDDIT_RATE_LIMIT_REQUESTS,
            REDDIT_RATE_LIMIT_WINDOW_SEC,
            name="reddit",
        )

    def _ensure_reddit(self) -> praw.Reddit:
        if self._reddit is None:
            if not self._client_id or not self._client_secret:
                raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are required")
            self._reddit = praw.Reddit(
                client_id=self._client_id,
                client_secret=self._client_secret,
                user_agent=self._user_agent,
            )
        return self._reddit

    def search_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int = 25,
        sort: str = "relevance",
    ) -> Generator[Dict[str, Any], None, None]:
        """搜尋指定 subreddit，只 yield 含 OnlyFans 或創作者 ID 的貼文。"""
        reddit = self._ensure_reddit()
        self._limiter.wait_if_needed()
        sub = reddit.subreddit(subreddit_name)
        results = sub.search(query, sort=sort, limit=min(limit, 100))

        for post in results:
            if not isinstance(post, Submission):
                continue
            content = (post.title or "") + " " + (post.selftext or "")
            if not _contains_target(content):
                continue
            payload = {
                "source": "reddit",
                "id": post.id,
                "subreddit": subreddit_name,
                "title": post.title,
                "selftext": post.selftext,
                "created_utc": post.created_utc,
                "author": getattr(post.author, "name", None) if post.author else None,
                "url": f"https://reddit.com{post.permalink}",
                "creator_refs": _extract_creator_refs(content),
            }
            yield payload
