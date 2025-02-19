# Configuração

Configurações em Selva são definidas através de arquivos YAML. Internamente é utilizado
a biblioteca [ruamel.yaml](https://yaml.readthedocs.io), então YAML 1.2 é suportado.

Arquivos de configuração são localizados por padrão no diretório `configuration`
com o nome base de `settings.yaml`:

```
project/
├── application/
│   └── ...
└── configuration/
    ├── settings.yaml
    ├── settings_dev.yaml
    └── settings_prod.yaml
```

## Acessando as configurações

Os valores de configuração pode ser acessados ao injetar `selva.configuration.Settings`.

```python
from typing import Annotated
from selva.conf import Settings
from selva.di import Inject, service


@service
class MyService:
    settings: Annotated[Settings, Inject]
```

O objeto `Settings` funciona como um `dict` que pode ser acessado com a sintaxe
de acesso à propriedades:

```python
from selva.conf import Settings

settings = Settings({"config": "value"})
assert settings["config"] == "value"
assert settings.config == "value"
```

### Configurações tipadas

Configurações carregadas de arquivos YAML são todos `dict`. Entretando, nós podemos
utilizar o `pydantic` e o sistema de injeção de dependências para prover acesso
às configurações de uma forma mais tipada.

=== "application.py"

    ```python
    from pydantic import BaseModel
    from selva.configuration import Settings
    from selva.di import service
    
    
    class MySettings(BaseModel):
        int_property: int
        bool_property: bool
    
    
    @service
    def my_settings(settings: Settings) -> MySettings:
        return MySettings.model_validate(settings.my_settings)
    ```

=== "configuration/settings.yaml"

    ```yaml
    my_settings:
      int_property: 1
      bool_property: true
    ```

## Substituição de ambiente

Os arquivos de configurações podem incluir referências a variáveis de ambiente no
formato `${ENV_VAR:default_value}`. O valor padrão é opcional e um erro será lançado
se ambos variável de ambiente e valor padrão não forem definidos.

```yaml
required: ${ENV_VAR}         # variável de ambiente requerida
optional: ${OPT_VAR:default} # variável de ambiente opcional
```

## Perfis

Perfis opcionais podem ser ativados ao definir a variável de ambiente `SELVA_PROFILE`.
O framework procurará por um arquivos chamado `settings_${SELVA_PROFILE}.yaml` e
combinará os valores com aqueles do `settings.yaml`. Valores do perfil tem precedência
sobre os valores da configuração principal.

Por exemplo, se nós definirmos `SELVA_PROFILE=dev`, o arquivos `settings_dev.yaml`
será carregado. Mas se ao invés nós definirmos `SELVA_PROFILE=prod`, então o arquivo
`settings_prod.yaml` será carregado.

Múltiplos perfis podem ser ativados ao definir `SELVA_PROFILE` com uma lista separada
por vírgula de pergis, por exemplo `SELVA_PROFILE=dev,prod`. O framework vai iterar
pela lista de combinar as configurações encontradas em cada um. A precedêcia é do
último para o primeiro, então as configurações do primeiro perfil sobrescrevem as
do perfil anterior.

## Variáveis de ambiente

Configurações também podem ser definidas em variáveis de ambiente cujos nomes começam
com `SELVA__`, onde subsequentes _underscores_ duplos (`__`) indicam aninhamento
(a variável é um mapeamento). Além disso, nomes de variáveis serão transformados em
letras minúsculas.

Por exemplo, considere as seguintes variáveis de ambiente:

```dotenv
SELVA__PROPERTY=1
SELVA__MAPPING__PROPERTY=2
SELVA__MAPPING__ANOTHER_PROPERTY=3
```

Essas variáveis serão coletadas da seguinte forma:

```python
{
    "property": "1",
    "mapping": {
        "property": "2",
        "another_property": "3",
    },
}
```

### DotEnv

Se estiver executando seu projeto usando `selva.run:app`, por exemplo, `uvicorn selva.run:app`,
variáveis de ambiente seráo carregadas do arquivo `.env`. O _parsing_ é realizado
com a biblioteca [python-dotenv](https://pypi.org/project/python-dotenv/).

Por padrão, o arquivos`.env` no diretório atual será carregado, mas ele pode ser
customizado com a variável de ambiente `SELVA_DOTENV` apontando para o arquivo `.env`.
