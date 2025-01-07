# Memcached

This extension provides support for connecting to Memcached servers. It registers the
`aiomcache.Client` service.

## Usage

First install the `memcached` extra:

```shell
pip install selva[redis]
```

Define the configuration properties:

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

    1.  Activate the extension
    2.  "default" connection will be registered without a name
    3.  Connection registered with name "other"

Inject the `aiomcache.Client` service:

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

## Using environment variables

=== "configuration/settings.yaml"

    ```yaml
    data:
      memcached:
        default:
          url: "${MEMCACHED_URL}" # (1)
    ```
    
    1.  Can be define with just the environment variable `SELVA__DATA__MEMCACHED__DEFAULT__URL`

## Example

=== "application/handler.py"

    ```python
    from typing import Annotated
    
    from aiomcache import Client as Memcached
    
    from asgikit.responses import respond_json
    
    from selva.di import Inject
    from selva.web import get
    
    @get
    async def index(request, redis: Annotated[Memcached, Inject]):
        if not await self.memcached.get(b"number"):
            await self.memcached.set(b"number", b"0")
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

## Configuration options

Selva offers several options to configure Redis. If you need more control over
the Memcached service, you can create your own `aiomcache.Client` service.

The available options are shown below:

```yaml
data:
  redis:
    default:
      address: ""
      options:
        pool_size: 10
        pool_minsize: 1
        get_flat_handler: "package.module.function" # dotted path to a python function
        set_flat_handler: "package.module.function" # dotted path to a python function
        conn_args: "package.module:variable" # dotted path to a python variable
```