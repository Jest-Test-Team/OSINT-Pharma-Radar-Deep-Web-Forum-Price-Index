---
name: ""
overview: ""
todos: []
isProject: false
---

# Cursor 開發計畫：Pharma Radar

## Phase 1: 基礎建設與爬蟲 (Producers)

- [ ] 撰寫 `docker-compose.yml` 啟動單節點 Kafka 與 Zookeeper。

- [ ] 開發 Telegram Listener，監聽特定測試頻道，並將原始訊息以 JSON 格式打入 Kafka `raw-telegram-messages` Topic。

- [ ] 實作代理 IP 池機制，確保網頁爬蟲不會輕易被封鎖。

## Phase 2: 串流處理 (Stream Processing)

- [ ] 使用 Python Faust 或 KSQL 建立 Consumer。

- [ ] 實作 NLP 正則表達式，從 `raw-telegram-messages` 中萃取出「物品名稱」、「價格」、「幣種」、「地區」。

- [ ] 將清洗後的結構化數據打入 `cleaned-market-data` Topic。

## Phase 3: 儲存與可視化 (Sink)

- [ ] 設定 Kafka Elasticsearch Sink Connector。

- [ ] 在 Kibana 建立 K-Line (K線圖) 來顯示特定物品的價格波動。