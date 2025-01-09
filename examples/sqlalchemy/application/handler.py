from typing import Annotated as A

from asgikit.responses import respond_json

from selva.di import Inject
from selva.web import get

from .service import DefaultDBService, OtherDBService


@get
async def index(request, db_service: A[DefaultDBService, Inject]):
    db_version = await db_service.db_version()
    model = await db_service.get_model()
    dto = {"id": model.id, "name": model.name}
    await respond_json(request.response, {"db_version": db_version, "model": dto})


@get("other")
async def other(request, db_service: A[OtherDBService, Inject]):
    db_version = await db_service.db_version()
    model = await db_service.get_model()
    dto = {"id": model.id, "name": model.name}
    await respond_json(request.response, {"db_version": db_version, "model": dto})
