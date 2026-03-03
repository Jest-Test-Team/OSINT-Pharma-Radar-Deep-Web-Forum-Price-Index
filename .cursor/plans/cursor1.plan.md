---
name: ""
overview: ""
todos: []
isProject: false
---

# Cursor 開發計畫：House Edge Sniper (Rust/Go/Next)

## Phase 1: Rust 極速基礎建設 (The Engine)

- [ ] 初始化 Rust 專案，設定 `ethers-rs` 連接本地端或私有 RPC (WebSocket)。

- [ ] 撰寫 `mempool_listener.rs` 捕獲特定 DEX Casino 合約的 Pending 交易。

- [ ] 整合 `rdkafka` (Rust Kafka client)，將原始交易資料打入 `mempool-raw` Topic。

## Phase 2: Go 串流處理與中樞 (The Brain)

- [ ] 初始化 Go 專案，建立 Kafka Consumer 群組訂閱 `mempool-raw`。

- [ ] 在 Go 中實作狀態機，緩存莊家資金池的當前水位 (可搭配 Redis)。

- [ ] 建立 WebSocket Server `ws_hub`) 準備推送過濾後的訊號。

## Phase 3: Next.js 實時面板 (The Face)

- [ ] 初始化 Next.js 14 (App Router) 專案。

- [ ] 建立 Dashboard 頁面，連線至 Go 的 WebSocket Server。

- [ ] 實作動態數據表格，高亮顯示當前 EV > 1 的「可狙擊」目標。

## Phase 4: 閉環自動化交易

- [ ] 在 Rust 中實作 `flashbots_relay.rs`。

- [ ] 當 Go 判定風險通過並發送執行指令到 Kafka `execute-trade` Topic 時，Rust 攔截並簽名發送交易。