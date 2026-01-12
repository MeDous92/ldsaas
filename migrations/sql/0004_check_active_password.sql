migrations/0004_check_active_password.sql-- ensure active users always have a password
ALTER TABLE users
  ADD CONSTRAINT users_active_requires_password
  CHECK (is_active = false OR password_hash IS NOT NULL);
