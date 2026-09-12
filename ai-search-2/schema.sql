-- Run once against the D1 database before first deploy:
--   npx wrangler d1 execute ai-search-2-db --remote --file=./schema.sql

CREATE TABLE IF NOT EXISTS queries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  blocked INTEGER NOT NULL DEFAULT 0
);
