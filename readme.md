# 💊 OSINT Pharma Radar (Deep Web/Forum Price Index)

## 專案簡介
這是一個開源情報（OSINT）與市場流動性分析工具。透過爬取特定論壇、Telegram 頻道與灰色電商平台的數據，利用 Apache Kafka 進行實時資料串流與 NLP 關鍵字萃取，建立「特定化學品/藥物」的價格指數與純度評價資料庫。

## ⚠️ 法律與免責聲明
本專案僅供技術研究與 Kafka 串流架構演練。不包含任何交易功能，亦不鼓勵任何非法物品買賣。

## 核心技術棧
* **資料獲取:** Python (Scrapy, Telethon, Selenium stealth)
* **訊息串流:** Apache Kafka, Kafka Connect
* **資料處理:** Kafka Streams / Faust (Python)
* **儲存與搜尋:** Elasticsearch + Kibana (ELK Stack)