import asyncio
from functools import cache

from celery import Celery

from selva.conf.settings import get_settings
from selva.di import Container

from .service import Greeter

app = Celery("hello", broker="redis://localhost:6379/2")


@cache
def di_container() -> Container:
    settings = get_settings()
    container = Container()
    container.scan(settings.application)
    return container


@app.task
def hello(name: str):
    di = di_container()
    greeter = asyncio.run(di.get(Greeter))
    result = greeter.greet(f"{name}, from celery")
    return result
