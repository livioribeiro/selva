# Logging

Selva uses [Structlog](https://www.structlog.org) for logging and provides
some facilities on top of it to make its usage a bit closer to other frameworks
like Spring Boot.

It is integrated with the standard library logging, so libraries that use it are logged
through Structlog. It also enables filtering by logger name using the standard library.

## Why?

Nowadays, it is very likely that your application is deployed to a cloud and its
logs are sent to an aggregator like Graylog, so a structured logging format seems
to be the logical choice.

For more information on why use structured logging, refer to the
[Structlog documentation](https://www.structlog.org/en/stable/why.html).

## Configure logging

Logging is configured in the Selva configuration:

```yaml
logging:
  root: WARNING # (1)
  level: # (2)
    application: INFO
    selva: DEBUG
  format: json # (3) 
  setup: selva.logging.setup # (4)
```

1.  Log level of the root logger.
2.  Mapping of logger names to log level.
3.  Log format. Possible values are `"json"`, `"logfmt"`, `"keyvalue"` and `"console"`.
4.  Setup function to configure logging.

The `format` config defines which renderer will be used. The possible values map to:

| value      | renderer                                                 |
|------------|----------------------------------------------------------|
| `json`     | `structlog.processors.JSONRenderer()`                    |
| `logfmt`   | `structlog.processors.LogfmtRenderer(bool_as_flag=True)` |
| `keyvalue` | `structlog.processors.KeyValueRenderer()`                |
| `console`  | `structlog.dev.ConsoleRenderer()`                        |

If not defined, `format` defaults to `"json"` if `sys.stderr.isatty() == False`,
or `"console"` otherwise. This is done to use the `ConsoleRenderer` during development
and the `JSONRenderer` when deploying to production.

## Manual logger setup

If you need full control of how Structlog is configured, you can provide a logger setup
function. You just need to reference it in the configuration file:

=== "configuration/settings.yaml"

    ```yaml
    logging:
      setup: application.logging.setup
    ```

=== "application/logging.py"

    ```python
    import structlog
    from selva.configuration import Settings
    
    
    def setup(settings: Settings):
        structlog.configure(...)
    ```

The setup function receives a parameter of type `selva.configuration.Settings`,
so you can have access to the whole settings.
