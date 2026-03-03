-- Phase 3: 已知受版權保護影像 pHash 資料庫與外流紀錄
-- 執行：psql $DATABASE_URL -f 001_create_protected_hashes_and_leak_alerts.sql

-- 已知受保護影像的 pHash（可來自權利人上傳或既有指紋庫）
CREATE TABLE IF NOT EXISTS protected_image_hashes (
    id BIGSERIAL PRIMARY KEY,
    phash_hex VARCHAR(32) NOT NULL,
    source_identifier VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(phash_hex)
);

CREATE INDEX IF NOT EXISTS idx_protected_phash ON protected_image_hashes(phash_hex);

-- 外流網址與比對結果（相似度 > 90% 時寫入）
CREATE TABLE IF NOT EXISTS leak_alerts (
    id BIGSERIAL PRIMARY KEY,
    leaked_url TEXT NOT NULL,
    matched_phash_id BIGINT NOT NULL REFERENCES protected_image_hashes(id),
    similarity_pct NUMERIC(5,2) NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_phash_hex VARCHAR(32),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_leak_detected_at ON leak_alerts(detected_at);
CREATE INDEX IF NOT EXISTS idx_leak_matched_phash ON leak_alerts(matched_phash_id);

COMMENT ON TABLE protected_image_hashes IS 'Phase 3: 已知受版權保護影像之 pHash 指紋';
COMMENT ON TABLE leak_alerts IS 'Phase 3: 相似度 > 閾值時觸發之外流網址記錄';
