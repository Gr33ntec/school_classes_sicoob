from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Course, Enrollment, SchoolClass, Student, Teacher
from app.schemas.entities import (
    ClassIn,
    ClassOut,
    CourseIn,
    CourseOut,
    EnrollmentIn,
    EnrollmentOut,
    Page,
    StudentIn,
    StudentOut,
    TeacherIn,
    TeacherOut,
)
from app.services.crud import CrudService, EnrollmentService

MAX_PAGE_SIZE = 100


def _crud_router(path, model, schema_in, schema_out, filters=(), service_cls=CrudService):
    router = APIRouter(prefix=f"/{path}", tags=[path])

    def service(db: Session = Depends(get_db)):
        return service_cls(db, model)

    @router.get("", response_model=Page[schema_out])
    def list_items(
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=MAX_PAGE_SIZE),
        sort: str = "id",
        order: str = Query("asc", pattern="^(asc|desc)$"),
        svc=Depends(service),
    ):
        if sort not in svc.repo.columns:
            raise HTTPException(422, "Campo de ordenacao invalido.")
        active = {k: request.query_params[k] for k in filters if k in request.query_params}
        items, total = svc.list(page, page_size, sort, order, active)
        return {"items": items, "total": total}

    @router.get("/{obj_id}", response_model=schema_out)
    def get_item(obj_id: int, svc=Depends(service)):
        return svc.get(obj_id)

    @router.post("", response_model=schema_out, status_code=201)
    def create_item(body: schema_in, svc=Depends(service)):
        return svc.create(body.model_dump())

    @router.put("/{obj_id}", response_model=schema_out)
    def update_item(obj_id: int, body: schema_in, svc=Depends(service)):
        return svc.update(obj_id, body.model_dump())

    @router.delete("/{obj_id}", status_code=204)
    def delete_item(obj_id: int, svc=Depends(service)):
        svc.delete(obj_id)
        return Response(status_code=204)

    return router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(_crud_router("students", Student, StudentIn, StudentOut, ("status",)))
api_router.include_router(_crud_router("teachers", Teacher, TeacherIn, TeacherOut, ("status",)))
api_router.include_router(_crud_router("courses", Course, CourseIn, CourseOut, ("status",)))
api_router.include_router(
    _crud_router(
        "classes", SchoolClass, ClassIn, ClassOut, ("status", "course_id", "teacher_id")
    )
)
api_router.include_router(
    _crud_router(
        "enrollments",
        Enrollment,
        EnrollmentIn,
        EnrollmentOut,
        ("status", "student_id", "class_id"),
        EnrollmentService,
    )
)
