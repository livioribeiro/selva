# Project Structure

In a Selva project, you need to define at least the `application`.

It can be a Python module or package and represents the main code of the project.
Any controllers or services defined under it will be discovered and registered
in the dependency injection context.

If your project is small, you can just define the `aplication.py` module, but you
can have any structure you need inside the `application` package.

For example:

```
project/
└── application/
    ├── __init__.py
    ├── controller/
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
