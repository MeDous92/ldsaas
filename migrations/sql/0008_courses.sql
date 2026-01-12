CREATE TABLE IF NOT EXISTS courses (
  id         BIGSERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  provider   TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS courses_name_provider_key
  ON courses (name, provider);

INSERT INTO courses (name, provider)
VALUES ('Intro to L&D', 'Internal')
ON CONFLICT (name, provider) DO NOTHING;
