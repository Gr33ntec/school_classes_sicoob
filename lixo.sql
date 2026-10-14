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
) ENGINE=InnoDB;
