# Redis

Esta extensão provê suporte para conectar a servidores Redis. Ela registra o serviço
`redis.asyncio.Redis`.

## Utilização

Primeiro instale o extra `redis`:

```shell
pip install selva[redis]
```

Defina as propriedades de configuração:

=== "configuration/settings.yaml"

    ```yaml
    extensions:
      - selva.ext.data.redis # (1)
    
    data:
      redis:
        default: # (2)
          url: redis://localhost:6379/0
        other: # (3)
          url: redis://localhost:6379/1
    ```

    1.  Ativar a extensão
    2.  A conexão "default" será registrada sem um nome
    3.  Conexão registrada com nome "other"

Injete o serviço `Redis`:

```python
from typing import Annotated
from redis.asyncio import Redis
from selva.di import service, Inject


@service
class MyService:
    # default service
    redis: Annotated[Redis, Inject]

    # named service
    other_redis: Annotated[Redis, Inject(name="other")]
```

Conexões Redis também podem ser definidas com nome de usuário e senha separados
da url, ou até como componentes individuais:

=== "configuration/settings.yaml"

    ```yaml
    data:
      redis:
        url_username_password: # (1)
          url: redis://localhost:6379/0
          username: user
          password: pass
    
        individual_components: # (2)
          host: localhost
          port: 6379
          db: 0
          username: user
          password: pass
    ```

    1.  Nome de usuário e senha separados da url
    2.  Cada componente definido individualmente

## Utilizando variáveis de ambiente

=== "configuration/settings.yaml"

    ```yaml
    data:
      redis:
        default:
          url: "${REDIS_URL}" # (1)

        other: # (2)
          url: "${REDIS_URL}"
          username: "${REDIS_USERNAME}"
          password: "${REDIS_PASSWORD}"
    
        another: # (3)
          host: "${REDIS_HOST}"
          port: ${REDIS_PORT}
          db: "${REDIS_DB}"
          username: "${REDIS_USERNAME}"
          password: "${REDIS_PASSWORD}"
    ```
    
    1.  Pode ser definido com a variável de ambiente `SELVA__DATA__REDIS__DEFAULT__URL`
    2.  Pode ser definido com as variáveis de ambiente:
        - `SELVA__DATA__REDIS__OTHER__URL`
        - `SELVA__DATA__REDIS__OTHER__USERNAME`
        - `SELVA__DATA__REDIS__OTHER__PASSWORD`
    3.  Pode ser definido com as variáveis de ambiente:
        - `SELVA__DATA__REDIS__ANOTHER__HOST`
        - `SELVA__DATA__REDIS__ANOTHER__PORT`
        - `SELVA__DATA__REDIS__ANOTHER__DB`
        - `SELVA__DATA__REDIS__ANOTHER__USERNAME`
        - `SELVA__DATA__REDIS__ANOTHER__PASSWORD`

## Exemplo

=== "application/handler.py"

    ```python
    from typing import Annotated
    
    from redis.asyncio import Redis
    
    from asgikit.responses import respond_json
    
    from selva.di import Inject
    from selva.web import get
    
    @get
    async def index(request, redis: Annotated[Redis, Inject]):
        number = await redis.incr("number")
        await respond_json(request.response, {"number": number})
    ```

=== "configuration/settings.yaml"

    ```yaml
    data:
      redis:
        default:
          url: "redis://localhost:6379/0"
    ```

## Opções de configuração

Selva ofecere várias opções para configura o Redis. Se você precisar de mais controle
sobre o serviço Redis, você pode criar o seu próprio serviço `redis.asyncio.Redis`.

As opções disponíveis são mostradas abaixo:

```yaml
data:
  redis:
    default:
      url: ""
      host: ""
      port: 6379
      db: 0
      username: ""
      password: ""
      options: # (1)
        socket_timeout: 1.0
        socket_connect_timeout: 1.0
        socket_keepalive: false
        socket_keepalive_options:
          TCP_KEEPIDLE: 100,
          TCP_KEEPCNT: 100,
          TCP_KEEPINTVL: 100,
        unix_socket_path: ""
        encoding: ""
        encoding_errors: "strict" # ou "ignore", "replace"
        decode_responses: false
        retry_on_timeout: false
        retry_on_error: []
        ssl: false
        ssl_keyfile: ""
        ssl_certfile: ""
        ssl_cert_reqs: ""
        ssl_ca_certs: ""
        ssl_ca_data: ""
        ssl_check_hostname: false
        max_connections: 1
        single_connection_client: false 
        health_check_interval: 1
        client_name: ""
        lib_name: ""
        lib_version: ""
        auto_close_connection_pool: false
        protocol: 3
        retry:
          retries: 1
          supported_errors: # (2)
            - package.module.Class
          backoff: # (3)
            no_backoff:
            constant:
              backoff: 1
            exponential:
              cap: 1
              base: 1
            full_jitter:
              cap: 1
              base: 1
            equal_jitter:
              cap: 1
              base: 1
            decorrelated_jitter:
              cap: 1
              base: 1
```

1.  Valores de `options` são descritos em [`redis.asyncio.Redis`](https://redis.readthedocs.io/en/stable/connections.html#async-client).
2.  Caminho para classes python.
3.  Apenas uma opção em `backoff` deve ser definida.