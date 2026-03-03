---
name: ""
overview: ""
todos: []
isProject: false
---

# Cursor 開發計畫：House Edge Sniper

## Phase 1: 節點連線與高速生產者

- 設定本地或私有 RPC 節點連線 (WebSocket)。
- 監聽特定賭場的 Smart Contract 地址，過濾 `BetPlaced` 或 `RewardClaimed` 事件。
- 將 Mempool 中的 Pending Transactions 打入 Kafka `mempool-tx-stream` Topic。

## Phase 2: 期望值計算引擎

- 開發 Kafka Consumer 即時讀取串流。
- 串接 Redis 快取目前的莊家賠率與資金池餘額。
- 撰寫邏輯：當偵測到勝率期望值 > 1.05 時，觸發 Alert 到 `action-triggers` Topic。

## Phase 3: 自動化執行 (MEV)

- 訂閱 `action-triggers` Topic。
- 整合 Flashbots API，建構 Bundle Transaction 確保交易優先被礦工打包。
- 實作 Gas 費自動競價邏輯。

