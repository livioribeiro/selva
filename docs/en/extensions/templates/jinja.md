# Jinja

This extension provides support for Jinja templates.

## Usage

To use jinja templates, first install the `jinja` extra:

```shell
pip install selva[jinja]
```

Then activate the extension in the configuration file:

```yaml
extensions:
  - selva.ext.templates.jinja
```

To render templates, inject the `selva.ext.templates.jinja.JinjaTemplate` dependency
and call its `respond` method:

=== "application.py"

    ```python
    from typing import Annotated
    from selva.di import Inject
    from selva.ext.templates.jinja import JinjaTemplate
    from selva.web import get
    
    @get
    async def index(request, template: Annotated[JinjaTemplate, Inject]):
        context = {"title": "Index"}
        await template.respond(request.response, "index.html", context)
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

## Render templates to string

The `JinjaTemplate` class provide methods to render templates into a `str`, instead
of rendering to the response.

The method `JinjaTempate.render` accepts a template name and returns a string with the
rendered template.

The method `JinjaTempate.render_str` accepts a template string, compiles it and returns
the result.

```python
rendered = template.render("template.html", {"variable": "value"})
rendered = template.render_str("{{ variable }}", {"variable": "value"})
```

## Configuration

Jinja can be configured through the `settings.yaml`. For example, to activate Jinja extensions:

```yaml
templates:
  jinja:
    extensions:
      - jinja2.ext.i18n
      - jinja2.ext.debug
```

Full list of settings:

```yaml
templates:
  jinja:
    paths:
      - resources/templates
    block_start_string: ""
    block_end_string: ""
    variable_start_string: ""
    variable_end_string: ""
    comment_start_string: ""
    comment_end_string: ""
    line_statement_prefix: ""
    line_comment_prefix: ""
    trim_blocks: true
    lstrip_blocks: true
    newline_sequence: "\n" # or "\r\n" or "\r"
    keep_trailing_newline: true
    extensions:
      - extension1
      - extensions2
    optimized: true
    # dotted path to python class
    undefined: "package.module.Class"
    # dotted path to python function
    finalize: "package.module.function"
    # dotted path to python function
    autoescape: "package.module.function"
    # dotted path to python variable
    loader: "package.module:variable"
    cache_size: 1
    auto_reload: true
    # dotted path to python variable
    bytecode_cache: "package.module:variable"
```