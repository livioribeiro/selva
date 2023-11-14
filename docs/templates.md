Selva offers support for Jinja templates.

To use templates, first install the `jinja` extra:

```shell
pip install selva[jinja]
```

Template files are located in the `resources/templates directory`:

```
project/
├── application/
│   └── ...
└── resources/
    └── templates/
        ├── index.html
        └── ...
```

To render templates, inject the `selva.web.templates.Template` dependency and call its `respond` method:

=== "application.py"

    ```python
    from typing import Annotated
    from selva.di import Inject
    from selva.web import controller, get
    from selva.web.templates import Template
    
    
    @controller
    class Controller:
        template: Annotated[Template, Inject]
    
        @get
        async def index(self, request):
            context = {"title": "Index"}
            await self.template.respond(request.response, "index.html", context)
    ```

=== "resources/templates/index.html"

    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Jinja Templates</title>
    </head>
    <body>
        <h1>{{ title }}</h1>
    </body>
    </html>
    ```

## Configuration

Jinja can be configured through the `settings.yaml`. For exmaple, to activate extensions:

```yaml
templates:
  jinja:
    extensions:
      - jinja2.ext.i18n
      - jinja2.ext.debug
```