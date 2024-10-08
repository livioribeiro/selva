# Extensions

Extensions are python packages that provide additional functionality or integrate
external libraries into the framework.

Current builtin extensions are:

- [SQLAlchemy](./sqlalchemy.md)
- [Jinja](./jinja.md)

## Activating extensions

Extensions need to be activated in `settings.yaml`, in the `extensions` property:

```yaml
extensions:
- selva.ext.data.sqlalchemy
- selva.ext.templates.jinja
```

## Creating extensions

An extension is a python package or module that contains a function named `selva_extension`
with arguments `selva.di.Container` and `selva.configuration.Settings`. It is called
during the startup phase of the application and may also be a coroutine.

```python
from selva.configuration import Settings
from selva.di import Container

# (1)
def selva_extension(container: Container, settings: Settings):
    pass
```

1.  `selva_extension` can also be `async`.

The function can then access values in the settings object, register new services,
retrieve the router service to register new routes, etc.
