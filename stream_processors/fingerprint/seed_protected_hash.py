# seed_protected_hash.py - 將已知受保護影像的 pHash 寫入資料庫（單張或目錄）
"""用法:
  python seed_protected_hash.py --image path/to/image.jpg
  python seed_protected_hash.py --dir path/to/images/ --identifier "rights_holder_1"
"""
import argparse
import logging
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from PIL import Image

from config import DATABASE_URL, PHASH_SIZE
from phash_compare import compute_phash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS protected_image_hashes (
                id BIGSERIAL PRIMARY KEY,
                phash_hex VARCHAR(32) NOT NULL,
                source_identifier VARCHAR(512),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(phash_hex)
            )
        """)
    conn.commit()


def insert_hash(conn, phash_hex: str, source_identifier: str = "") -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO protected_image_hashes (phash_hex, source_identifier) VALUES (%s, %s) ON CONFLICT (phash_hex) DO NOTHING",
            (phash_hex, source_identifier),
        )
    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="單張圖片路徑")
    parser.add_argument("--dir", type=str, help="圖片目錄（遞迴）")
    parser.add_argument("--identifier", type=str, default="", help="來源識別（如權利人代號）")
    args = parser.parse_args()

    if not args.image and not args.dir:
        parser.print_help()
        sys.exit(1)

    paths = []
    if args.image:
        paths.append(Path(args.image))
    if args.dir:
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            paths.extend(Path(args.dir).rglob(ext))

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        ensure_schema(conn)
        for p in paths:
            if not p.is_file():
                continue
            try:
                img = Image.open(p).convert("RGB")
                h = compute_phash(img, hash_size=PHASH_SIZE)
                insert_hash(conn, str(h), args.identifier or p.name)
                logger.info("Inserted phash for %s", p)
            except Exception as e:
                logger.warning("Skip %s: %s", p, e)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
