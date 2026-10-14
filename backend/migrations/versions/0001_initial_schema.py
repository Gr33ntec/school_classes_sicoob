"""initial schema

Revision ID: 0001
Revises:
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TABLES = [
    """
CREATE TABLE students (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  registration_code VARCHAR(30) NOT NULL,
  full_name VARCHAR(160) NOT NULL,
  email VARCHAR(254) NULL,
  phone VARCHAR(30) NULL,
  birth_date DATE NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_students_registration_code (registration_code),
  UNIQUE KEY uk_students_email (email),
  CONSTRAINT chk_students_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
    """
CREATE TABLE teachers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_code VARCHAR(30) NOT NULL,
  full_name VARCHAR(160) NOT NULL,
  email VARCHAR(254) NULL,
  phone VARCHAR(30) NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_teachers_employee_code (employee_code),
  UNIQUE KEY uk_teachers_email (email),
  CONSTRAINT chk_teachers_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
    """
CREATE TABLE courses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  course_code VARCHAR(30) NOT NULL,
  name VARCHAR(160) NOT NULL,
  description TEXT NULL,
  workload_hours SMALLINT UNSIGNED NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_courses_course_code (course_code),
  CONSTRAINT chk_courses_workload CHECK (workload_hours > 0),
  CONSTRAINT chk_courses_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
    """
CREATE TABLE school_classes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  class_code VARCHAR(30) NOT NULL,
  course_id BIGINT UNSIGNED NOT NULL,
  teacher_id BIGINT UNSIGNED NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  max_students SMALLINT UNSIGNED NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'planned',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_school_classes_class_code (class_code),
  KEY idx_school_classes_course_id (course_id),
  KEY idx_school_classes_teacher_id (teacher_id),
  CONSTRAINT fk_school_classes_course
    FOREIGN KEY (course_id) REFERENCES courses (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_school_classes_teacher
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_school_classes_dates CHECK (end_date >= start_date),
  CONSTRAINT chk_school_classes_capacity CHECK (max_students > 0),
  CONSTRAINT chk_school_classes_status
    CHECK (status IN ('planned', 'active', 'completed', 'cancelled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
    """
CREATE TABLE enrollments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  student_id BIGINT UNSIGNED NOT NULL,
  class_id BIGINT UNSIGNED NOT NULL,
  enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(16) NOT NULL DEFAULT 'enrolled',
  final_grade DECIMAL(5,2) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_enrollments_student_class (student_id, class_id),
  KEY idx_enrollments_class_id (class_id),
  CONSTRAINT fk_enrollments_student
    FOREIGN KEY (student_id) REFERENCES students (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_enrollments_class
    FOREIGN KEY (class_id) REFERENCES school_classes (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_enrollments_status
    CHECK (status IN ('enrolled', 'completed', 'cancelled')),
  CONSTRAINT chk_enrollments_final_grade
    CHECK (final_grade IS NULL OR final_grade BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""",
]


def upgrade() -> None:
    for ddl in TABLES:
        op.execute(ddl)


def downgrade() -> None:
    for name in ("enrollments", "school_classes", "courses", "teachers", "students"):
        op.execute(f"DROP TABLE IF EXISTS {name}")
