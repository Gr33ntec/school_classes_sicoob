from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import Enrollment, SchoolClass
from app.repositories.base import Repository

# Codigos de erro do MySQL tratados como conflito de dominio.
_MYSQL_MESSAGES = {
    1062: "Registro duplicado.",
    1451: "Registro possui vinculos e nao pode ser excluido.",
    1452: "Referencia inexistente.",
}


def _conflict(exc: IntegrityError) -> ConflictError:
    args = getattr(exc.orig, "args", ())
    return ConflictError(_MYSQL_MESSAGES.get(args[0] if args else None, "Conflito de integridade."))


class CrudService:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model
        self.repo = Repository(db, model)

    def list(self, page, page_size, sort, order, filters):
        return self.repo.list(page, page_size, sort, order, filters)

    def get(self, obj_id: int):
        obj = self.repo.get(obj_id)
        if obj is None:
            raise NotFoundError("Registro nao encontrado.")
        return obj

    def create(self, data: dict):
        obj = self.model(**data)
        self.repo.add(obj)
        self._commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj_id: int, data: dict):
        obj = self.get(obj_id)
        for key, value in data.items():
            setattr(obj, key, value)
        self._commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> None:
        self.repo.delete(self.get(obj_id))
        self._commit()

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise _conflict(exc) from exc


class EnrollmentService(CrudService):
    def _ensure_capacity(self, class_id: int, exclude_id: int | None = None) -> None:
        # O lock na turma serializa matriculas concorrentes ate o commit.
        klass = self.db.scalar(
            select(SchoolClass).where(SchoolClass.id == class_id).with_for_update()
        )
        if klass is None:
            self.db.rollback()
            raise ConflictError("Turma inexistente.")
        stmt = (
            select(func.count())
            .select_from(Enrollment)
            .where(Enrollment.class_id == class_id, Enrollment.status != "cancelled")
        )
        if exclude_id is not None:
            stmt = stmt.where(Enrollment.id != exclude_id)
        if self.db.scalar(stmt) >= klass.max_students:
            self.db.rollback()
            raise ConflictError("Turma lotada.")

    def create(self, data: dict):
        if data["status"] != "cancelled":
            self._ensure_capacity(data["class_id"])
        return super().create(data)

    def update(self, obj_id: int, data: dict):
        current = self.get(obj_id)
        takes_seat = data["status"] != "cancelled"
        if takes_seat and (data["class_id"] != current.class_id or current.status == "cancelled"):
            self._ensure_capacity(data["class_id"], exclude_id=obj_id)
        return super().update(obj_id, data)
