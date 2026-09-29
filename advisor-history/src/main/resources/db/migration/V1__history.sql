CREATE TABLE history (
 id BIGSERIAL PRIMARY KEY, request_id UUID NOT NULL, owner VARCHAR(64) NOT NULL,
 kind VARCHAR(20) NOT NULL CHECK (kind IN ('financial','investment')),
 question VARCHAR(2000) NOT NULL, answer TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(owner,request_id));
CREATE INDEX history_owner_created ON history(owner,created_at DESC,id DESC);
