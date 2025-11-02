-- Seed a first admin (id auto, email case-insensitive via CITEXT)
INSERT INTO users (email, name, password_hash, role, is_active, email_verified_at)
VALUES ('admin@example.com', 'Admin', '$2b$12$rPwYVRUjU1oy5zbjhzmUfO9boXA6V7zocsEAx9Ue1.ZpivQg1L.0K', 'admin', true, now())
ON CONFLICT (email) DO UPDATE SET role='admin', is_active=true;
