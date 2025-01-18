# Serviços em plano de fundo

Há casos onde você precisa executar código em paralelo a sua aplicação, por exemplo,
escutar por mensagens em uma fila.

Selva provê o decorador `selva.web.background` para funções como serviços em plano
de fundo que será iniciados como tarefas assíncronas em paralelo à aplicação principal.

```python
from selva.web import background


@background
async def background_service():
    ...
```

As funções de plano de fundo podem receber serviços como parâmetros do sistema de
injeção de depdenências.

Por exemplo, você pode criar um serviço que escuta por noticiações do Redis: 

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