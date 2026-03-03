# phash_store.py - 受保護影像 pHash 的讀取與比對（PostgreSQL）
import logging
from contextlib import contextmanager
from typing import List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor, Json

from config import DATABASE_URL

logger = logging.getLogger(__name__)


@contextmanager
def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_protected_hashes(conn=None) -> List[Tuple[int, str]]:
    """回傳 (id, phash_hex) 列表，供比對用。"""
    rows = []
    own_conn = False
    if conn is None:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        own_conn = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, phash_hex FROM protected_image_hashes")
            rows = [(r["id"], r["phash_hex"]) for r in cur.fetchall()]
    finally:
        if own_conn:
            conn.close()
    return rows


def insert_leak_alert(
    leaked_url: str,
    matched_phash_id: int,
    similarity_pct: float,
    raw_phash_hex: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    """寫入一筆外流警告至 leak_alerts。"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO leak_alerts
                (leaked_url, matched_phash_id, similarity_pct, raw_phash_hex, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (leaked_url, matched_phash_id, similarity_pct, raw_phash_hex, Json(metadata) if metadata else None),
            )
    logger.info(
        "Leak alert recorded: url=%s matched_id=%s similarity=%.2f",
        leaked_url, matched_phash_id, similarity_pct,
    )
