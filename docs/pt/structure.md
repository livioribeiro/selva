# Estrutura do projeto

Em um projeto Selva, você precisa definir pelo menos o `application`.

Pode ser um módulo ou um pacote Python e representa o código principal do projeto.
Quaisquer tratadores e serviços definidos sob ele serão descobertos e registrados.

Se o seu projeto é pequeno, você pode apenas definir o módulo `application.py`,
mas você pode ter qualquer estrutura que quiser dentro do pacote `application`.

Por exemplo:

```
# mínimo
project/
└── application.py

# com módulos
project/
└── application/
    ├── __init__.py
    ├── handler.py
    ├── model.py
    ├── repository.py
    └── service.py

# estrutura complexa
project/
└── application/
    ├── __init__.py
    ├── handler/
    │   ├── __init__.py
    │   ├── public/
    │   │   ├── __init__.py
    │   │   ├── about.py
    │   │   ├── home.py
    │   │   └── product.py
    │   └── private/
    │       ├── __init__.py
    │       ├── category.py
    │       ├── customer.py
    │       └── product.py
    ├── model/
    │   ├── __init__.py
    │   ├── category.py
    │   ├── customer.py
    │   └── product.py
    ├── repository/
    │   ├── __init__.py
    │   ├── category.py
    │   ├── customer.py
    │   └── product.py
    └── service/
        ├── __init__.py
        ├── category.py
        ├── customer.py
        ├── email.py
        └── product.py
```
