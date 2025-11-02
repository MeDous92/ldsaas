-- allow invited users to exist without a password until they accept
ALTER TABLE users
  ALTER COLUMN password_hash DROP NOT NULL;
