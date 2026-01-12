-- 0009_enrollments_notifications.sql
-- Manager assignments (employee -> manager)
CREATE TABLE IF NOT EXISTS employee_managers (
  employee_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  manager_id  BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Course enrollments with approval workflow
CREATE TABLE IF NOT EXISTS course_enrollments (
  id           BIGSERIAL PRIMARY KEY,
  employee_id  BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  course_id    BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  status       TEXT NOT NULL DEFAULT 'pending',
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at  TIMESTAMPTZ,
  approved_by  BIGINT REFERENCES users(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS course_enrollments_employee_course_key
  ON course_enrollments (employee_id, course_id);

CREATE INDEX IF NOT EXISTS idx_course_enrollments_employee_id
  ON course_enrollments (employee_id);

CREATE INDEX IF NOT EXISTS idx_course_enrollments_status
  ON course_enrollments (status);

ALTER TABLE course_enrollments
  ADD CONSTRAINT course_enrollments_status_check
  CHECK (status IN ('pending', 'approved', 'rejected'));

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title      TEXT NOT NULL,
  body       TEXT NOT NULL,
  type       TEXT NOT NULL,
  is_read    BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata   JSONB
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id
  ON notifications (user_id);

-- For now, set the admin as manager for all employees
INSERT INTO employee_managers (employee_id, manager_id)
SELECT u.id, a.id
FROM users u
CROSS JOIN LATERAL (
  SELECT id FROM users WHERE role = 'admin' ORDER BY id LIMIT 1
) a
WHERE u.role = 'employee'
ON CONFLICT (employee_id) DO UPDATE
SET manager_id = EXCLUDED.manager_id;
