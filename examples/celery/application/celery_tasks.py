import asyncio

from celery import Celery

from selva.conf.settings import get_settings
from selva.di import Container

from .service import Greeter

app = Celery("hello", broker="redis://localhost:6379/2")


_di_container = None


def di_container() -> Container:
    global _di_container
    if _di_container is None:
        settings = get_settings()
        _di_container = Container()
        _di_container.scan(settings.application)
    return _di_container


@app.task
def hello(name: str):
    di = di_container()
    greeter = asyncio.run(di.get(Greeter))
    result = greeter.greet(f"{name}, from celery")
    return result
