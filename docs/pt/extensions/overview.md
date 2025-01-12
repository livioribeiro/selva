# Extensões

Extensions are python packages that provide additional functionality or integrate
external libraries into the framework.

Current builtin extensions are:

- Databases
    - [SQLAlchemy](data/sqlalchemy.md)
    - [Redis](data/redis.md)
    - [Memcached](data/memcached.md)
- Template engines
    - [Jinja](templates/jinja.md)
    - [Mako](templates/mako.md)

## Activating extensions

Extensions need to be activated in `settings.yaml`, in the `extensions` property:

```yaml
extensions:
- selva.ext.data.sqlalchemy
- selva.ext.templates.jinja
```

## Creating extensions

An extension is a python package or module that contains a function named `init_extension`
with arguments `selva.di.Container` and `selva.configuration.Settings`. It is called
during the startup phase of the application and may also be a coroutine.

```python
from selva.configuration import Settings
from selva.di import Container

async def init_extension(container: Container, settings: Settings):
    pass

# # init_extension can also be sync
# def init_extension(container: Container, settings: Settings): ...
```

The function can then access values in the settings object, register new services,
retrieve the router service to register new routes, etc.
