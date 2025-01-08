from collections.abc import Callable

from selva._util.maybe_async import maybe_async
from selva.di.container import Container
from selva.di.service.parse import get_dependencies


async def call_with_dependencies(di: Container, target: Callable):
    dependencies = {
        name: await di.get(dep.service, name=dep.name, optional=dep.optional)
        for name, dep in get_dependencies(target)
    }

    return await maybe_async(target, **dependencies)
