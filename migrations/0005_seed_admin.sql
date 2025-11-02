INSERT INTO users (email, name, password_hash, role, is_active)
VALUES (
  'admin@email.com',
  'System Admin',
  '$2b$12$YhSvX3Wg1F6cRkDwoSC9Me8hZmAAg4RRl3vBPOgMHD/oG.G0M58M2',  -- hash of "Admin123!"
  'admin',
  true
);
