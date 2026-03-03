---
name: ""
overview: ""
todos: []
isProject: false
---

# Cursor 開發計畫：Adult-Content Alpha

## Phase 1: 海量社群資料接入

- [ ] 註冊 Twitter/X 開發者 API 與 Reddit API。

- [ ] 建立 Kafka Producer，將包含目標創作者 ID 或 OnlyFans 連結的貼文打入 `social-mentions` Topic。

- [ ] 實作 Rate Limit 處理機制，避免 API 帳號被封鎖。

## Phase 2: ksqlDB 實時聚合計算

- [ ] 啟動 ksqlDB Server。

- [ ] 撰寫 KSQL 語法，建立 1 小時與 24 小時的「滑動窗口 (Sliding Window)」。

- [ ] 即時計算並輸出「今日成長最快 Top 10 創作者」到 `trending-creators` Topic。

## Phase 3: 盜版指紋比對防護

- [ ] 建立一個已知受版權保護的影像 pHash 資料庫。

- [ ] 當監聽到論壇有新圖片連結時，自動下載並計算 pHash。

- [ ] 若與資料庫相似度 > 90%，觸發警告並記錄外流網址至 PostgreSQL。