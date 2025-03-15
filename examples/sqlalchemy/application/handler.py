from typing import Annotated as A

from selva.di import Inject
from selva.web import Request, get

from .service import DefaultDBService, OtherDBService


@get
async def index(request: Request, db_service: A[DefaultDBService, Inject]):
    db_version = await db_service.db_version()
    model = await db_service.get_model()
    dto = {"id": model.id, "name": model.name}
    await request.respond({"db_version": db_version, "model": dto})


@get("other")
async def other(request: Request, db_service: A[OtherDBService, Inject]):
    db_version = await db_service.db_version()
    model = await db_service.get_model()
    dto = {"id": model.id, "name": model.name}
    await request.respond({"db_version": db_version, "model": dto})
