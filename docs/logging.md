# Logging

Selva uses [loguru](https://pypi.org/project/loguru/) for logging, but provides
some facilities on top of it to make its usage a bit closer to other frameworks
like Spring Boot.

First, an interceptor to the standard `logging` module is configured by default,
as suggested in <https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging>.

Second, a custom logging filter is provided in order to set the logging level for
each package independently.

## Configuring logging

Logging is configured in the Selva configuration:

```yaml
logging:
  root: WARNING
  level:
    application: INFO
    application.service: TRACE
    sqlalchemy: DEBUG
  enable:
    - packages_to_activate_logging
  disabled:
    - packages_to_deactivate_logging
```

The `root` property is the *root* level. It is used if no other level is set for the
package where the log comes from.

The `level` property defines the logging level for each package independently.

The `enable` and `disable` properties lists the packages to enable or disable logging.
This comes from loguru, as can be seen in <https://github.com/Delgan/loguru#suitable-for-scripts-and-libraries>.

## Manual logger setup

If you want full control of how loguru is configured, you can provide a logger setup
function and reference it in the configuration file:

=== "application/logging.py"

    ```python
    from loguru import logger
    
    
    def setup(settings):
        logger.configure(...)
    ```

=== "configuration/settings.yaml"

    ```yaml
    logging:
      setup: application.logging.setup
    ```

The setup function receives a parameter of type `selva.configuration.Settings`,
so you can have access to the whole settings.
