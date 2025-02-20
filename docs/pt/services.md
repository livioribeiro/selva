# Serviços

Serviços são tipos registrados no contêiner de injeção de dependências que podem
ser injetados em outros serviços e handlers. Eles são definidos com o decorador
`@service`.

```python
from typing import Annotated
from selva.di import Inject, service


@service
class MyService:
    pass


@service
class MyOtherService:
    dependency: Annotated[MyService, Inject]


class SomeClass:
    pass


class OtherClass:
    def __init__(self, dependency: SomeClass):
        self.dependency = dependency


@service
async def factory() -> SomeClass:
    return SomeClass()


@service
async def other_factory(dependency: SomeClass) -> OtherClass:
    return OtherClass(dependency)
```

## Serviços como classes

Serviços definidos como classes tem dependências como anotações da classe.

```python
from typing import Annotated
from selva.di import Inject, service


@service
class MyService:
    pass


@service
class OtherService:
    property: Annotated[MyService, Inject]
```

Quando um serviço de um tipo é requisitado no contêiner de injeção de dependências,
a classe será inspecionada pelas dependências anotadas que serão criadas e injetadas
no serviço requisitado.

Anotações sem `Inject` serão ignoradas.

### Inicializadores e finalizadores

Opcionalmente, classes de serviços podem definir dois métodos: `initialize()`, que
será chamado após a criação do serviço e injeção das dependências; e `finalize()`,
que será chamado na finalização da aplicação.

```python
from selva.di import service


@service
class MyService:
    async def initialize(self):
        """executa lógica de inicialização"""

    async def finalize(self):
        """executa lógica de finalização"""
```

Os métodos `initialize()` e `finalize()` não precisam ser `async`.

### Serviços que proveem uma interface

Você pode ter serviços que proveem uma interface ao invés do seu próprio tipo, de
forma que você requisita a interface como dependência ao invés do tipo concreto.

```python
from typing import Annotated

from selva.di import Inject, service


class Interface:
    def some_method(self): pass


@service(provides=Interface)
class MyService:
    def some_method(self): pass


@service
class OtherService:
    dependency: Annotated[Interface, Inject]
```

Quando `OtherService` for criado, o contêiner de injeção de dependências procurará
por um serviço do tipo `Interface` e produzirá uma instância da classe `MyService`.

### Serviços nomeados

Serviços podem ser registrados com um nome, de forma que você pode ter mais de um
serviço do mesmo tipo, desde que tenham nomes distintos. Sem um nome, o serviço
é registrado como o padrão para aquele tipo.

```python
from typing import Annotated

from selva.di import Inject, service


class Interface: pass


@service(name="A", provides=Interface)
class ServiceA: pass


@service(name="B", provides=Interface)
class ServiceB: pass


@service
class OtherService:
    dependency_a: Annotated[Interface, Inject("A")]
    dependency_b: Annotated[Interface, Inject("B")]
```

### Dependências opcionais

Se uma dependência requisitada não for registrada, um erro é lançado, a não ser
que haja um valor padrão declarado, onde a propriedade terá esse valor quando o
serviço for criado.

```python
from typing import Annotated

from selva.di import Inject, service


@service
class SomeService:
    pass


@service
class MyService:
    dependency: Annotated[SomeService, Inject] = None

    def some_method(self):
        if self.dependency:
            ...
```

## Serviços como funções geradoras

Para registrar um tipo que nós não temos controle, por exemplo, um tipo de uma biblioteca
externa, nós podemos uma uma função geradora:

```python
from selva.di import service
from some_library import SomeClass


@service
async def some_class_factory() -> SomeClass:
    return SomeClass()
```

A anotação de tipo de retorno é requirida em funções geradoras, já que esta será o
serviço provido pela função. Se a anotação de tipo de retorno não for provida, um
erro será lançado.

O valor do parâmetro `provides` em `@service` é ignorado quando estiver decorando
uma função geradora, e um _warning_ será lançado.

Parâmetros de funções geradoras não precisam da anotação `Inject`, a não ser que elas
precisem especificar uma dependência nomeada.

```python
from typing import Annotated

from selva.di import Inject, service
from some_library import SomeClass


@service
async def some_class_factory(
    dependency: MyService,
    other: Annotated[OtherService, Inject("service_name")]
) -> SomeClass:
    return SomeClass()
```

### Inicialização e finalização

Para executar inicialização em funções geradoras, você apenas executa a lógica antes
de retornar o serviço.

```python
from selva.di import service


class SomeClass:
    pass


@service
async def factory() -> SomeClass:
    some_service = SomeClass()
    # perform initialization login
    return some_service
```

Para executar finalização, você usa `yield` ao invés de `return` e executa a lógica
de finalização logo após

```python
from selva.di import service


class SomeClass:
    pass


@service
async def factory() -> SomeClass:
    some_service = SomeClass()
    # perform initialization logic
    yield some_service
    # perform finalization logic
```

### Serviços nomeados

Serviços nomeados funcionam da mesma forma que nas classes.

```python
from typing import Annotated

from selva.di import Inject, service

from some_library import SomeClass


@service(name="service_name")
def factory() -> SomeClass:
    return SomeClass


@service
class MyService:
    dependency: Annotated[SomeClass, Inject("service_name")]
```

### Dependências opcionais

Dependências opcionais funcionam da mesma forma que nas classes, onde você especifica
um valor padrão para o argumento.

```python
from typing import Annotated

from selva.di import Inject, service
from some_library import SomeClass


@service
async def some_class_factory(
    dependency: MyService,
    other: Annotated[OtherService, Inject("service_name")] = None
) -> SomeClass:
    if other:
        ...

    return SomeClass()
```
