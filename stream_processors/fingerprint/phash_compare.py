# phash_compare.py - 下載圖片、計算 pHash、與資料庫比對
import io
import logging
from typing import Optional, Tuple

import imagehash
import requests
from PIL import Image

from config import PHASH_SIZE, SIMILARITY_THRESHOLD
from phash_store import load_protected_hashes, insert_leak_alert

logger = logging.getLogger(__name__)

# 64-bit hash -> 最大漢明距離 64
MAX_HAMMING = 64


def _hex_to_hash(hex_str: str) -> imagehash.ImageHash:
    return imagehash.hex_to_hash(hex_str)


def _similarity_from_distance(distance: int, max_bits: int = MAX_HAMMING) -> float:
    return 1.0 - (distance / max_bits)


def download_image(url: str, timeout: int = 15) -> Optional[Image.Image]:
    """下載圖片並回傳 PIL Image，失敗回傳 None。"""
    try:
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content))
        img.load()
        return img.convert("RGB")
    except Exception as e:
        logger.warning("Download failed for %s: %s", url, e)
        return None


def compute_phash(image: Image.Image, hash_size: int = PHASH_SIZE) -> imagehash.ImageHash:
    return imagehash.phash(image, hash_size=hash_size)


def find_best_match(
    candidate_hex: str,
    protected: Optional[list] = None,
) -> Optional[Tuple[int, str, float]]:
    """
    與資料庫內受保護 pHash 比對，回傳 (matched_id, phash_hex, similarity) 或 None。
    similarity 為 0~1，僅在 >= SIMILARITY_THRESHOLD 時視為匹配。
    """
    if protected is None:
        protected = load_protected_hashes()
    try:
        candidate = _hex_to_hash(candidate_hex)
    except Exception as e:
        logger.warning("Invalid candidate hash %s: %s", candidate_hex[:16], e)
        return None

    best_id, best_hex, best_sim = None, None, 0.0
    for pid, phex in protected:
        try:
            ref = _hex_to_hash(phex)
            dist = candidate - ref
            sim = _similarity_from_distance(dist)
            if sim > best_sim:
                best_sim = sim
                best_id = pid
                best_hex = phex
        except Exception as e:
            logger.debug("Skip protected id %s: %s", pid, e)
            continue

    if best_sim >= SIMILARITY_THRESHOLD:
        return (best_id, best_hex, best_sim)
    return None


def process_image_url(url: str) -> bool:
    """
    下載圖片、計算 pHash、若與資料庫相似度 > 閾值則觸發警告並寫入 PostgreSQL。
    回傳是否觸發警告。
    """
    img = download_image(url)
    if img is None:
        return False
    phash = compute_phash(img)
    phash_hex = str(phash)
    protected = load_protected_hashes()
    match = find_best_match(phash_hex, protected=protected)
    if match is None:
        return False
    matched_id, _, similarity = match
    similarity_pct = round(similarity * 100, 2)
    insert_leak_alert(
        leaked_url=url,
        matched_phash_id=matched_id,
        similarity_pct=similarity_pct,
        raw_phash_hex=phash_hex,
        metadata={"source": "forum-image-links"},
    )
    return True
