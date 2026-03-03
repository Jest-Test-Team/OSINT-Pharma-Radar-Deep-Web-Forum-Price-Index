# run_producer.py - 主程式：輪流從 Twitter / Reddit 拉取並打入 social-mentions Topic
import logging
import os
import sys
import time

from config import (
    KAFKA_TOPIC_SOCIAL_MENTIONS,
    REDDIT_CLIENT_ID,
    TWITTER_BEARER_TOKEN,
)
from kafka_producer import SocialMentionsProducer
from reddit_client import RedditStreamClient
from twitter_client import TwitterStreamClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_twitter_cycle(producer: SocialMentionsProducer, query: str = "onlyfans") -> int:
    count = 0
    try:
        client = TwitterStreamClient()
        for payload in client.search_recent(query=query, max_results=50):
            producer.send(payload, key=payload.get("id"))
            count += 1
            logger.info("Twitter mention sent: %s", payload.get("id"))
    except Exception as e:
        logger.exception("Twitter cycle failed: %s", e)
    return count


def run_reddit_cycle(
    producer: SocialMentionsProducer,
    subreddit: str = "all",
    query: str = "onlyfans",
) -> int:
    count = 0
    try:
        client = RedditStreamClient()
        for payload in client.search_subreddit(subreddit, query=query, limit=50):
            producer.send(payload, key=payload.get("id"))
            count += 1
            logger.info("Reddit mention sent: %s", payload.get("id"))
    except Exception as e:
        logger.exception("Reddit cycle failed: %s", e)
    return count


def main() -> None:
    if not TWITTER_BEARER_TOKEN and not REDDIT_CLIENT_ID:
        logger.error(
            "Set at least one of TWITTER_BEARER_TOKEN or REDDIT_CLIENT_ID (and REDDIT_CLIENT_SECRET)."
        )
        sys.exit(1)

    producer = SocialMentionsProducer()
    interval_sec = int(os.environ.get("POLL_INTERVAL_SEC", "300"))

    try:
        while True:
            total = 0
            if TWITTER_BEARER_TOKEN:
                total += run_twitter_cycle(producer)
            if REDDIT_CLIENT_ID:
                total += run_reddit_cycle(producer)
            producer.flush()
            logger.info("Cycle done, sent %d mentions. Sleeping %ds.", total, interval_sec)
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
