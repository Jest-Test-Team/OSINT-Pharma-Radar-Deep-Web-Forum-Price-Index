# config.py - 指紋比對服務設定
import os
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# Kafka：監聽論壇新圖片連結的 Topic（可由 forum_spider 寫入）
KAFKA_BOOTSTRAP_SERVERS = get_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_IMAGE_LINKS = get_env("KAFKA_TOPIC_IMAGE_LINKS", "forum-image-links")
KAFKA_GROUP_ID = get_env("KAFKA_GROUP_ID", "fingerprint-matcher")

# PostgreSQL
DATABASE_URL = get_env(
    "DATABASE_URL",
    "postgresql://localhost:5432/pharma_radar?user=postgres&password=postgres",
)

# 相似度閾值（0~1），超過則觸發警告並寫入 leak_alerts
SIMILARITY_THRESHOLD = float(get_env("SIMILARITY_THRESHOLD", "0.90"))

# pHash 位元大小（imagehash 預設 8 -> 64 bits）
PHASH_SIZE = int(get_env("PHASH_SIZE", "8"))
