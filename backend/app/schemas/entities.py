from datetime import date, datetime
from decimal import Decimal
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
ActiveStatus = Literal["active", "inactive"]
T = TypeVar("T")


class _In(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # Formularios enviam "" para campos vazios; sem isso e-mails vazios colidiriam na unicidade.
    @field_validator("*", mode="before")
    @classmethod
    def _blank_to_none(cls, value):
        return None if isinstance(value, str) and value == "" else value


class _Audit(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int


class StudentIn(_In):
    registration_code: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=1, max_length=160)
    email: str | None = Field(None, max_length=254, pattern=EMAIL_PATTERN)
    phone: str | None = Field(None, max_length=30)
    birth_date: date | None = None
    status: ActiveStatus = "active"


class StudentOut(_Audit, StudentIn):
    pass


class TeacherIn(_In):
    employee_code: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=1, max_length=160)
    email: str | None = Field(None, max_length=254, pattern=EMAIL_PATTERN)
    phone: str | None = Field(None, max_length=30)
    status: ActiveStatus = "active"


class TeacherOut(_Audit, TeacherIn):
    pass


class CourseIn(_In):
    course_code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    workload_hours: int = Field(gt=0, le=65535)
    status: ActiveStatus = "active"


class CourseOut(_Audit, CourseIn):
    pass


class ClassIn(_In):
    class_code: str = Field(min_length=1, max_length=30)
    course_id: int = Field(gt=0)
    teacher_id: int = Field(gt=0)
    start_date: date
    end_date: date
    max_students: int = Field(gt=0, le=65535)
    status: Literal["planned", "active", "completed", "cancelled"] = "planned"

    @model_validator(mode="after")
    def _check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date deve ser >= start_date")
        return self


class ClassOut(_Audit, ClassIn):
    pass


class EnrollmentIn(_In):
    student_id: int = Field(gt=0)
    class_id: int = Field(gt=0)
    status: Literal["enrolled", "completed", "cancelled"] = "enrolled"
    final_grade: Decimal | None = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)


class EnrollmentOut(_Audit, EnrollmentIn):
    enrolled_at: datetime
    final_grade: float | None = None
