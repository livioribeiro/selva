# Memcached

Essa extensão provê suporte para conectar a servidores Memcached. Ela registra o
serviço `aiomcache.Client`.

## Utilização

Primeiro instale o extra `memcached`:

```shell
pip install selva[memcached]
```

Defina as propriedade de configuração:

=== "configuration/settings.yaml"

    ```yaml
    extensions:
      - selva.ext.data.memcached # (1)
    
    data:
      memcached:
        default: # (2)
          address: "localhost:11211"
        other: # (3)
          address: "localhost:11212"
    ```

    1.  Ativar a extensão
    2.  A conexão "default" será registrada sem um nome
    3.  Conexão registrada com nome "other"

Injete o serviço `aiomcache.Client`:

```python
from typing import Annotated
from aiomcache import Client as Memcached
from selva.di import service, Inject


@service
class MyService:
    # default service
    memcached: Annotated[Memcached, Inject]

    # named service
    other_memcached: Annotated[Memcached, Inject(name="other")]
```

## Utilizando variáveis de ambiente

=== "configuration/settings.yaml"

    ```yaml
    data:
      memcached:
        default:
          address: "${MEMCACHED_ADDR}" # (1)
    ```
    
    1.  Pode ser definido com a variável de ambiente `SELVA__DATA__MEMCACHED__DEFAULT__ADDRESS`

## Examplo

=== "application/handler.py"

    ```python
    from typing import Annotated
    
    from aiomcache import Client as Memcached
    
    from asgikit.responses import respond_json
    
    from selva.di import Inject
    from selva.web import get
    
    @get
    async def index(request, memcached: Annotated[Memcached, Inject]):
        if not await memcached.get(b"number"):
            await memcached.set(b"number", b"0")
        number = await memcached.incr("number")
        await respond_json(request.response, {"number": number})
    ```

=== "configuration/settings.yaml"

    ```yaml
    data:
      memcached:
        default:
          address: "localhost:11211"
    ```

## Opções de configuração

Selva oferece várias opções para configurar Memcached. Se você precisar de mais
controle sobre o serviço do Memcached, você pode criar o seu próprio serviço `aiomcache.Client`.

As opções disponíveis são exibidas abaixo:

```yaml
data:
  memcached:
    default:
      address: ""
      options:
        pool_size: 10
        pool_minsize: 1
        get_flat_handler: "package.module.function" # (1)
        set_flat_handler: "package.module.function" # (2)
        conn_args: "package.module:variable" # (3)
```

1.  caminho para uma função python
2.  caminho para uma função python
3.  caminho para uma variável python