from typing import Annotated

from asgikit.responses import respond_json
from selva.di import Inject
from selva.web import controller, get

from .service import DefautDBService, OtherDBService


@controller
class Controller:
    default_db_service: Annotated[DefautDBService, Inject]
    other_db_service: Annotated[OtherDBService, Inject]

    @get
    async def index(self, request):
        db_version = await self.default_db_service.db_version()
        model = await self.default_db_service.get_model()
        dto = {
            "id": model.id,
            "name": model.name,
        }
        await respond_json(request.response, {"db_version": db_version, "model": dto})

    @get("other")
    async def other(self, request):
        db_version = await self.other_db_service.db_version()
        model = await self.other_db_service.get_model()
        dto = {
            "id": model.id,
            "name": model.name,
        }
        await respond_json(request.response, {"db_version": db_version,"model": dto})
