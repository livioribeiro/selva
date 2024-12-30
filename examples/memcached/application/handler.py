from typing import Annotated as A

from asgikit.responses import respond_json

from selva.di import Inject
from selva.web import get

from .service import MemcachedService


@get
async def index(request, memcached_service: A[MemcachedService, Inject]):
    number = await memcached_service.get_incr()
    await respond_json(request.response, {"number": number})
