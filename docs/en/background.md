# Background services

There are cases where you need to run code in parallel of your application, for
example, to listen to a messaging queue.

Selva provides the `selva.web.background` decorator to mark functions as background
services that will be started as async tasks and run alongside the main application.

```python
from selva.web import background


@background
async def background_service():
    ...
```

Background service functions can receive services as parameters from the dependency
injection system.

For example, you can create a function that listens for notification from Redis: 

```python
from redis.asyncio import Redis
from selva.web import background
import structlog

logger = structlog.get_logger()


@background
async def listen_channel(redis: Redis):
    async with redis.pubsub() as pubsub:
        await pubsub.psubscribe("chat")
        while True:
            if message := await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=None
            ):
                logger.info("chat", message=message["data"].decode())
```