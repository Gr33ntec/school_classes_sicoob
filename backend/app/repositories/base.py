from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session


class Repository:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    @property
    def columns(self) -> set[str]:
        return set(self.model.__table__.columns.keys())

    def list(self, page: int, page_size: int, sort: str, order: str, filters: dict):
        stmt = select(self.model)
        for column, value in filters.items():
            stmt = stmt.where(getattr(self.model, column) == value)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        direction = desc if order == "desc" else asc
        stmt = (
            stmt.order_by(direction(getattr(self.model, sort)), self.model.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt)), total

    def get(self, obj_id: int):
        return self.db.get(self.model, obj_id)

    def add(self, obj) -> None:
        self.db.add(obj)

    def delete(self, obj) -> None:
        self.db.delete(obj)
