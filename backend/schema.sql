-- Sorin Library staging schema (SQLite). No production data or migrations.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY, handle TEXT NOT NULL UNIQUE COLLATE NOCASE,
 email TEXT NOT NULL UNIQUE COLLATE NOCASE, salt TEXT NOT NULL,
 password_hash TEXT NOT NULL,
 role TEXT NOT NULL DEFAULT 'member' CHECK(role IN ('member','admin')),
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY,
 user_id TEXT NOT NULL REFERENCES users(id),
 expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS resources (
 id TEXT PRIMARY KEY,
 owner_id TEXT NOT NULL REFERENCES users(id),
 kind TEXT NOT NULL CHECK(kind IN ('emoji','sticker','sound','graphics')),
 title TEXT NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL,
 media_type TEXT NOT NULL, stored_name TEXT NOT NULL, file_hash TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
 created_at INTEGER NOT NULL, reviewed_at INTEGER,
 reviewer_id TEXT REFERENCES users(id), rejection_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_resources_status_kind ON resources(status,kind,created_at);
CREATE INDEX IF NOT EXISTS idx_resources_owner ON resources(owner_id,status);
CREATE TABLE IF NOT EXISTS ratings (
 user_id TEXT NOT NULL REFERENCES users(id),
 resource_id TEXT NOT NULL REFERENCES resources(id),
 score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
 created_at INTEGER NOT NULL,
 PRIMARY KEY(user_id,resource_id)
);
CREATE TABLE IF NOT EXISTS points (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL REFERENCES users(id),
 resource_id TEXT NOT NULL UNIQUE REFERENCES resources(id),
 amount INTEGER NOT NULL CHECK(amount > 0),
 created_at INTEGER NOT NULL
);
