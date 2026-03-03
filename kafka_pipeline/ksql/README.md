# ksqlDB 腳本說明（Phase 2）

## 啟動順序

1. 啟動 Kafka + ksqlDB：`docker compose -f kafka_pipeline/docker-compose.yml up -d`
2. 等待 ksqlDB 就緒：`docker compose -f kafka_pipeline/docker-compose.yml exec ksqldb-server curl -s http://localhost:8088/info`
3. 依序執行 KSQL（先建立 Stream，再建立 Table）：
   - `01_stream_social_mentions.ksql`：建立 `social_mentions_raw`、`social_mentions_by_creator`
   - `02_trending_creators_sliding_window.ksql`：建立 1h/24h 視窗與 `trending-creators` Topic

## 執行方式

```bash
# 進入 ksqlDB CLI 後貼上腳本內容，或：
docker compose -f kafka_pipeline/docker-compose.yml exec ksqldb-cli ksql http://ksqldb-server:8088 -f /path/to/01_stream_social_mentions.ksql
```

## Topic 對應

| Topic / Table        | 說明 |
|----------------------|------|
| `social-mentions`    | Phase 1 Producer 寫入的原始貼文 |
| `trending_creators_1h` | 1 小時窗口創作者提及數 |
| `trending_creators_24h` | 24 小時窗口創作者提及數 |
| `trending-creators`   | 即時輸出 1h 提及數，下游可取 Top 10 |

「今日成長最快 Top 10」可由消費 `trending-creators` 的服務依 `mention_count_1h` 排序取前 10 筆實作。
