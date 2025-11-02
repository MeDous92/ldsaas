-- 0002_invites.sql

-- extra fields for invite-first flow
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS invited_at         timestamptz,
  ADD COLUMN IF NOT EXISTS invited_by         bigint,
  ADD COLUMN IF NOT EXISTS invite_token_hash  text,
  ADD COLUMN IF NOT EXISTS invite_expires_at  timestamptz,
  ADD COLUMN IF NOT EXISTS email_verified_at  timestamptz;

-- optional: faster lookup by email (case-insensitive if you used citext)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_invite_expires_at ON users (invite_expires_at);
