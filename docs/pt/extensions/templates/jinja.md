# Jinja

Esta estensão provê suport para templates Jinja.

## Utilização

Para utilizar templates Jinja, primeiro instale o extra `jinja`:

```shell
pip install selva[jinja]
```

Depois ative a extensão no arquivo de configurações:

```yaml
extensions:
  - selva.ext.templates.jinja
```

Para renderizar templates, injet o a dependência `selva.ext.templates.jinja.JinjaTemplate`
e chame o método `respond`:

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

## Renderizar templates para string

A classe `JinjaTemplate` provê métodos para renderizar templates para `str`, ao
invés de renderizar para a resposta.

O método `JinjaTempate.render` aceita um nome de template e retorna uma string com
o template renderizado.

O método `JinjaTempate.render_str` aceita um template como string, o compila e retorna
o resultado.

```python
rendered = template.render("template.html", {"variable": "value"})
rendered = template.render_str("{{ variable }}", {"variable": "value"})
```

## Configuração

Jinja pode ser configurado através do `settings.yaml`. Por exemplo, para ativar
extensões do Jinja:

```yaml
templates:
  jinja:
    extensions:
      - jinja2.ext.i18n
      - jinja2.ext.debug
```

Lista completa de configurações:

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
    # caminho para uma classe python
    undefined: "package.module.Class"
    # caminho para uma função python
    finalize: "package.module.function"
    # caminho para uma função python
    autoescape: "package.module.function"
    # caminho para uma variável python
    loader: "package.module:variable"
    cache_size: 1
    auto_reload: true
    # caminho para uma variável python
    bytecode_cache: "package.module:variable"
```