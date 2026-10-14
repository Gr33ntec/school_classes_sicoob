from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

UBigInt = BigInteger().with_variant(BIGINT(unsigned=True), "mysql")
USmallInt = SmallInteger().with_variant(SMALLINT(unsigned=True), "mysql")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Student(TimestampMixin, Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name="chk_students_status"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    registration_code: Mapped[str] = mapped_column(String(30), unique=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(254), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    birth_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), server_default="active")


class Teacher(TimestampMixin, Base):
    __tablename__ = "teachers"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name="chk_teachers_status"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    employee_code: Mapped[str] = mapped_column(String(30), unique=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(254), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(16), server_default="active")


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("workload_hours > 0", name="chk_courses_workload"),
        CheckConstraint("status IN ('active', 'inactive')", name="chk_courses_status"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    course_code: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    workload_hours: Mapped[int] = mapped_column(USmallInt)
    status: Mapped[str] = mapped_column(String(16), server_default="active")


class SchoolClass(TimestampMixin, Base):
    __tablename__ = "school_classes"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_school_classes_dates"),
        CheckConstraint("max_students > 0", name="chk_school_classes_capacity"),
        CheckConstraint(
            "status IN ('planned', 'active', 'completed', 'cancelled')",
            name="chk_school_classes_status",
        ),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    class_code: Mapped[str] = mapped_column(String(30), unique=True)
    course_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("courses.id", onupdate="RESTRICT", ondelete="RESTRICT"), index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("teachers.id", onupdate="RESTRICT", ondelete="RESTRICT"), index=True
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    max_students: Mapped[int] = mapped_column(USmallInt)
    status: Mapped[str] = mapped_column(String(16), server_default="planned")


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "class_id", name="uk_enrollments_student_class"),
        CheckConstraint(
            "status IN ('enrolled', 'completed', 'cancelled')",
            name="chk_enrollments_status",
        ),
        CheckConstraint(
            "final_grade IS NULL OR final_grade BETWEEN 0 AND 100",
            name="chk_enrollments_final_grade",
        ),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("students.id", onupdate="RESTRICT", ondelete="RESTRICT")
    )
    class_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("school_classes.id", onupdate="RESTRICT", ondelete="RESTRICT"),
        index=True,
    )
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column(String(16), server_default="enrolled")
    final_grade: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
