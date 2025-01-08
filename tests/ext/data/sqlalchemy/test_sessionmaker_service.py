import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.data.sqlalchemy.service import sessionmaker_service


class BaseA(DeclarativeBase):
    pass


class ModelA(BaseA):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class BaseB(DeclarativeBase):
    pass


class ModelB(BaseB):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


async def test_session_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                    "session": {
                        "options": {
                            "info": {"framework": "selva"},
                        },
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.data.sqlalchemy.connections.default.url)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        assert session.info == {"framework": "selva"}


session_info = {
    "framework": "selva",
}


async def test_session_options_info_dotted_path():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                    "session": {
                        "options": {
                            "info": f"{test_session_options_info_dotted_path.__module__}.session_info",
                        },
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.data.sqlalchemy.connections.default.url)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        assert session.info == {"framework": "selva"}


class MySession(AsyncSession):
    pass


async def test_session_class():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                    "session": {
                        "options": {
                            "class": f"{MySession.__module__}:{MySession.__name__}",
                        },
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.data.sqlalchemy.connections.default.url)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        assert session.__class__ == MySession


async def test_binds():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "conn_a": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                        "conn_b": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                    "session": {
                        "binds": {
                            f"{BaseA.__module__}:{BaseA.__qualname__}": "conn_a",
                            f"{BaseB.__module__}:{BaseB.__qualname__}": "conn_b",
                        },
                    },
                },
            },
        }
    )

    engine_a = create_async_engine(settings.data.sqlalchemy.connections.conn_a.url)
    engine_b = create_async_engine(settings.data.sqlalchemy.connections.conn_b.url)

    sessionmaker = await sessionmaker_service(
        settings, {"conn_a": engine_a, "conn_b": engine_b}
    )
    async with sessionmaker() as session:
        assert session.binds[BaseA] == engine_a
        assert session.binds[BaseB] == engine_b


async def test_sessiomaker_without_default_connection():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "conn": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.data.sqlalchemy.connections.conn.url)

    sessionmaker = await sessionmaker_service(settings, {"conn": engine})
    async with sessionmaker() as session:
        assert session.bind is engine


async def test_binds_model():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "conn_a": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                        "conn_b": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                    "session": {
                        "binds": {
                            f"{BaseA.__module__}:{BaseA.__qualname__}": "conn_a",
                            f"{BaseB.__module__}:{BaseB.__qualname__}": "conn_b",
                        },
                    },
                },
            },
        }
    )

    engine_a = create_async_engine(settings.data.sqlalchemy.connections.conn_a.url)
    async with engine_a.connect() as conn:
        await conn.run_sync(BaseA.metadata.create_all)

    engine_b = create_async_engine(settings.data.sqlalchemy.connections.conn_b.url)
    async with engine_b.connect() as conn:
        await conn.run_sync(BaseB.metadata.create_all)

    sessionmaker = await sessionmaker_service(
        settings, {"conn_a": engine_a, "conn_b": engine_b}
    )
    async with sessionmaker() as session:
        session.add_all(
            [
                ModelA(id=1, name="A"),
                ModelB(id=1, name="B"),
            ]
        )
        await session.commit()

    async with sessionmaker() as session:
        name_a = await session.scalar(select(ModelA.name).where(ModelA.id == 1))
        name_b = await session.scalar(select(ModelB.name).where(ModelB.id == 1))

        assert name_a == "A"
        assert name_b == "B"


async def test_binds_with_invalid_connection_should_fail():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "connections": {
                        "default": {
                            "url": "sqlite+aiosqlite:///:memory:",
                        },
                    },
                    "session": {
                        "binds": {
                            f"{BaseA.__module__}:{BaseA.__qualname__}": "invalid",
                        },
                    },
                },
            },
        }
    )

    with pytest.raises(ValueError, match="No engine with name 'invalid'"):
        await sessionmaker_service(settings, {"default": None})
