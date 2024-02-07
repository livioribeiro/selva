# Templates

Selva offers support for rendering html responses from templates.

## Usage

First install the [Jinja extension](./extensions/jinja.md).

By default, template files are located in the `resources/templates directory`:

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

## Render templates to str

The `Template` interface provide methods to render templates into an str, instead
of rendering to the response.

The method `Tempate.render` accepts a template name and returns a string with the
rendered template.

The method `Template.render_str` accepts a template string, compiles it and returns
the result.

## Configuration

Selva offers configuration options for templates.

```yaml
templates:
  backend: "selva.ext.templates.jinja" # (1)
  paths: # (2)
    ["resources/templates"]
```

1.  If there are more extensions that provide templates, the backend property can
    be used to choose which one to use.
2.  Paths that will be used to look for templates.