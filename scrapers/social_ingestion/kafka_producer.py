# kafka_producer.py - 將含創作者 ID 或 OnlyFans 連結的貼文打入 social-mentions Topic
import json
import logging
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_SOCIAL_MENTIONS

logger = logging.getLogger(__name__)


def _json_serializer(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


class SocialMentionsProducer:
    def __init__(
        self,
        bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS,
        topic: str = KAFKA_TOPIC_SOCIAL_MENTIONS,
    ):
        self.topic = topic
        self._producer: Optional[KafkaProducer] = None
        self._bootstrap_servers = bootstrap_servers

    def _ensure_producer(self) -> KafkaProducer:
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=_json_serializer,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
            )
        return self._producer

    def send(self, payload: Dict[str, Any], key: Optional[str] = None) -> None:
        """發送一筆 social mention 到 Topic。"""
        producer = self._ensure_producer()
        try:
            future = producer.send(self.topic, value=payload, key=key)
            future.get(timeout=10)
        except KafkaError as e:
            logger.exception("Kafka send failed: %s", e)
            raise

    def flush(self) -> None:
        if self._producer:
            self._producer.flush()

    def close(self) -> None:
        if self._producer:
            self._producer.close()
            self._producer = None
