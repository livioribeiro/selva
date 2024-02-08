from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class MyModel(Base):
    __tablename__ = 'my_model'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=100))

    def __repr__(self):
        return f"<MyModel(id={self.id}, name={self.name})>"
