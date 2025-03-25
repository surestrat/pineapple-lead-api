from typing import Generic, TypeVar, List, Optional, Protocol
from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class HasID(Protocol):
    id: int


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model_class: type[ModelType]):
        self.session = session
        self.model = model_class
        assert hasattr(
            model_class, "id"
        ), f"Model {model_class.__name__} must have an 'id' attribute"

    def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, id: int) -> Optional[ModelType]:
        statement = select(self.model).where(getattr(self.model, "id") == id)
        return self.session.exec(statement).one_or_none()

    def get_all(self) -> List[ModelType]:
        statement = select(self.model)
        return list(self.session.exec(statement).all())

    def update(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> None:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
