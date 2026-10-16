"""Testes de integracao das restricoes no schema de teste (isolado do real)."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

pytestmark = pytest.mark.integration


def _seed(c):
    c.execute(text("INSERT INTO courses (course_code,name,workload_hours) VALUES ('C1','Mat',40)"))
    c.execute(text("INSERT INTO teachers (employee_code,full_name) VALUES ('T1','Prof')"))
    c.execute(text("INSERT INTO students (registration_code,full_name) VALUES ('S1','Aluno')"))
    c.execute(
        text(
            "INSERT INTO school_classes (class_code,course_id,teacher_id,start_date,end_date,max_students) "
            "SELECT 'K1',c.id,t.id,'2026-01-01','2026-06-01',2 FROM courses c, teachers t"
        )
    )


def _enroll(c):
    c.execute(
        text(
            "INSERT INTO enrollments (student_id,class_id) "
            "SELECT s.id,k.id FROM students s, school_classes k"
        )
    )


def test_tables_exist(engine):
    with engine.connect() as c:
        names = {r[0] for r in c.execute(text("SHOW TABLES"))}
    assert {"students", "teachers", "courses", "school_classes", "enrollments"} <= names


def test_duplicate_enrollment(conn):
    _seed(conn)
    _enroll(conn)
    with pytest.raises(IntegrityError):
        _enroll(conn)


def test_invalid_dates(conn):
    _seed(conn)
    with pytest.raises(DBAPIError):  # CHECK violado vira OperationalError (3819)
        conn.execute(
            text(
                "INSERT INTO school_classes (class_code,course_id,teacher_id,start_date,end_date,max_students) "
                "SELECT 'K2',c.id,t.id,'2026-06-01','2026-01-01',5 FROM courses c, teachers t"
            )
        )


def test_missing_reference(conn):
    with pytest.raises(IntegrityError):
        conn.execute(text("INSERT INTO enrollments (student_id,class_id) VALUES (999999,999999)"))


def test_delete_related_blocked(conn):
    _seed(conn)
    _enroll(conn)
    with pytest.raises(IntegrityError):
        conn.execute(text("DELETE FROM students"))


def test_invalid_status(conn):
    _seed(conn)
    with pytest.raises(DBAPIError):
        conn.execute(text("UPDATE students SET status='x'"))


def test_invalid_final_grade(conn):
    _seed(conn)
    _enroll(conn)
    with pytest.raises(DBAPIError):
        conn.execute(text("UPDATE enrollments SET final_grade=101"))
