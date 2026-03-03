# run_consumer.py - 監聽 forum-image-links Topic，對每筆圖片連結下載並比對 pHash
import json
import logging
import os

from kafka import KafkaConsumer

from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    KAFKA_TOPIC_IMAGE_LINKS,
)
from phash_compare import process_image_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    consumer = KafkaConsumer(
        KAFKA_TOPIC_IMAGE_LINKS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
        auto_offset_reset="earliest",
    )
    logger.info("Consuming topic %s", KAFKA_TOPIC_IMAGE_LINKS)

    for msg in consumer:
        try:
            payload = msg.value
            if not payload:
                continue
            # 支援 { "url": "https://..." } 或 { "image_url": "..." }
            url = payload.get("url") or payload.get("image_url")
            if not url or not isinstance(url, str):
                logger.debug("Skip message without url: %s", payload)
                continue
            if process_image_url(url):
                logger.info("Leak alert triggered for %s", url)
        except Exception as e:
            logger.exception("Process message failed: %s", e)


if __name__ == "__main__":
    main()
