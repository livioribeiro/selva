# Logging

Selva usa [Structlog](https://www.structlog.org) para logging e provê algumas facilidades
para tornar seu uso mais próximo de outros frameworks como Spring Boot.

Ele é integrado com o logging da biblioteca padrão, então bibliotecas que a usam
realizarão logging com Structlog. Ele também permite filtrar pelo nome do logger
usando a biblioteca padrão.

## Porque?

Atualmente, é muito provável que sua aplicação seja implantada em uma nuvem e os
logs enviados para um agregador como Greylog, então um formato de logging estruturado
parece ser a escolha mais lógica.

Para mais informações sobre o porquê de usar logging estruturado, veja
[Structlog documentation](https://www.structlog.org/en/stable/why.html).

## Configure o logging

O logging é configurado através da configuração do Selva:

```yaml
logging:
  root: WARNING # (1)
  level: # (2)
    application: INFO
    selva: DEBUG
  format: json # (3) 
  setup: selva.logging.setup # (4)
```

1.  Nível de log do logger raiz.
2.  Mapa de nomes de loggers para o nível de log.
3.  Formato do log. Possíveis valores são `"json"`, `"logfmt"`, `"keyvalue"` e `"console"`.
4.  Setup function to configure logging.

A configuração `format` define quanl _renderer_ será utilizado. Os possível valores
apontam para o seguinte:

| value      | renderer                                                 |
|------------|----------------------------------------------------------|
| `json`     | `structlog.processors.JSONRenderer()`                    |
| `logfmt`   | `structlog.processors.LogfmtRenderer(bool_as_flag=True)` |
| `keyvalue` | `structlog.processors.KeyValueRenderer()`                |
| `console`  | `structlog.dev.ConsoleRenderer()`                        |

Se não definido, `format` terá o valor de `"json"` se `sys.stderr.isatty() == False`,
caso contrário terá o valor `"console"`. Isto é feito para utilizar `ConsoleRenderer`
em desenvolvimento e `JSONRenderer` quando implantado em produção

## Definição manual do logger

Se você precisar de controle total de como o Structlog é configurado, você pode
fornecer uma função de definição de logger. Você precisa apenas referenciá-la no
arquivo de configuração:

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

A função de definição recebe um parâmetro do tipo `selva.configuration.Settings`,
então você terá acesso a todas as configurações.
