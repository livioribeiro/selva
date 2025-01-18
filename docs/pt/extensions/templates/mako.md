# Mako

Esta extensão provê suporte para templates Mako.

## Utilização

Para utilizar templates Mako, primeiro instale o extra `mako`:

```shell
pip install selva[mako]
```

Depois ative a extensão no arquivo de configuração:

```yaml
extensions:
  - selva.ext.templates.mako
```

Para renderizar templates, injete a dependência `selva.ext.templates.mako.MakoTemplate`
e chame o método `respond`:

=== "application.py"

    ```python
    from typing import Annotated
    from selva.di import Inject
    from selva.ext.templates.mako import MakoTemplate
    from selva.web import get
    
    @get
    async def index(request, template: Annotated[MakoTemplate, Inject]):
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
        <h1>${title}</h1>
    </body>
    </html>
    ```

## Renderizar templates para string

A classe `MakoTemplate` provê métodos para renderizar templates para `str`, ao invés
de renderizar para a resposta.

O método `MakoTempate.render` aceita um nome de template e retorna uma string com
o template renderizado.

```python
rendered = template.render("template.html", {"variable": "value"})
rendered = template.render_str("${variable}", {"variable": "value"})
```

## Configuração

Mako pode ser configurado através do `settings.yaml`. Por exemplo, para ativar a
opção "filesystem_checks":

```yaml
templates:
  mako:
    directories:
      - resources/mako
    filesystem_checks: true
```

Lista completa de configurações:

```yaml
templates:
  mako:
    directories:
      - resources/templates
    module_directory: ""
    filesystem_checks: false
    collection_size: 100
    format_exceptions: false
    # caminho para uma função python
    error_handler: "package.module.function"
    encoding_errors: "strict" # ou "ignore", "replace", "xmlcharrefreplace", "htmlentityreplace"
    cache_enabled: true
    cache_impl: "beaker"
    # caminho para uma variável python
    cache_args: "package.module:variable"
    # caminho para uma função python
    modulename_callable: "package.module.function"
    # caminho para uma função python
    module_writer: "package.module.function"
    default_filters: []
    buffer_filters: []
    strict_undefined: false
    imports: []
    future_imports: []
    enable_loop: true
    input_encoding: "utf-8"
    # caminho para uma função python
    preprocessor: "package.module.function"
    # caminho para uma classe python
    lexer_cls: "package.module.Class"
    # caminho para uma função python
    include_error_handler: "package.module.function"
```