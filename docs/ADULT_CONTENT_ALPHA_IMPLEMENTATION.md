# Adult-Content Alpha 實作說明

本文件對應 `.cursor/plans/cursor1.plan.md` 三階段實作。

## Phase 1：海量社群資料接入

- **位置**：`scrapers/social_ingestion/`
- **內容**：
  - **Twitter/X**：需註冊 [Twitter Developer](https://developer.twitter.com/) 取得 Bearer Token，設定 `TWITTER_BEARER_TOKEN`。
  - **Reddit**：於 [Reddit App](https://www.reddit.com/prefs/apps) 建立 script 型應用，設定 `REDDIT_CLIENT_ID`、`REDDIT_CLIENT_SECRET`、`REDDIT_USER_AGENT`。
  - **Kafka Producer**：將含目標創作者 ID 或 OnlyFans 連結的貼文寫入 `social-mentions` Topic（JSON）。
  - **Rate Limit**：`rate_limiter.py` 滑動窗口限制，避免 API 帳號被封鎖。
- **執行**：
  ```bash
  cd scrapers/social_ingestion && pip install -r requirements.txt
  cp .env.example .env  # 填入 API 與 Kafka 設定
  python run_producer.py
  ```

## Phase 2：ksqlDB 實時聚合計算

- **位置**：`kafka_pipeline/`
- **內容**：
  - `docker-compose.yml`：Zookeeper、Kafka、ksqlDB Server。
  - `ksql/01_stream_social_mentions.ksql`：建立 `social_mentions_raw`、`social_mentions_by_creator`（EXPLODE creator_refs）。
  - `ksql/02_trending_creators_sliding_window.ksql`：1 小時與 24 小時 Tumbling 窗口，輸出至 `trending-creators` Topic。
- **執行**：
  ```bash
  docker compose -f kafka_pipeline/docker-compose.yml up -d
  # 依序執行 01、02 KSQL（見 kafka_pipeline/ksql/README.md）
  ```
- **Top 10**：消費 `trending-creators` 的服務依 `mention_count_1h` 排序取前 10 即為「今日成長最快 Top 10 創作者」。

## Phase 3：盜版指紋比對防護

- **位置**：`stream_processors/fingerprint/`、`database/migrations/`
- **內容**：
  - **pHash 資料庫**：`database/migrations/001_create_protected_hashes_and_leak_alerts.sql` 建立 `protected_image_hashes`、`leak_alerts`。
  - **比對流程**：監聽 `forum-image-links` Topic → 下載圖片 → 計算 pHash（imagehash）→ 與 `protected_image_hashes` 比對 → 相似度 > 90% 則寫入 `leak_alerts` 並記錄外流網址。
  - **種子資料**：`seed_protected_hash.py` 可將已知受保護影像的 pHash 寫入資料庫。
- **執行**：
  ```bash
  psql $DATABASE_URL -f database/migrations/001_create_protected_hashes_and_leak_alerts.sql
  cd stream_processors/fingerprint && pip install -r requirements.txt
  python seed_protected_hash.py --image path/to/protected.jpg --identifier "rights_holder_1"
  python run_consumer.py
  ```
- **論壇圖片來源**：需由論壇爬蟲（如 `scrapers/forum_spider`）將新圖片連結以 `{"url": "https://..."}` 寫入 `forum-image-links` Topic。

## 依賴關係

1. Phase 1 與 Phase 2 共用 Kafka；Phase 1 寫入 `social-mentions`，Phase 2 消費並產出 `trending-creators`。
2. Phase 3 依賴 Kafka（`forum-image-links`）與 PostgreSQL（migration + 指紋庫）；論壇爬蟲需另行實作並寫入圖片連結。

## 注意事項

- API 金鑰與 `DATABASE_URL` 勿提交至版控，請使用 `.env` 並參考各模組 `.env.example`。
- 本實作僅供技術與架構演練，請遵守各平台 API 條款與當地法規。
