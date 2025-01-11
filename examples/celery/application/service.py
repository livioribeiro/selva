from selva.di import service


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
