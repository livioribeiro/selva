# Redis

This extension provides support for connecting to Redis servers. It registers the
`redis.asyncio.Redis` service.

## Usage

First install the `redis` extra:

```shell
pip install selva[redis]
```

Define the configuration properties:

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

    1.  Activate the sqlalchemy extension
    2.  "default" connection will be registered without a name
    3.  Connection registered with name "other"

Inject the `Redis` service:

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

Redis connections can also be defined with username and password separated from
the url, or even with individual components:

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

    1.  Username and password separated from the redis url
    2.  Each component defined individually

## Using environment variables

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
    
    1.  Can be define with just the environment variable `SELVA__DATA__REDIS__DEFAULT__URL`
    2.  Can be defined with just the environment variables:
        - `SELVA__DATA__REDIS__OTHER__URL`
        - `SELVA__DATA__REDIS__OTHER__USERNAME`
        - `SELVA__DATA__REDIS__OTHER__PASSWORD`
    3.  Can be defined with just the environment variables:
        - `SELVA__DATA__REDIS__ANOTHER__HOST`
        - `SELVA__DATA__REDIS__ANOTHER__PORT`
        - `SELVA__DATA__REDIS__ANOTHER__DB`
        - `SELVA__DATA__REDIS__ANOTHER__USERNAME`
        - `SELVA__DATA__REDIS__ANOTHER__PASSWORD`

## Example

=== "application/controller.py"

    ```python
    from redis.asyncio import Redis

    from asgikit.responses import respond_json

    from selva.di import Inject
    from selva.web import controller, get


    @controller
    class Controller:
        redis: Annotated[Redis, Inject]

        async def initialize():
            await self.redis.set("number", 0, nx=True)
    
        @get
        async def index(request):
            number = await self.redis.incr("number")
            await respond_json(request.response, {"number": number})
    ```

=== "configuration/settings.yaml"

    ```yaml
    data:
      redis:
        default:
          url: "redis://localhost:6379/0"
    ```

## Configuration options

Selva offers several options to configure Redis. If you need more control over
the SQLAlchemy services, you can create your own `redis.asyncio.Redis` outside
of the DI context.

The available options are shown below:

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
        socket_keepalive_options: {}
        unix_socket_path: ""
        encoding: ""
        encoding_errors: "strict" # or "ignore", "replace"
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
          supported_errors: []
          backoff: # (2)
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

1.  `options` values are described in [`redis.asyncio.Redis`](https://redis.readthedocs.io/en/stable/connections.html#async-client).
2.  Only one option in `backoff` should be filled.