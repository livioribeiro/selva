# Logging

Selva uses [Structlog](https://pypi.org/project/structlog/) for logging and provides
some facilities on top of it to make its usage a bit closer to other frameworks
like Spring Boot.

It is integrated with the standard library logging, so libraries that use it are logged
through Structlog. It also enables filtering by logger name using the standard library.

The default configuration uses the `structlog.dev.ConsoleRenderer` if the property
`debug` in the settings is `True`, otherwise it is set to `structlog.procesors.JSONRenderer`.
It is possible to configure `structlog.processors.LogfmtRenderer` through the settings.

## Configuring logging

Logging is configured in the Selva configuration:

```yaml
debug: false
logging:
  setup: selva.logging.setup # (1)
  format: null # (2) 
  root: WARNING # (3)
  level: # (4)
    application: INFO
    sqlalchemy: DEBUG
```

1.  Setup function to configure logging. It receices the application settings as parameter.
2.  Log format. Possible values are "json", "logfmt" and console". If not defined,
    defaults to "json" if "debug" is false, or "console" otherwise.
3.  Log level of the root logger.
4.  Mapping of logger names to log level.

## Manual logger setup

If you want full control of how Structlog is configured, you can provide a logger setup
function and reference it in the configuration file:

=== "application/logging.py"

    ```python
    import structlog
    from selva.configuration import Settings
    
    
    def setup(settings: Settings):
        structlog.configure(...)
    ```

=== "configuration/settings.yaml"

    ```yaml
    logging:
      setup: application.logging.setup
    ```

The setup function receives a parameter of type `selva.configuration.Settings`,
so you can have access to the whole settings.
