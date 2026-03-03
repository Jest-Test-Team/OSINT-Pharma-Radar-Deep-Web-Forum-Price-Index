# config.py - 從環境變數載入 API 與 Kafka 設定，不將密鑰寫入程式碼
import os
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# Twitter / X API v2
TWITTER_BEARER_TOKEN = get_env("TWITTER_BEARER_TOKEN")

# Reddit API (https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID = get_env("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = get_env("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = get_env("REDDIT_USER_AGENT", "PharmaRadar/1.0 by YourBot")

# Kafka
KAFKA_BOOTSTRAP_SERVERS = get_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_SOCIAL_MENTIONS = get_env("KAFKA_TOPIC_SOCIAL_MENTIONS", "social-mentions")

# Rate limits (requests per window) - 依各 API 條款調整
TWITTER_RATE_LIMIT_REQUESTS = int(get_env("TWITTER_RATE_LIMIT_REQUESTS", "300"))
TWITTER_RATE_LIMIT_WINDOW_SEC = int(get_env("TWITTER_RATE_LIMIT_WINDOW_SEC", "900"))  # 15 min
REDDIT_RATE_LIMIT_REQUESTS = int(get_env("REDDIT_RATE_LIMIT_REQUESTS", "60"))
REDDIT_RATE_LIMIT_WINDOW_SEC = int(get_env("REDDIT_RATE_LIMIT_WINDOW_SEC", "60"))  # 1 min
