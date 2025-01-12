# Ciclo de vida

Selva provê decoradores para marcas funções como ganchos que serão chamadas quando
a aplicação iniciar. As funções serão chamadas na ordem em que foram descobertas
e, se alguma lançar um erro, a aplicação não será iniciada.

```python
from selva.web import startup


@startup
def my_startup_hook():
    ...
```

Funções de inicialização podem receber serviços como parâmetros através do sistema
de injeção de dependências.

```python
from selva.di import service
from selva.web import startup


@service
class OIDCService:
    async def oidc_discovey(self):
        ...


@startup
async def my_startup_hook(oidc_service: OIDCService):
    await oidc_service.oidc_discovey()
```

Você pode usar a anotação `Inject` se precisar de um serviço nomeado.

```python
from typing import Annotated

from selva.di import Inject, service
from selva.web import startup


@service(name="provider")
class OIDCService:
    async def oidc_discovey(self):
        ...


@startup
async def my_startup_hook(oidc_service: Annotated[OIDCService, Inject(name="provider")]):
    await oidc_service.oidc_discovey()
```