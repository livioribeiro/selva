from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MyModel(Base):
    __tablename__ = 'my_model'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=100))

    def __repr__(self):
        return f"<MyModel(id={self.id}, name={self.name})>"


class OtherBase(DeclarativeBase):
    pass


class OtherModel(OtherBase):
    __tablename__ = 'my_model'
    id: Mapped[int] = Column(primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(length=100))

    def __repr__(self):
        return f"<OtherModel(id={self.id}, name={self.name})>"
