/pharma-radar
├── /scrapers                 # 資料來源生產者 (Producers)
│   ├── /telegram_bot         # Telethon 監聽特定頻道
│   ├── /forum_spider         # Scrapy 爬蟲 (含代理IP池輪替)
│   └── /schema               # Avro/JSON schema 定義檔
├── /kafka_pipeline           # Kafka 核心設定
│   ├── docker-compose.yml    # Kafka, Zookeeper, ELK 容器設定
│   └── /connectors           # Source/Sink 設定檔
├── /stream_processors        # 資料清洗與聚合 (Consumers)
│   ├── /nlp_extractor        # 提取價格、單位、純度關鍵字
│   └── /price_aggregator     # 計算移動平均價格
├── /api_server               # 提供前端或 B2B 客戶的 API
└── /dashboard                # Kibana Dashboard 設定匯出檔