# Extensões

Extensões são pacotes python que provêem funcionalidade adicional ou integram bibliotecas
externas com o framework.

As extensões providas são:

- Bancos de dados
    - [SQLAlchemy](data/sqlalchemy.md)
    - [Redis](data/redis.md)
    - [Memcached](data/memcached.md)
- Templates
    - [Jinja](templates/jinja.md)
    - [Mako](templates/mako.md)

## Ativando extensões

Extensões precisam ser ativada no `settings.yaml`, na propriedade `extensions`:

```yaml
extensions:
- selva.ext.data.sqlalchemy
- selva.ext.templates.jinja
```

## Criando extensões

Uma extensão é um pacote ou módulo que contém uma função chamada `init_extension`
que recebe os argumentos `selva.di.Container` e `selva.configuration.Settings`.
Ela é chamada durante a inicialização da aplicação e pode ser uma função assíncrona.

```python
from selva.conf import Settings
from selva.di import Container


async def init_extension(container: Container, settings: Settings):
    pass

# # init_extension não precisa ser assíncrona
# def init_extension(container: Container, settings: Settings): ...
```

A função pode então acessar valores no objeto de configuração, registrar serviços,
recuperar o serviço roteador para registrar novas rotas, etc.
